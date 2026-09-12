use rustpython_parser::lexer::{lex, LexicalErrorType};
use rustpython_parser::{Mode, Tok};

/// Runs of standalone comments longer than `max_lines`, as (first, last) line (1-based).
///
/// Recoverable lexical errors are skipped, because the lexer resyncs after them and
/// comment walls further down the file still deserve reporting. An `Eof` error is
/// fatal instead: on an unclosed bracket the lexer repeats it forever rather than
/// ending the iterator, so skipping it would spin.
pub fn find_long_comment_blocks(source: &str, max_lines: usize) -> Vec<(usize, usize)> {
    let mut violations = Vec::new();
    let mut run: Option<(usize, usize)> = None;
    let (mut cursor, mut line, mut line_start) = (0usize, 1usize, 0usize);

    for item in lex(source, Mode::Module) {
        let (tok, range) = match item {
            Ok(pair) => pair,
            Err(err) if matches!(err.error, LexicalErrorType::Eof) => break,
            Err(_) => continue,
        };
        if !matches!(tok, Tok::Comment(_)) {
            continue;
        }
        let offset = usize::from(range.start());

        // Comments arrive in source order, so the line counter only moves forward.
        for (i, byte) in source.as_bytes()[cursor..offset].iter().enumerate() {
            if *byte == b'\n' {
                line += 1;
                line_start = cursor + i + 1;
            }
        }
        cursor = offset;

        // standalone only: nothing but whitespace before the #
        if !source[line_start..offset].trim().is_empty() {
            continue;
        }

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

    #[test]
    fn an_unclosed_bracket_at_eof_terminates() {
        assert!(find_long_comment_blocks("x = (", 0).is_empty());
        assert_eq!(find_long_comment_blocks("# a\n# b\nf(\n", 1), vec![(1, 2)]);
    }

    #[test]
    fn a_recoverable_lex_error_does_not_hide_later_runs() {
        assert_eq!(
            find_long_comment_blocks("x = 1)\n# a\n# b\n# c\n", 2),
            vec![(2, 4)]
        );
        assert_eq!(
            find_long_comment_blocks("if True:\n\t # a\n \t# b\n \t# c\n\tpass\n", 2),
            vec![(2, 4)]
        );
    }

    #[test]
    fn a_run_ending_at_eof_is_reported() {
        assert_eq!(find_long_comment_blocks("x = 1\n# a\n# b", 1), vec![(2, 3)]);
    }

    #[test]
    fn multibyte_text_does_not_shift_line_numbers() {
        let src = "s = \"аргумент\"  # хвост\n# раз\n# два\n# три\n";
        assert_eq!(find_long_comment_blocks(src, 2), vec![(2, 4)]);
    }

    #[test]
    fn crlf_line_endings_are_counted_once() {
        let src = "# a\r\n# b\r\n# c\r\n";
        assert_eq!(find_long_comment_blocks(src, 2), vec![(1, 3)]);
    }

    #[test]
    fn a_hash_inside_an_fstring_is_not_a_comment() {
        let src = "x = 1\ns = f'{x}#{x}'\nt = f'# nope'\n";
        assert!(find_long_comment_blocks(src, 0).is_empty());
    }

    #[test]
    fn max_lines_zero_reports_every_run() {
        assert_eq!(
            find_long_comment_blocks("# a\nx = 1\n# b\n", 0),
            vec![(1, 1), (3, 3)]
        );
    }
}
