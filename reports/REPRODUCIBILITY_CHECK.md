# Reproducibility Check

This check reconstructs the consolidated workload-scaling summary from saved aggregate CSVs.
It checks request counts against saved request-level trial files.
No model inference or benchmark requests are executed by this check.

- Raw trial CSV files found: 18
- Workload configurations checked: 6
- Request-count checks passed: 6/6

## Configuration checks

|   max_tokens |   concurrency |   trial_files |   raw_requests |   aggregate_requests | match   |
|-------------:|--------------:|--------------:|---------------:|---------------------:|:--------|
|           16 |             1 |             3 |             15 |                   15 | True    |
|           16 |             2 |             3 |             15 |                   15 | True    |
|           32 |             1 |             3 |             15 |                   15 | True    |
|           32 |             2 |             3 |             15 |                   15 | True    |
|           64 |             1 |             3 |             15 |                   15 | True    |
|           64 |             2 |             3 |             15 |                   15 | True    |
