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

