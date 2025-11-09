"""
Analyze match sync logs to identify patterns in save failures
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

def analyze_log_file(log_file: Path):
    """Analyze a single log file"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {log_file.name}")
    print(f"{'='*80}\n")
    
    events = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                events.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    if not events:
        print("No events found in log file")
        return
    
    # Count event types
    event_counts = Counter(e['event'] for e in events)
    print("Event Summary:")
    for event_type, count in event_counts.most_common():
        print(f"  {event_type}: {count}")
    
    # Analyze save attempts vs successes
    attempts = [e for e in events if e['event'] == 'save_attempt']
    successes = [e for e in events if e['event'] == 'save_success']
    failures = [e for e in events if e['event'] == 'save_failure']
    verif_failures = [e for e in events if e['event'] == 'verification_failure']
    
    print(f"\nSave Statistics:")
    print(f"  Total attempts: {len(attempts)}")
    print(f"  Successful saves: {len(successes)}")
    print(f"  Failed saves: {len(failures)}")
    print(f"  Verification failures: {len(verif_failures)}")
    
    if attempts:
        success_rate = (len(successes) / len(attempts)) * 100
        print(f"  Success rate: {success_rate:.1f}%")
    
    # Analyze failure reasons
    if failures:
        print(f"\nFailure Reasons:")
        failure_reasons = Counter(f['reason'] for f in failures)
        for reason, count in failure_reasons.most_common():
            print(f"  {reason}: {count}")
            # Show sample errors for each reason
            samples = [f for f in failures if f['reason'] == reason and f.get('error')][:3]
            for sample in samples:
                print(f"    - {sample.get('error', 'N/A')[:100]}")
    
    # Analyze verification failures
    if verif_failures:
        print(f"\nVerification Failures:")
        print(f"  Matches that saved but couldn't be verified:")
        for vf in verif_failures[:10]:  # Show first 10
            print(f"    - {vf['match_id']}")
    
    # Analyze batch summaries
    batch_summaries = [e for e in events if e['event'] == 'batch_summary']
    if batch_summaries:
        print(f"\nBatch Summaries:")
        for batch in batch_summaries:
            print(f"  Attempted: {batch['total_attempted']}, "
                  f"Saved: {batch['total_saved']}, "
                  f"Failed: {batch['total_failed']}, "
                  f"Success Rate: {batch['success_rate']}")
    
    # Find matches that were attempted but never succeeded
    attempted_matches = {e['match_id'] for e in attempts}
    successful_matches = {e['match_id'] for e in successes}
    failed_matches = attempted_matches - successful_matches
    
    if failed_matches:
        print(f"\nMatches that failed to save ({len(failed_matches)} total):")
        for match_id in list(failed_matches)[:20]:  # Show first 20
            print(f"  - {match_id}")

def main():
    """Main analysis function"""
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        print(f"Logs directory not found: {logs_dir}")
        return
    
    # Find all match sync log files
    log_files = sorted(logs_dir.glob("match_sync_*.jsonl"))
    
    if not log_files:
        print("No match sync log files found")
        return
    
    print(f"Found {len(log_files)} log file(s)")
    
    # Analyze each log file
    for log_file in log_files:
        analyze_log_file(log_file)
    
    # Combined analysis if multiple files
    if len(log_files) > 1:
        print(f"\n{'='*80}")
        print("COMBINED ANALYSIS")
        print(f"{'='*80}\n")
        
        all_events = []
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        all_events.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        
        total_attempts = len([e for e in all_events if e['event'] == 'save_attempt'])
        total_successes = len([e for e in all_events if e['event'] == 'save_success'])
        total_failures = len([e for e in all_events if e['event'] == 'save_failure'])
        
        print(f"Total across all sessions:")
        print(f"  Attempts: {total_attempts}")
        print(f"  Successes: {total_successes}")
        print(f"  Failures: {total_failures}")
        if total_attempts:
            print(f"  Overall success rate: {(total_successes/total_attempts)*100:.1f}%")

if __name__ == "__main__":
    main()
