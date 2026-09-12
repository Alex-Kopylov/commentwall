use std::path::Path;

pub const COMMENT_GUIDANCE: &str = include_str!("../prompts/comment-guidance.md");

pub fn diagnostic(
    path: &Path,
    source: &str,
    first: usize,
    last: usize,
    max_lines: usize,
) -> String {
    let column = source
        .lines()
        .nth(first - 1)
        .unwrap_or_default()
        .chars()
        .take_while(|&ch| ch != '#')
        .count()
        + 1;
    format!(
        "{}:{first}:{column}: CW001 Standalone comment block of {} lines exceeds max-lines {max_lines}",
        path.display(),
        last - first + 1,
    )
}
