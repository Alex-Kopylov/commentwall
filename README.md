# commentwall

Fails Python files that contain walls of standalone comments.

A *wall* is a run of consecutive comment-only lines. Trailing comments
(`x = 1  # note`) never count, and a `#` inside a string is not a comment —
the file is tokenized with the RustPython lexer rather than pattern-matched.

```console
$ commentwall --max-lines 5 src/app.py
src/app.py:12: standalone comment block of 9 lines exceeds max-lines 5
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
"ubi:Alex-Kopylov/commentwall" = "0.1.0"
```

Or grab an archive for your platform from
[Releases](https://github.com/Alex-Kopylov/commentwall/releases).

## Usage

```
commentwall [--max-lines N] <FILE>...
```

| Option | Default | Meaning |
| --- | --- | --- |
| `--max-lines N` | `5` | Longest accepted run of consecutive comment-only lines |

Files are checked independently; every violating block is reported.

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
