# Benchmarks

`find_long_comment_blocks` is everything commentwall does between reading a
file and printing a diagnostic, so it is the only thing measured here. The
harness is [Criterion](https://bheisler.github.io/criterion.rs/book/).

```bash
cargo bench
```

## Fixtures

Real Python, not generated noise, and byte-pinned: `.gitattributes` marks
`benches/fixtures/**` as `-text` so no checkout rewrites a line ending and
shifts the per-byte numbers.

| Fixture | Bytes | Lines | Comment runs | Blocks at `--max-lines 5` | Stresses |
| --- | ---: | ---: | ---: | ---: | --- |
| `small.py` | 1 312 | 42 | 1 | 0 | The common case: a small module a commit hook sees hundreds of times a day |
| `many_comments.py` | 7 587 | 231 | 26 | 0 | Run bookkeeping — many short runs opened, extended and closed, none reportable |
| `long_comments.py` | 8 213 | 214 | 6 | 6 | Agent narration: a few very long walls, every one of them collected |
| `pathological.py` | 25 390 | 212 | 12 | 4 | Adversarial lexing (below) |

`pathological.py` is built to be expensive per byte and cheap in findings:

- 120 hash-prefixed lines inside one string literal — a wall that is not a wall
- twelve lines of 200 numeric literals each, every one closed by a trailing
  comment that has to be located and then discarded
- nested f-strings with hashes in the replacement fields
- a stray `)` and mixed tab/space indentation, both recoverable lexical errors
  followed by real walls
- non-ASCII identifiers, string content and comments, so byte offsets and
  character columns diverge
- a CRLF section in the middle of an otherwise LF file
- an unclosed `max(` on the last line, which makes the lexer repeat its EOF
  error for as long as it is polled

The last two make the file a correctness trap as much as a speed one: a scan
that bails early still produces a benchmark number, just not for the input it
claims to measure. [`tests/bench_fixtures.rs`](../tests/bench_fixtures.rs)
pins the exact blocks each fixture yields and asserts the final run — the one
immediately before that unclosed bracket — is still found, so `cargo test`
fails if a fixture ever stops being scanned end to end.

## Groups

| Group | Question |
| --- | --- |
| `fixtures` | How fast is each shape of input, in bytes per second? |
| `max_lines` | Does the threshold change the cost? (0, 5, unlimited → 12, 4, 0 blocks on the same file) |
| `scaling` | Is the scan linear in file size? (`long_comments.py` at 1×, 4×, 16×) |

Every group reports throughput, so numbers are comparable across fixtures of
different sizes.

## Reference numbers

Xeon Gold 6142 @ 2.60 GHz, 4 cores, Linux, rustc 1.98.1, criterion 0.8.2,
release profile (`lto = true`, `codegen-units = 1`), mean of 100 samples.
Absolute values move with the machine; the ratios do not.

| Benchmark | Mean | Throughput |
| --- | ---: | ---: |
| `fixtures/small` | 33.3 µs | 37.6 MiB/s |
| `fixtures/many_comments` | 177.6 µs | 40.7 MiB/s |
| `fixtures/long_comments` | 148.4 µs | 52.8 MiB/s |
| `fixtures/pathological` | 721.9 µs | 33.5 MiB/s |
| `max_lines/0` (12 blocks) | 623.2 µs | 38.9 MiB/s |
| `max_lines/5` (4 blocks) | 630.5 µs | 38.4 MiB/s |
| `max_lines/unlimited` (0 blocks) | 632.9 µs | 38.3 MiB/s |
| `scaling/1x` (8 KiB) | 146.6 µs | 53.4 MiB/s |
| `scaling/4x` (32 KiB) | 599.5 µs | 52.3 MiB/s |
| `scaling/16x` (128 KiB) | 2.290 ms | 54.7 MiB/s |

Three things fall out of that:

- **Throughput is set by the lexer, not by the comments.** The spread across
  fixtures is 34–53 MiB/s, and the slow end is `pathological.py`, whose 200
  numeric literals per line cost far more per byte than a comment does.
- **`--max-lines` is free.** Reporting 12 blocks, 4 blocks and none differ by
  under 2% on the same file — less than the run-to-run noise, and the ordering
  is even backwards.
- **The scan is linear.** 17.9, 18.3 and 17.4 ns/byte across a 16× size range.

## Where the time actually goes

Criterion measures the scan alone. End to end, a `commentwall` process on the
same machine costs about 1.8 ms, and roughly 1.5 ms of that is the `fork`/
`exec` any process pays — `/bin/true` measures the same in the same loop.

| Command, mean of 200 runs | Wall time |
| --- | ---: |
| `/bin/true` | 1.483 ms |
| `commentwall --help` (starts, scans nothing) | 1.778 ms |
| `commentwall small.py` | 1.811 ms |
| `commentwall pathological.py` | 2.916 ms |

The 33 µs between `--help` and `small.py` is the scan, and it matches
`fixtures/small` above. On files of that size commentwall's own work is around
2% of the invocation; the rest is process start. Making the scan faster would
not move a commit hook.

## Comparing runs

Criterion diffs against the previous run automatically. To pin an explicit
point of reference:

```bash
cargo bench -- --save-baseline main
```

```bash
cargo bench -- --baseline main
```

Filters take a regex over `group/benchmark`:

```bash
cargo bench -- fixtures/pathological
```

CI runs `cargo bench --bench comment_blocks -- --test`, which executes each
benchmark once without measuring. That catches a broken bench or a fixture
that no longer parses; it says nothing about speed, since shared runners are
too noisy to gate on.
