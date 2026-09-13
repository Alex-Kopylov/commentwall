//! The benchmarks are only meaningful if the scanner walks each fixture from
//! end to end. `pathological.py` in particular is built out of lexical errors
//! and an unclosed bracket, any of which could silently cut a scan short: the
//! benchmark would still produce a number, just not for the input it claims.

use commentwall::find_long_comment_blocks;

struct Fixture {
    name: &'static str,
    source: &'static str,
    /// Blocks reported at the CLI default of five.
    blocks: &'static [(usize, usize)],
    /// Every standalone run, however short, at `--max-lines 0`.
    runs: usize,
    /// The last of those runs. It sits at the end of the file, so finding it
    /// proves the scan reached there.
    last_run: (usize, usize),
}

const FIXTURES: [Fixture; 4] = [
    Fixture {
        name: "small.py",
        source: include_str!("../benches/fixtures/small.py"),
        blocks: &[],
        runs: 1,
        last_run: (38, 40),
    },
    Fixture {
        name: "many_comments.py",
        source: include_str!("../benches/fixtures/many_comments.py"),
        blocks: &[],
        runs: 26,
        last_run: (228, 228),
    },
    Fixture {
        name: "long_comments.py",
        source: include_str!("../benches/fixtures/long_comments.py"),
        blocks: &[
            (17, 36),
            (56, 73),
            (86, 100),
            (124, 137),
            (158, 172),
            (198, 206),
        ],
        runs: 6,
        last_run: (198, 206),
    },
    Fixture {
        name: "pathological.py",
        source: include_str!("../benches/fixtures/pathological.py"),
        blocks: &[(161, 168), (175, 182), (186, 193), (199, 206)],
        runs: 12,
        last_run: (209, 211),
    },
];

#[test]
fn fixtures_are_scanned_end_to_end() {
    for fixture in &FIXTURES {
        let Fixture {
            name,
            source,
            blocks,
            runs,
            last_run,
        } = fixture;

        assert_eq!(&find_long_comment_blocks(source, 5), blocks, "{name}");

        let all = find_long_comment_blocks(source, 0);
        assert_eq!(all.len(), *runs, "{name}: {all:?}");
        assert_eq!(all.last(), Some(last_run), "{name}");
    }
}
