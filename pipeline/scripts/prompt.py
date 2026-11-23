"""Prompt builder for the repair pipeline.

build_prompt(breakage, context_items, examples, feedback=None) -> (system, user)
  breakage      : from context.breakage_from_log (symptoms only; a new case is not classified)
  context_items : from context.code_context  [(path, kind, text)]
  examples      : retrieved KB entries (full entries); [] for the no-RAG condition
  feedback      : on a retry, the harness result of the previous attempt (what still failed)
The system prompt is fixed (no per-case or time-dependent text) so it can be prompt-cached.
"""
import json

SYSTEM = """You repair Java projects whose tests broke after a dependency update changed the dependency's behavior.

You receive: the dependency update, the build/test failure, the relevant project source files, and (when
available) fixes of similar past breakages from a knowledge base.

Your task: produce ONE patch that makes the failing tests pass while keeping the dependency update.

Hard rules (patches that break them are rejected automatically):
1. Keep the updated dependency at the new version or higher. Do not revert, downgrade, exclude or remove it.
2. Do not delete, disable, skip or weaken tests (no @Ignore/@Disabled, no removed assertions or test methods).
   Updating an expected value is allowed only when the new library behavior is the intended behavior.
3. Every test that passed before the update must still pass.
4. You may change source code, test code, configuration files, or build files; you may add or upgrade a
   companion dependency (for example a provider that matches the new version) when that is the right fix.
5. Prefer the smallest change that addresses the actual behavior change.

Output format:
- First, at most a few sentences explaining the behavior change and your fix.
- Then exactly one fenced code block with language `diff` containing a unified diff (git format) against the
  files as shown, with paths relative to the repository root:
  ```diff
  diff --git a/path/File.java b/path/File.java
  --- a/path/File.java
  +++ b/path/File.java
  @@ -10,7 +10,7 @@
   context line
  -old line
  +new line
   context line
  ```
- Context lines must match the given files exactly. Do not output anything after the diff block."""


def _fmt_example(i, e, max_patch=6000):
    b, beh, fx = e["breakage"], e["behavior"], e["fix"]
    patch = fx["patch"] if len(fx["patch"]) <= max_patch else fx["patch"][:max_patch] + "\n... (patch truncated)"
    author = {"developer": "the project's developers", "derived from developer fix (Claude)": "derived from the developers' fix"}.get(
        fx["author"], "written by the researchers (validated, but not the project's own fix)")
    return "\n".join([
        f"### Past case {i}: {b['dependency']} {b['old_version']} -> {b['new_version']} ({e['project']})",
        f"Symptom: {'; '.join(b['exception_types'][:3]) or 'test failure'}",
        *(f"  {l[:240]}" for l in b["error_lines"][:2]),
        f"Behavior change: {beh['description']}",
        f"Fix ({fx['fix_type']}, {author}; validated: all tests pass): {fx['explanation'][:400]}",
        "```diff", patch.rstrip(), "```"])


def build_prompt(breakage, context_items, examples, feedback=None):
    b = breakage
    parts = [
        "## Dependency update",
        f"`{b['dependency']}` was updated from `{b['old_version']}` to `{b['new_version']}`. The project compiles, but tests now fail.",
        "", "## Failure (from the build log)",
        f"Failing test classes: {', '.join(b['failing_test_classes']) or '(not named in the log)'}",
        f"Exception types: {', '.join(b['exception_types']) or '(none)'}",
        "Error lines:", *(f"- {l}" for l in b["error_lines"]),
    ]
    if b["slf4j_console"]:
        parts += ["SLF4J console output:", *(f"- {l}" for l in b["slf4j_console"])]
    if b["project_frames"]:
        parts += ["Project stack frames:", *(f"- {f['cls']} ({f['file']}:{f['line']})" for f in b["project_frames"][:12])]
    if examples:
        parts += ["", "## Similar past breakages and their validated fixes (from the knowledge base)",
                  "They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.", ""]
        parts += [_fmt_example(i + 1, e) + "\n" for i, e in enumerate(examples)]
    parts += ["", "## Project files (at the breaking commit)"]
    for path, kind, text in context_items:
        parts += [f"### {path}  ({kind})", "```", text.rstrip(), "```", ""]
    if feedback:
        parts += ["## Your previous patch did not repair the case",
                  f"Checks failed: {', '.join(feedback['failed_checks']) or 'see below'}",
                  f"Build: {feedback['build']['status']}, tests {feedback['build']['tests']}, failures {feedback['build']['failures']}, errors {feedback['build']['errors']}"]
        if feedback.get("apply_error"):
            # Nothing ran, so test lists would only be noise: report why the patch did not apply.
            parts += ["The patch did not apply (git apply rejected it), so no test ran. git reported:", "```",
                      feedback["apply_error"][:3000], "```",
                      "Check that every context and '-' line matches the files shown above exactly, including whitespace."]
        else:
            still = {k: v for k, v in feedback.get("target_classes", {}).items() if v != "passed"}
            if still:
                parts.append("Originally failing tests still failing: " + "; ".join(f"{k}: {v}" for k, v in still.items()))
            if feedback.get("regressions"):
                parts.append("Tests that passed before the update and now fail: " + "; ".join(feedback["regressions"][:10]))
            if feedback.get("error_excerpt"):
                parts += ["Error excerpt from the new run:", "```", feedback["error_excerpt"][:4000], "```"]
        parts.append("Produce a corrected patch against the ORIGINAL files shown above (not on top of your previous patch).")
    parts += ["", "Now write the explanation and the single ```diff block."]
    return SYSTEM, "\n".join(parts)
