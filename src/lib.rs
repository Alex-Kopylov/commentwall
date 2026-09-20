use rustpython_parser::lexer::{lex, LexicalErrorType};
use rustpython_parser::{Mode, Tok};

/// Runs of standalone comments longer than `max_lines`, as (first, last) line (1-based).
///
/// Recoverable lexical errors are skipped, because the lexer resyncs after them and
/// comment walls further down the file still deserve reporting. The first `Eof`
/// is skipped to drain queued comments. A repeated `Eof` at the same location
/// stops iteration, since an unclosed bracket makes the lexer repeat it forever.
pub fn find_long_comment_blocks(source: &str, max_lines: usize) -> Vec<(usize, usize)> {
    let mut violations = Vec::new();
    let mut run: Option<(usize, usize)> = None;
    let (mut cursor, mut line) = (0usize, 1usize);
    let mut eof_location = None;

    for item in lex(source, Mode::Module) {
        let (tok, range) = match item {
            Ok(pair) => pair,
            Err(err) if matches!(err.error, LexicalErrorType::Eof) => {
                if eof_location == Some(err.location) {
                    break;
                }
                eof_location = Some(err.location);
                continue;
            }
            Err(_) => continue,
        };
        if !matches!(tok, Tok::Comment(_)) {
            continue;
        }
        let offset = usize::from(range.start());

        // Comments arrive in source order, so the line counter only moves forward.
        line += source[cursor..offset].matches('\n').count();
        cursor = offset;

        // standalone only: nothing but whitespace before the #
        let line_start = source[..offset].rfind('\n').map_or(0, |i| i + 1);
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
