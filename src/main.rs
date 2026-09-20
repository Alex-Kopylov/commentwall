use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;
use commentwall::find_long_comment_blocks;

const COMMENT_GUIDANCE: &str = include_str!("../prompts/comment-guidance.md");

/// Fail Python files that contain walls of standalone comments.
#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Longest run of consecutive standalone comment lines that is accepted
    #[arg(long, default_value_t = 5, value_name = "N")]
    max_lines: usize,

    /// Print comment-writing guidance once if any comment blocks exceed the limit
    #[arg(short = 'p', long = "with-prompt")]
    with_prompt: bool,

    /// Python files to check
    #[arg(value_name = "FILE", required = true)]
    files: Vec<PathBuf>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let mut failed = false;
    let mut has_violations = false;

    for path in &cli.files {
        let source = match std::fs::read_to_string(path) {
            Ok(source) => source,
            Err(err) => {
                eprintln!("{}: {err}", path.display());
                failed = true;
                continue;
            }
        };

        for (first, last) in find_long_comment_blocks(&source, cli.max_lines) {
            let column = source
                .lines()
                .nth(first - 1)
                .unwrap_or_default()
                .chars()
                .take_while(|&ch| ch != '#')
                .count()
                + 1;
            println!(
                "{}:{first}:{column}: CW001 Standalone comment block of {} lines exceeds max-lines {}",
                path.display(),
                last - first + 1,
                cli.max_lines,
            );
            failed = true;
            has_violations = true;
        }
    }

    if cli.with_prompt && has_violations {
        print!("\n{COMMENT_GUIDANCE}");
    }

    if failed {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
