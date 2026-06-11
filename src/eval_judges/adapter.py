"""MLX model adapter — shared interface for Qwen and Phi judge models."""
from mlx_lm import load, generate

_cache = {}

def get_model(model_id: str):
    if model_id not in _cache:
        model, tokenizer = load(model_id)
        _cache[model_id] = (model, tokenizer)
    return _cache[model_id]


def run_inference(model_id: str, prompt: str, max_tokens: int = 512) -> str:
    model, tokenizer = get_model(model_id)

    # Both Qwen3 and Phi-4 support the chat template via apply_chat_template
    messages = [{"role": "user", "content": prompt}]
    if hasattr(tokenizer, "apply_chat_template"):
        # enable_thinking=False disables Qwen3's chain-of-thought reasoning mode,
        # cutting inference time from ~40s to ~2s per call for short JSON outputs.
        try:
            formatted = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            # Phi-4 and other models don't support enable_thinking
            formatted = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    else:
        formatted = prompt

    response = generate(model, tokenizer, prompt=formatted, max_tokens=max_tokens, verbose=False)
    return response.strip()
