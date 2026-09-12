# commentwall

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
"ubi:Alex-Kopylov/commentwall" = "0.2.0"
```

Or grab an archive for your platform from
[Releases](https://github.com/Alex-Kopylov/commentwall/releases).

## Usage

```
commentwall [--max-lines N] [--show-guidance] <FILE>...
commentwall --help
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--max-lines N` | `5` | Longest accepted run of consecutive comment-only lines |
| `--show-guidance` | off | Print comment-writing guidance once after all diagnostics, only if violations occur |
| `-h`, `--help` | | Print help and exit; no files required |

Files are checked independently; every violating block is reported.

Diagnostics follow [Ruff's concise format](https://docs.astral.sh/ruff/settings/#output-prefer-rule-codes):
`file:line:column: CODE message`. `CW001` identifies a comment block above the
limit. Lines and columns are 1-based and point to the first `#` in the block.
The message format is maintained in [`src/output.rs`](src/output.rs).

For agent feedback, run `commentwall --show-guidance src/app.py src/other.py`.
The exact guidance lives in [`prompts/comment-guidance.md`](prompts/comment-guidance.md)
and is embedded at compile time; rebuild after editing it. It appears once per
invocation, even with multiple files or blocks. Clean runs and file-read errors
alone do not print guidance.

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

## License

MIT
