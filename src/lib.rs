use rustpython_parser::{lexer::lex, Mode, Tok};

/// Runs of standalone comments longer than `max_lines`, as (first, last) line (1-based).
pub fn find_long_comment_blocks(source: &str, max_lines: usize) -> Vec<(usize, usize)> {
    let mut violations = Vec::new();
    let mut run: Option<(usize, usize)> = None;

    // ponytail: O(n) line recount per comment -> O(n*m).
    // If this ever becomes the bottleneck: incremental counter or
    // ruff_source_file::LineIndex.
    for (tok, range) in lex(source, Mode::Module).flatten() {
        if !matches!(tok, Tok::Comment(_)) {
            continue;
        }
        let offset = usize::from(range.start());
        let line_start = source[..offset].rfind('\n').map_or(0, |i| i + 1);

        // standalone only: nothing but whitespace before the #
        if !source[line_start..offset].trim().is_empty() {
            continue;
        }
        let line = source[..line_start].matches('\n').count() + 1;

        run = match run {
            Some((s, p)) if line == p + 1 => Some((s, line)),
            Some((s, p)) => {
                if p - s + 1 > max_lines {
                    violations.push((s, p));
                }
                Some((line, line))
            }
            None => Some((line, line)),
        };
    }

    if let Some((s, p)) = run {
        if p - s + 1 > max_lines {
            violations.push((s, p));
        }
    }
    violations
}

#[cfg(test)]
mod tests {
    use super::find_long_comment_blocks;

    #[test]
    fn finds_only_long_standalone_runs() {
        let src = "# a\n# b\n# c\n# d\n# e\n# f\nx = 1  # trailing\ny = '# not a comment'\n\n# short\n# short\n";
        assert_eq!(find_long_comment_blocks(src, 5), vec![(1, 6)]);
    }

    #[test]
    fn a_run_exactly_at_the_limit_passes() {
        let src = "# a\n# b\n# c\n";
        assert!(find_long_comment_blocks(src, 3).is_empty());
        assert_eq!(find_long_comment_blocks(src, 2), vec![(1, 3)]);
    }

    #[test]
    fn blank_line_breaks_a_run() {
        let src = "# a\n# b\n\n# c\n# d\n";
        assert!(find_long_comment_blocks(src, 2).is_empty());
    }

    #[test]
    fn indented_comments_count_as_standalone() {
        let src = "def f():\n    # a\n    # b\n    # c\n    return 1\n";
        assert_eq!(find_long_comment_blocks(src, 2), vec![(2, 4)]);
    }

    #[test]
    fn trailing_comments_never_start_a_run() {
        let src = "a = 1  # one\nb = 2  # two\nc = 3  # three\n";
        assert!(find_long_comment_blocks(src, 1).is_empty());
    }

    #[test]
    fn reports_every_long_run() {
        let src = "# a\n# b\n# c\n\nx = 1\n\n# d\n# e\n# f\n";
        assert_eq!(find_long_comment_blocks(src, 2), vec![(1, 3), (7, 9)]);
    }

    #[test]
    fn hashes_inside_strings_are_not_comments() {
        let src = "s = '''\n# a\n# b\n# c\n'''\n";
        assert!(find_long_comment_blocks(src, 1).is_empty());
    }

    #[test]
    fn empty_source_is_clean() {
        assert!(find_long_comment_blocks("", 0).is_empty());
    }
}
