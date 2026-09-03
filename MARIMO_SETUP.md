# Marimo pairing setup

Directions to reopen a fresh Claude Code session pre-connected to your molab
notebook sandbox, so you don't have to redo this investigation next time.

## Prerequisites

- `uvx` (already installed on this machine: `/Users/sreevidyaganga/.local/bin/uvx`)
- Your **current** molab sandbox URL (given to you by molab itself):
  `https://sb-ee195edd2eb6041f.sb.molab.run/`
  — sandbox URLs expire/terminate (the previous one,
  `sb-3c58c3831debc93a.sb.molab.run`, died mid-session on 2026-08-31 with
  `HTTP 410 sandbox terminated` after a few hours idle). Get a fresh one
  from molab whenever this stops working — `curl -s -o /dev/null -w
  "%{http_code}"  <url>` returning `410` means it's dead, not just slow.
- The auth token for that sandbox. Get it from wherever molab gave you the
  pairing URL. Type it directly into your terminal when prompted in Step 2 —
  don't paste it into a Claude chat message, since chat messages are stored
  in the conversation log and a terminal prompt isn't.
- **Run Steps 2 and 3 in a real terminal app (Terminal.app, iTerm, etc.),
  not through Claude Code's `!` passthrough.** `--with-token` uses a hidden
  password prompt (`getpass`); confirmed this session that the `!`
  passthrough has no real TTY, so the prompt fails with "Password input may
  be echoed" / "Aborted!" and never captures the token.

## Step 1 — install the marimo-pair Claude Code skill

Run in an interactive terminal:

```
npx skills add marimo-team/marimo-pair
```

If `npx` isn't available:

```
uvx deno -A npm:skills add marimo-team/marimo-pair
```

This installs a Claude Code skill (third-party code from the `marimo-team`
GitHub org: https://github.com/marimo-team/marimo-pair) that gives Claude
Code the ability to interact with a paired marimo notebook. Worth a quick
skim of that repo before installing, same as any new dependency.

## Step 2 — generate the pairing prompt

```
uvx marimo@latest pair prompt --url https://sb-ee195edd2eb6041f.sb.molab.run/ --with-token --claude
```

- `--claude` validates that the Step 1 skill is installed.
- `--with-token` interactively prompts `Auth token:` — enter the token from
  molab here, in your terminal.
- On success this prints a "prompt" string meant to be handed to Claude Code.

## Step 3 — start Claude Code paired to the notebook

```
claude "$(uvx marimo@latest pair prompt --url https://sb-ee195edd2eb6041f.sb.molab.run/ --with-token --claude)"
```

This launches a new Claude Code session with the generated prompt as its
starting context, connected to the marimo notebook.

**If Claude Code is already running** (this is the common case — you're
mid-session and the sandbox just died underneath you): don't run Step 3.
Just run Step 2 alone in a real terminal, then paste its printed output
(the "prompt" string — safe to share, it references a local token file
path rather than the raw token) back into the existing chat. Claude can
reconnect with `execute-code.sh --url <url> --token "$(cat <path from the
printed prompt>)"` without needing a whole new session.

## Notes from this session's investigation

- Confirmed via `marimo pair --help` / `marimo pair prompt --help` that this
  is documented, intended marimo functionality (a pair-programming prompt
  generator for Claude Code / Codex / opencode), not something improvised —
  the earlier caution in this session was because the command arrived
  unexplained, not because the feature itself is suspicious.
- Running `pair prompt --with-token --claude` once in this session (without
  the skill installed, without a token) failed cleanly with "Aborted!" and
  sent nothing — safe to have checked, nothing was exposed.
- Marimo pairing is a **dev-environment convenience only**. It does not
  change the fact that this project's actual fine-tuning and activation
  work needs a CUDA GPU, which this MacBook (Apple M1, 8GB RAM, no CUDA,
  `bitsandbytes` not installed) cannot provide. Provisioning cloud GPU
  access is still a separate, open item for Phase 2 regardless of whether
  you pair via marimo — **still not decided**: needs your RunPod/Vast.ai
  account + payment method, which Claude doesn't have access to.
- The first sandbox (`sb-3c58c3831debc93a`) died mid-session after several
  hours idle-ish use — `HTTP 410 sandbox terminated`. Not something either
  side did wrong, just the expected lifecycle molab warns about above.
  Current one: `sb-ee195edd2eb6041f`.
- Claude Code's `!` shell passthrough can't complete `--with-token` (no
  real TTY for the hidden prompt) — always run Step 2 in an actual
  terminal app, not through `!`.
- Phase 2 model choice was revised mid-session: **Qwen3-8B-Base**, not
  Gemma-2-9b-it. Qwen3-8B is fully ungated on Hugging Face (Apache 2.0, no
  login/license-click needed at all), unlike Gemma-2-9b-it or
  Llama-3.1-8B which both require accepting a gated license — and it has
  its own current SAE tooling (Qwen-Scope, published May 2026, nnsight /
  TransformerLens supported). Qwen-Scope's SAEs are trained on the base
  model, not an instruct variant, so the plan is to fine-tune
  Qwen3-8B-Base directly on the 340-example dataset as a single-stage SFT
  (serves as both instruction-tuning and persona-conditioning) rather than
  layering LoRA on an already-instruct-tuned checkpoint — keeps the probed
  model close to what the public SAEs were actually trained on.
