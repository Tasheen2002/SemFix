"""LLM providers that need no API key.

ManualProvider : writes the prompt to <run>/prompts/case<N>_attempt<k>.md and reads the model's answer from
                 <run>/responses/case<N>_attempt<k>.md if it exists (paste any LLM's answer there and rerun).
                 Lets the whole pipeline run with any chat model, by hand.
OracleProvider : PIPELINE TEST ONLY. Answers with the case's own frozen fix wrapped as an LLM reply, to prove that
                 patch extraction -> harness works end to end. Its results are never experiment results.
"""
import os


class ManualProvider:
    name = "manual"

    def __init__(self, run_dir):
        self.run_dir = run_dir
        os.makedirs(os.path.join(run_dir, "prompts"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "responses"), exist_ok=True)
        self.tag = None

    def complete(self, system, user):
        p = os.path.join(self.run_dir, "prompts", f"{self.tag}.md")
        open(p, "w", encoding="utf-8").write(f"<!-- SYSTEM PROMPT -->\n{system}\n\n<!-- USER PROMPT -->\n{user}\n")
        r = os.path.join(self.run_dir, "responses", f"{self.tag}.md")
        if not os.path.exists(r):
            return dict(text=None, awaiting=r, stop_reason="awaiting_manual_response", model_served="manual")
        return dict(text=open(r, encoding="utf-8").read(), stop_reason="end_turn", model_served="manual")


class OracleProvider:
    name = "oracle"

    def __init__(self, patch_text):
        self.patch_text = patch_text
        self.tag = None

    def complete(self, system, user):
        return dict(text="Oracle (pipeline test): returning the frozen fix.\n\n```diff\n" + self.patch_text.rstrip() + "\n```\n",
                    stop_reason="end_turn", model_served="oracle")


class OracleRetryProvider:
    """PIPELINE TEST ONLY. Attempt 1 answers with a broken patch (context lines that do not exist, so it cannot apply);
    later attempts answer with the frozen fix. Tests failure detection -> feedback in the next prompt -> retry."""
    name = "oracle_retry"

    def __init__(self, patch_text):
        self.patch_text = patch_text
        self.tag = None
        self.calls = 0
        self.prompts = []

    def complete(self, system, user):
        self.calls += 1
        self.prompts.append(user)
        if self.calls == 1:
            bad = "\n".join(("+" + l[1:] if l.startswith(" ") and i % 3 == 0 else l) if not l.startswith(("diff", "---", "+++", "@@")) else l
                            for i, l in enumerate(self.patch_text.splitlines()))
            bad = bad.replace("\n ", "\n THIS-LINE-DOES-NOT-EXIST ", 1)
            return dict(text="Pipeline test: deliberately broken patch.\n\n```diff\n" + bad + "\n```\n", stop_reason="end_turn", model_served="oracle_retry")
        return dict(text="Pipeline test: correct patch.\n\n```diff\n" + self.patch_text.rstrip() + "\n```\n", stop_reason="end_turn", model_served="oracle_retry")
