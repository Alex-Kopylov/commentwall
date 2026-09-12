use commentwall::find_long_comment_blocks;

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
fn comments_before_an_unterminated_triple_string_are_reported() {
    assert_eq!(
        find_long_comment_blocks("# a\n# b\n\"\"\"unfinished", 1),
        vec![(1, 2)]
    );
    assert_eq!(
        find_long_comment_blocks("x = 1\n# a\n# b\n\"\"\"unfinished", 1),
        vec![(2, 3)]
    );
}

#[test]
fn comments_before_a_final_line_continuation_are_reported() {
    assert_eq!(find_long_comment_blocks("# a\n# b\n\\\n", 1), vec![(1, 2)]);
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
