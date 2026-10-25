# LLM Inference Benchmark Lab

A reproducible benchmark harness for OpenAI-compatible chat-completion endpoints.

## Features

- Concurrent asynchronous HTTP requests
- Streaming and non-streaming requests
- Time to first streamed content (TTFT)
- Mean inter-chunk interval (ITL proxy; chunks are not guaranteed to equal tokens)
- Request latency percentiles and throughput
- Per-request CSV output and JSON summary
- Mock server for testing the benchmark harness

## Setup

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Run the mock server

```bash
python scripts/mock_server.py
```

It listens on port `8010`.

## Run a non-streaming benchmark

```bash
python -m src.benchmark.client \
  --url http://127.0.0.1:8010/v1/chat/completions \
  --model mock-model \
  --requests 10 \
  --concurrency 2 \
  --output results/raw/mock-nonstream.csv
```

## Run a streaming benchmark

```bash
python -m src.benchmark.client \
  --url http://127.0.0.1:8010/v1/chat/completions \
  --model mock-model \
  --requests 10 \
  --concurrency 2 \
  --stream \
  --output results/raw/mock-stream.csv
```

**Important:** mock-server results validate the benchmark software only. They are not real LLM performance measurements. Streaming ITL here measures intervals between received content chunks, not necessarily individual tokens. Real-model measurements must document the model, hardware, runtime, and configuration.

## Real-model CPU inference

The project includes a FastAPI server for running a real Hugging Face language model on CPU.

**Model:** `Qwen/Qwen2.5-0.5B-Instruct`

### Install inference dependencies

```bash
pip install transformers fastapi uvicorn
```

### Start the inference server

```bash
uvicorn scripts.cpu_model_server:app --host 127.0.0.1 --port 8000
```

The server exposes `GET /health` and `POST /v1/chat/completions`.

**Note:** Benchmark results depend on the runtime, input length, and concurrency. Treat the current CPU measurements as preliminary.

## Benchmark Results

This project evaluates local LLM inference performance across generation limits, concurrency levels, and streaming modes. Experiments use saved results; metrics are specific to the documented model and runtime environment.

- [Workload scaling report](reports/WORKLOAD_SCALING.md)
- [Cross-configuration analysis](reports/WORKLOAD_SCALING_ANALYSIS.md)
- [Summary CSV](reports/workload-scaling-summary.csv)
- [Latency chart](reports/workload-scaling-latency.png)
- [Request throughput chart](reports/workload-scaling-throughput.png)
- [Token throughput chart](reports/workload-scaling-token-throughput.png)
- [Validation results](reports/workload-scaling-validation.csv)
- [Metric consistency check](reports/workload-scaling-metric-check.csv)
- [Streaming comparison report](reports/STREAMING_COMPARISON.md)
- [Streaming comparison CSV](reports/streaming-comparison-summary.csv)
- [Streaming latency chart](reports/streaming-comparison-latency.png)

<!-- WORKLOAD-SCALING-RESULTS -->

<!-- RESULTS-TABLE-START -->
### Headline results (CPU, Qwen2.5-0.5B-Instruct)

| Max tokens | Concurrency | Req/s | Tokens/s | Mean latency (s) | P95 latency (s) |
|---|---|---|---|---|---|
| 16.0 | 1.0 | 0.197 | 3.156 | 5.382 | 7.856 |
| 16.0 | 2.0 | 0.252 | 4.028 | 7.071 | 8.298 |
| 32.0 | 1.0 | 0.12 | 3.828 | 8.361 | 9.339 |
| 32.0 | 2.0 | 0.141 | 4.515 | 12.673 | 14.005 |
| 64.0 | 1.0 | 0.061 | 3.922 | 16.329 | 17.867 |
| 64.0 | 2.0 | 0.071 | 4.515 | 25.42 | 28.832 |

<!-- RESULTS-TABLE-END -->

## Reproducibility and Validation

The following artifacts document checks performed on saved benchmark results. These checks do not rerun model inference.

- [Reproducibility check](reports/REPRODUCIBILITY_CHECK.md)
- [Reproducibility results CSV](reports/reproducibility-check.csv)
- [Workload scaling report](reports/WORKLOAD_SCALING.md)
- [Workload scaling summary](reports/workload-scaling-summary.csv)

<!-- REPRODUCIBILITY-REPORTS -->

<!-- LIMITATIONS -->
## Limitations and Environment

- **CPU-only:** all results were measured on a CPU-only runtime (Linux x86_64, Google Colab). No GPU or XPU results are included.
- **Single model:** results cover Qwen2.5-0.5B-Instruct only and do not generalize to larger models.
- **Small scale:** a limited number of trials per configuration, so treat differences between nearby configurations as indicative, not statistically conclusive.
- **Shared hardware:** Colab CPUs are shared and variable, so absolute numbers will differ on other machines.
- **Not directly comparable:** results are not directly comparable across different hardware, runtimes, prompt lengths, or generation limits.
- **Saved results only:** the reports are generated from saved raw data and do not rerun model inference.

## License

MIT. See [LICENSE](LICENSE).
