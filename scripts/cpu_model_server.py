
import json
import threading
import uuid

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
)

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
torch.set_num_threads(2)

print(f"Loading {MODEL_ID} on CPU...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    dtype=torch.float32,
    low_cpu_mem_usage=True,
)
model.eval()
print("Model loaded.", flush=True)

app = FastAPI(title="CPU LLM Inference Server")


def prepare_prompt(messages):
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )


def generation_inputs(messages, max_tokens):
    prompt = prepare_prompt(messages)
    inputs = tokenizer(prompt, return_tensors="pt")
    return prompt, inputs


@app.get("/health")
def health():
    return {"status": "healthy", "model": MODEL_ID, "device": "cpu"}


@app.post("/v1/chat/completions")
def chat(payload: dict):
    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(400, "messages must not be empty")

    max_tokens = min(max(int(payload.get("max_tokens", 64)), 1), 256)
    prompt, inputs = generation_inputs(messages, max_tokens)
    prompt_tokens = inputs["input_ids"].shape[1]
    completion_id = "chatcmpl-" + uuid.uuid4().hex[:12]

    if payload.get("stream", False):
        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=180,
        )
        kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        thread = threading.Thread(
            target=model.generate, kwargs=kwargs, daemon=True
        )

        def events():
            generated_text = ""
            thread.start()
            try:
                for chunk in streamer:
                    if not chunk:
                        continue
                    generated_text += chunk
                    event = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "model": MODEL_ID,
                        "choices": [{
                            "index": 0,
                            "delta": {"content": chunk},
                            "finish_reason": None,
                        }],
                    }
                    yield "data: " + json.dumps(event) + "\n\n"

                thread.join()
                completion_tokens = len(
                    tokenizer.encode(generated_text, add_special_tokens=False)
                )
                final_event = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "model": MODEL_ID,
                    "choices": [{
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }],
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    },
                }
                yield "data: " + json.dumps(final_event) + "\n\n"
                yield "data: [DONE]\n\n"
            finally:
                if thread.is_alive():
                    thread.join(timeout=5)

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[0, inputs["input_ids"].shape[1]:]
    answer = tokenizer.decode(new_tokens, skip_special_tokens=True)
    completion_tokens = len(new_tokens)

    return {
        "id": completion_id,
        "object": "chat.completion",
        "model": MODEL_ID,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }
