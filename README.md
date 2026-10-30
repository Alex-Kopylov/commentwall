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
"ubi:Alex-Kopylov/commentwall" = "latest"
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
| `--no-comments` | off | Print a hand-off to the `/no-comments` skill once after all diagnostics, only if violations occur |
| `-h`, `--help` | | Print help and exit; no files required |

Diagnostics follow [Ruff's concise format](https://docs.astral.sh/ruff/settings/#output-prefer-rule-codes):
`file:line:column: CODE message`. `CW001` identifies a comment block above the
limit. Lines and columns are 1-based and point to the first `#` in the block.

The `--with-prompt` and `--no-comments` texts live in
[`prompts/`](prompts/) and are embedded at compile time; rebuild after editing them.

## With a coding agent

Four ways to use it, from cheapest to most thorough.

**Linter only.** The command above, in CI or a commit hook. Nothing touches
the code.

**AI formatter.** The agent runs `commentwall --with-prompt` on the files it
changed. The diagnostics come with
[`prompts/comment-guidance.md`](prompts/comment-guidance.md), and the agent
rewrites each flagged block in place.

**No-comments mode.** A port of the `/no-comments` skill from Cursor's
`pstack` plugin (MIT, see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)).
Copy [`.claude/agents/comment-sicko.md`](.claude/agents/comment-sicko.md) and
[`.claude/skills/no-comments/SKILL.md`](.claude/skills/no-comments/SKILL.md)
into your project's `.claude/` and run `/no-comments`. It spawns the Comment
Sicko agent over the current diff against `main`. Every comment dies unless it
is a license header, a public API doc, an issue link, or a quirk forced by
code we cannot change. Load-bearing prose becomes a `MUST KILL` flag on the
symbol, and the skill fixes the accepted flags.

**No-comments mode on the linter.** `commentwall --no-comments <FILE>...`.
The report is followed by a hand-off, and the agent runs `/no-comments` with
the whole report as its scope. Only the flagged blocks are touched.

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
