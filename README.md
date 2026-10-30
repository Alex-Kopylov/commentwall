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
commentwall [--max-lines N] [--format | --remove] <FILE>...
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--max-lines N` | `5`, or `0` with `--remove` | Longest accepted run of consecutive comment-only lines |
| `--format` | off | After the report, hand the flagged blocks to the `format-comments` skill |
| `--remove` | off | After the report, hand the flagged blocks to the `no-comments` skill |

Diagnostics follow [Ruff's concise format](https://docs.astral.sh/ruff/settings/#output-prefer-rule-codes):
`file:line:column: CODE message`. `CW001` identifies a comment block above the
limit. Lines and columns are 1-based and point to the first `#` in the block.

`--format` and `--remove` are for hooks that run under a coding agent. Run by
hand, they only append one sentence addressed to an agent.

## As a commit hook

With [prek](https://github.com/j178/prek) or pre-commit:

```yaml
repos:
  - repo: local
    hooks:
      - id: commentwall
        name: commentwall (comment blocks)
        entry: commentwall --format
        language: system
        types: [python]
```

Without a flag it is a plain linter: the commit fails, nothing touches the
code. For a hard ceiling on a pathological file: `entry: timeout 10 commentwall --format`.

## With a coding agent

The agent commits. On a violation the hook fails with the report and one
sentence:

```
src/app.py:12:1: CW001 Standalone comment block of 9 lines exceeds max-lines 5

Run the `format-comments` skill with the report above as its scope. The flagged
blocks are the whole scope. Leave every other comment alone.
```

The agent runs the named skill on those blocks and commits again. A clean
commit prints nothing. The sentence has no `/` or `$`, so one hook serves
Claude Code and Codex. If the agent ignores it, add to `CLAUDE.md` or
`AGENTS.md`: *when a commit hook fails with a commentwall report, run the
skill it names.*

Copy the skills into your project. Claude Code:

- [`.claude/skills/format-comments/SKILL.md`](.claude/skills/format-comments/SKILL.md)
- [`.claude/skills/no-comments/SKILL.md`](.claude/skills/no-comments/SKILL.md)
- [`.claude/agents/comment-sicko.md`](.claude/agents/comment-sicko.md)

Codex:

- [`.agents/skills/format-comments/SKILL.md`](.agents/skills/format-comments/SKILL.md)
- [`.agents/skills/no-comments/SKILL.md`](.agents/skills/no-comments/SKILL.md)
- [`.codex/agents/comment-sicko.toml`](.codex/agents/comment-sicko.toml)

**`--format`** → `format-comments`: each flagged block becomes the shortest
comment that states the non-obvious why, or is deleted if it only restates the
code. The BEFORE/AFTER at the top.

**`--remove`** → `no-comments`: a port of the `/no-comments` skill from
Cursor's `pstack` plugin (MIT, see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)). It spawns the Comment
Sicko agent. Every comment dies unless it is a license header, a public API
doc, an issue link, or a quirk forced by code we cannot change. Load-bearing
prose becomes a `MUST KILL` flag on the symbol, which the skill then fixes.
With `--remove` the limit defaults to `0`, so every standalone comment is
flagged.

Both skills also run on their own over files, a diff, or a pasted report;
with no argument they take the diff against `main`.

## License

MIT
