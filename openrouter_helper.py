import os
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import sqlite3
import argparse


SYSTEM_PROMPT = "You are a helpful assistant."
COMPARISON_SYSTEM_PROMPT = """You are an AI assistant specialized in comparing abilities. 
Provide a concise comparison of the two abilities, highlighting their similarities, 
differences, and potential interactions."""


def get_openrouter_response(model: str, user_prompt: str, system_prompt: str) -> str:
    """
    Gets a response from the OpenRouter API.

    Args:
        model: The name of the model to use.
        user_prompt: The user's prompt.
        system_prompt: The system's prompt.

    Returns:
        The response from the API.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        }
    )

    response.raise_for_status()  # Raise an exception for bad status codes

    return response.json()["choices"][0]["message"]["content"]

def process_csv_with_openrouter(csv_file_path: str, prompt_column: str, model_name: str, num_threads: int = 4):
    """
    Processes a CSV file, gets responses from OpenRouter API for a specific column,
    and saves the output to a new 'output' column in the same CSV.

    Args:
        csv_file_path: The path to the CSV file.
        prompt_column: The name of the column containing the user prompts.
        model_name: The name of the model to use.
        num_threads: The number of threads to use for parallel processing.
    """



    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return

    if prompt_column not in df.columns:
        print(f"Error: Column '{prompt_column}' not found in the CSV file.")
        return

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(get_openrouter_response, model_name, prompt, SYSTEM_PROMPT) for prompt in df[prompt_column]]
        results = [future.result() for future in futures]

    df['output'] = results
    df.to_csv(csv_file_path, index=False)
    print(f"Successfully processed {csv_file_path} and saved the output.")

def compare_abilities_pairwise(
    csv_file_path: str,
    ability_column_name: str,
    model_name: str,
    sqlite_db_path: str = "ability_comparisons.db",
    table_name: str = "comparisons",
    num_threads: int = 4
):
    """
    Performs pairwise comparisons between unique pairs of abilities in a specified CSV column
    using the OpenRouter API and saves the results to an SQLite database.

    Args:
        csv_file_path: The path to the CSV file containing ability descriptions.
        ability_column_name: The name of the column with ability descriptions.
        model_name: The name of the model to use for comparisons.
        sqlite_db_path: The path to the SQLite database file.
        table_name: The name of the table to store the comparisons.
        num_threads: The number of threads for parallel processing.
    """



    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return

    if ability_column_name not in df.columns:
        print(f"Error: Column '{ability_column_name}' not found in the CSV file.")
        return

    abilities = df[ability_column_name].tolist()
    comparison_tasks = []

    # Generate unique pairs (A, B)
    for ability1, ability2 in itertools.combinations(abilities, 2):
        user_prompt = f"Compare these two abilities:\nAbility 1: {ability1}\nAbility 2: {ability2}"
        comparison_tasks.append((ability1, ability2, user_prompt))

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            ability1_description TEXT NOT NULL,
            ability2_description TEXT NOT NULL,
            comparison_result TEXT,
            PRIMARY KEY (ability1_description, ability2_description)
        )
    """)
    conn.commit()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_abilities = {
            executor.submit(get_openrouter_response, model_name, task[2], COMPARISON_SYSTEM_PROMPT): (task[0], task[1])
            for task in comparison_tasks
        }

        for future in as_completed(future_to_abilities):
            ability1_desc, ability2_desc = future_to_abilities[future]
            try:
                comparison_result = future.result()
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {table_name} (ability1_description, ability2_description, comparison_result)
                    VALUES (?, ?, ?)
                """, (ability1_desc, ability2_desc, comparison_result))
                conn.commit()
            except Exception as exc:
                print(f"Ability pair ({ability1_desc}, {ability2_desc}) generated an exception: {exc}")
                # Store error message in DB
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {table_name} (ability1_description, ability2_description, comparison_result)
                    VALUES (?, ?, ?)
                """, (ability1_desc, ability2_desc, f"Error: {exc}"))
                conn.commit()
    
    conn.close()
    print(f"Successfully performed pairwise comparisons and saved results to SQLite database: {sqlite_db_path} in table {table_name}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OpenRouter API helper script")
    parser.add_argument('--model', default='mistralai/mistral-7b-instruct', help='Model name (default: mistralai/mistral-7b-instruct)')
    parser.add_argument('--user-prompt', help='User prompt for get_openrouter_response example')
    parser.add_argument('--csv', help='CSV file path for process_csv_with_openrouter')
    parser.add_argument('--prompt-column', default='prompt', help='Column name for prompts in CSV (default: prompt)')
    parser.add_argument('--ability-csv', help='CSV file path for compare_abilities_pairwise')
    parser.add_argument('--ability-column', default='Description', help='Column name for abilities in CSV (default: Description)')
    parser.add_argument('--sqlite-db', default='ability_comparisons.db', help='SQLite database path (default: ability_comparisons.db)')
    parser.add_argument('--table-name', default='comparisons', help='Table name for comparisons (default: comparisons)')
    parser.add_argument('--num-threads', type=int, default=4, help='Number of threads for parallel processing (default: 4)')
    args = parser.parse_args()

    # Example usage for get_openrouter_response (run if user-prompt is provided)
    if args.user_prompt:
        try:
            output = get_openrouter_response(args.model, args.user_prompt, SYSTEM_PROMPT)
            print("--- Example for get_openrouter_response ---")
            print(output)
        except (ValueError, requests.exceptions.RequestException) as e:
            print(f"An error occurred: {e}")

    # Example usage for process_csv_with_openrouter (run if csv is provided)
    if args.csv:
        print("\n--- Example for process_csv_with_openrouter ---")
        process_csv_with_openrouter(
            csv_file_path=args.csv,
            prompt_column=args.prompt_column,
            model_name=args.model,
            num_threads=args.num_threads
        )

    # Example usage for compare_abilities_pairwise (run if ability-csv is provided)
    if args.ability_csv:
        print("\n--- Example for compare_abilities_pairwise (SQLite) ---")
        compare_abilities_pairwise(
            csv_file_path=args.ability_csv,
            ability_column_name=args.ability_column,
            model_name=args.model,
            sqlite_db_path=args.sqlite_db,
            table_name=args.table_name,
            num_threads=args.num_threads
        )
