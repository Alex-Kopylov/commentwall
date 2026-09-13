//! Benchmarks for `find_long_comment_blocks`, which is all of commentwall's
//! work apart from reading the file and formatting diagnostics.

use std::hint::black_box;

use commentwall::find_long_comment_blocks;
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};

/// The CLI default, so `fixtures` measures what a commit hook actually runs.
const DEFAULT_MAX_LINES: usize = 5;

const LONG_COMMENTS: &str = include_str!("fixtures/long_comments.py");
const PATHOLOGICAL: &str = include_str!("fixtures/pathological.py");

const FIXTURES: [(&str, &str); 4] = [
    ("small", include_str!("fixtures/small.py")),
    ("many_comments", include_str!("fixtures/many_comments.py")),
    ("long_comments", LONG_COMMENTS),
    ("pathological", PATHOLOGICAL),
];

fn fixtures(c: &mut Criterion) {
    let mut group = c.benchmark_group("fixtures");
    for (name, source) in FIXTURES {
        group.throughput(Throughput::Bytes(source.len() as u64));
        group.bench_function(name, |b| {
            b.iter(|| find_long_comment_blocks(black_box(source), black_box(DEFAULT_MAX_LINES)));
        });
    }
    group.finish();
}

/// `max_lines` changes how many runs are collected, never how many are
/// scanned. On `pathological.py` the three points report 12, 4 and 0 blocks,
/// so the spread is the price of building the violation list.
fn max_lines(c: &mut Criterion) {
    let mut group = c.benchmark_group("max_lines");
    group.throughput(Throughput::Bytes(PATHOLOGICAL.len() as u64));
    for (label, limit) in [
        ("0", 0),
        ("5", DEFAULT_MAX_LINES),
        ("unlimited", usize::MAX),
    ] {
        group.bench_with_input(BenchmarkId::from_parameter(label), &limit, |b, &limit| {
            b.iter(|| find_long_comment_blocks(black_box(PATHOLOGICAL), black_box(limit)));
        });
    }
    group.finish();
}

/// Scanning should be linear in input size; this is the evidence for it.
fn scaling(c: &mut Criterion) {
    let mut group = c.benchmark_group("scaling");
    for repeats in [1usize, 4, 16] {
        let source = LONG_COMMENTS.repeat(repeats);
        group.throughput(Throughput::Bytes(source.len() as u64));
        group.bench_with_input(
            BenchmarkId::from_parameter(format!("{repeats}x")),
            &source,
            |b, source| {
                b.iter(|| {
                    find_long_comment_blocks(
                        black_box(source.as_str()),
                        black_box(DEFAULT_MAX_LINES),
                    )
                });
            },
        );
    }
    group.finish();
}

criterion_group!(benches, fixtures, max_lines, scaling);
criterion_main!(benches);
