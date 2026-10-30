# commentwall - deslopify your AI-generated code

<table>
<tr><th>BEFORE</th><th>AFTER</th></tr>
<tr>
<td>

```python
# Retry window correction — see
# NET-RETRY-017.
#
# The retry scheduler uses exponential
# backoff, which is mathematically
# correct but can cause many workers
# that failed at roughly the same time
# to retry together. In practice this
# creates short request spikes and can
# make an already overloaded service
# worse.
#
# Add a small random offset to each
# delay so retries are spread across
# the window instead of clustering
# around the same timestamps.
#
# Revisit this if the backoff strategy,
# worker count, timeout policy, or
# upstream rate limits change.
delay = base_delay * (2 ** attempt)
delay += random.uniform(0, delay * retry_jitter)
```

</td>
<td>

```python
# Avoids retry synchronization
# that would spike load.
delay = base_delay * (2 ** attempt)
delay += random.uniform(0, delay * retry_jitter)
```

</td>
</tr>
</table>

Fails Python files that contain walls of standalone comments.

A *wall* is a run of consecutive comment-only lines. Trailing comments
(`x = 1  # note`) never count, and a `#` inside a string is not a comment —
the file is tokenized with the RustPython lexer rather than pattern-matched.

```console
$ commentwall --max-lines 5 src/app.py
src/app.py:12:1: CW001 Standalone comment block of 9 lines exceeds max-lines 5
```

Exit code is `1` when anything is reported, `0` otherwise.

## Why

Coding agents narrate. Left unchecked they turn every function into a
paragraph of prose that restates the code below it and rots the moment the
code changes. This is the cheapest possible gate against that: one number,
enforced at commit time.

## Install

With [mise](https://mise.jdx.dev):

```toml
[tools]
"ubi:Alex-Kopylov/commentwall" = "1.0.0"
```

Or grab an archive for your platform from
[Releases](https://github.com/Alex-Kopylov/commentwall/releases).

## Usage

```
commentwall [--max-lines N] [--with-prompt] <FILE>...
commentwall --help
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--max-lines N` | `5` | Longest accepted run of consecutive comment-only lines |
| `-p`, `--with-prompt` | off | Print comment-writing guidance once after all diagnostics, only if violations occur |
| `-h`, `--help` | | Print help and exit; no files required |

Diagnostics follow [Ruff's concise format](https://docs.astral.sh/ruff/settings/#output-prefer-rule-codes):
`file:line:column: CODE message`. `CW001` identifies a comment block above the
limit. Lines and columns are 1-based and point to the first `#` in the block.

The `--with-prompt` text lives in [`prompts/comment-guidance.md`](prompts/comment-guidance.md)
and is embedded at compile time; rebuild after editing it.

## With a coding agent

Four ways to use it, from cheapest to most thorough.

**Linter only.** The command above, in CI or a commit hook. Nothing touches
the code; the agent sees the failure and deals with it.

**Light formatter.** Tell the agent to run `commentwall --with-prompt` on the
files it changed. The diagnostics come with
[`prompts/comment-guidance.md`](prompts/comment-guidance.md), and the agent
rewrites each flagged block in place. No subagent, no git archaeology.

**No-comments mode.** Copy [`.claude/agents/comment-sicko.md`](.claude/agents/comment-sicko.md)
and [`.claude/skills/no-comments/SKILL.md`](.claude/skills/no-comments/SKILL.md)
into your project's `.claude/` and run `/no-comments`. The skill spawns the
Comment Sicko agent over the current diff against `main`, working tree
included. Every comment in that diff dies unless it is a license header, a
public API doc comment, a link to an issue or RFC, or a quirk forced by code
we cannot change. Anything else that looks load-bearing gets a `MUST KILL`
flag on the guilty symbol instead of a comment. The skill then fixes the
accepted flags. One pass per invocation, not one per comment.

**No-comments mode on the linter.** `/no-comments lint`. Same agent, but the
skill runs `commentwall` first and hands it only the flagged blocks. Pass
files to narrow further: `/no-comments lint src/app.py`.

Both agent files are adapted from Cursor's `pstack` plugin, see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## As a commit hook

With [prek](https://github.com/j178/prek) or pre-commit:

```yaml
repos:
  - repo: local
    hooks:
      - id: commentwall
        name: commentwall (comment blocks)
        entry: commentwall --max-lines 5
        language: system
        types: [python]
```

For a hard ceiling on a pathological file, wrap the entry:
`entry: timeout 10 commentwall --max-lines 5`.

## License

MIT
