"""LLM provider: Claude via the official Anthropic Python SDK (`pip install anthropic`).

Credentials are resolved by the SDK from the environment (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an
`ant auth login` profile). No key is stored in this repository.

Defaults (change per experiment, record the values used):
  model   claude-opus-5-5 (the current default model; the researcher has not chosen the experiment model yet)
  effort  high (set explicitly: claude-opus-5-5 defaults to medium)
  thinking adaptive (always on for this model; depth is controlled by effort)
  fallbacks "default" (server-side refusal fallback, beta server-side-fallback-2026-07-01): if a safety classifier
          declines, the API re-runs the same request on a fallback model in the same call. The model that actually
          answered is recorded (response.model), so every result says which model produced the patch.
"""
import anthropic

DEFAULT_MODEL = "claude-opus-5-5"


class ClaudeProvider:
    name = "claude"

    def __init__(self, model=DEFAULT_MODEL, effort="high", max_tokens=16000, fallbacks=True):
        self.client = anthropic.Anthropic()
        self.model, self.effort, self.max_tokens, self.fallbacks = model, effort, max_tokens, fallbacks

    def complete(self, system, user):
        kwargs = dict(
            model=self.model, max_tokens=self.max_tokens,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],   # fixed system prompt: cacheable
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            messages=[{"role": "user", "content": user}],
        )
        if self.fallbacks:
            response = self.client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
        else:
            response = self.client.messages.create(**kwargs)
        text = "".join(b.text for b in response.content if b.type == "text")
        u = response.usage
        return dict(
            text=text, stop_reason=response.stop_reason,
            refusal=(dict(category=response.stop_details.category, explanation=response.stop_details.explanation)
                     if response.stop_reason == "refusal" and getattr(response, "stop_details", None) else None),
            model_requested=self.model, model_served=response.model, effort=self.effort,
            usage=dict(input_tokens=u.input_tokens, output_tokens=u.output_tokens,
                       cache_read_input_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
                       cache_creation_input_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0),
            request_id=getattr(response, "_request_id", None))
