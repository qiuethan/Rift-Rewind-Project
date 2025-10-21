# Rift Rewind Project Overview

This repository contains tools and data for the "Rift Rewind" project, an AI-powered agent designed to provide personalized insights for League of Legends players.

## File Summaries

*   `champion_abilities.csv`: Stores parsed champion ability data, including name, type, and description.
*   `champion.json`: Contains comprehensive metadata for all League of Legends champions.
*   `download_champion_data.py`: Script to download champion data from the League of Legends Data Dragon API.
*   `GEMINI.md`: The main project README, detailing the "Rift Rewind" project goals and requirements.
*   `Ideas.MD`: A planning document outlining project goals, user flow, tasks, and brainstorming ideas.
*   `league_abilities.html`: A saved HTML page from the League of Legends Fandom Wiki, containing raw ability data.
*   `openrouter_helper.py`: Provides utility functions for interacting with the OpenRouter API, including LLM calls and pairwise ability comparisons.
*   `parse_champion_data.py`: Parses champion data from individual JSON files and outputs it to `champion_abilities.csv`.
*   `schemas.MD`: Documents the JSON schemas for the Riot Games API timeline data.
*   `scrape_abilities_playwright.py`: Scrapes champion ability data from a Fandom wiki using Playwright and saves it to `champion_abilities.csv`.
*   `scrape_abilities.py`: Parses `league_abilities.html` to extract champion ability names and descriptions.
*   `test_prompts.csv`: Contains example prompts used for testing the OpenRouter API integration.
*   `champion_data/`: This directory contains individual JSON files, each holding detailed data for a specific League of Legends champion.
