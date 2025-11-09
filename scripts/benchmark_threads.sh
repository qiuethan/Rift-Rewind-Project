#!/bin/bash

# Hyperparameter sweep for compute_ability_similarity.py
# Tests different thread counts to find optimal performance
# Usage: ./benchmark_threads.sh

echo "=== Thread Count Benchmark for Ability Similarity ==="
echo "Testing with --limit-champions 5 (~25 abilities = ~300 pairs)"
echo ""

# Array of thread counts (powers of 2)
THREADS=(1 2 4 8 16 32)
# THREADS=(32 64 128)

# Output file for results
RESULTS_FILE="benchmark_results.txt"
echo "Thread Count Benchmark Results" > "$RESULTS_FILE"
echo "Date: $(date)" >> "$RESULTS_FILE"
echo "Script: compute_ability_similarity.py" >> "$RESULTS_FILE"
echo "Limit: 5 champions (~25 abilities = ~300 pairs)" >> "$RESULTS_FILE"
echo "================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Run benchmark for each thread count
for NUM_THREADS in "${THREADS[@]}"; do
    echo "Testing with $NUM_THREADS thread(s)..."
    echo "Thread Count: $NUM_THREADS" >> "$RESULTS_FILE"
    
    # Run the script and capture timing
    START_TIME=$(date +%s)
    # python3 scripts/compute_ability_similarity.py --limit 4 --num-threads "$NUM_THREADS" > /dev/null 2>&1
    python3 scripts/compute_ability_similarity.py --limit 3 --num-threads "$NUM_THREADS"
    END_TIME=$(date +%s)
    
    ELAPSED=$((END_TIME - START_TIME))
    echo "  Time: ${ELAPSED}s"
    echo "  Elapsed: ${ELAPSED} seconds" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    
    # Small delay between runs to avoid rate limiting
    sleep 2
done

echo ""
echo "=== Benchmark Complete ==="
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Summary:"
cat "$RESULTS_FILE" | grep -E "Thread Count:|Elapsed:"
