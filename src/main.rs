use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;
use commentwall::find_long_comment_blocks;

/// Fail Python files that contain walls of standalone comments.
#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Longest run of consecutive standalone comment lines that is accepted [default: 5, or 0 with --remove]
    #[arg(long, value_name = "N", default_value_if("remove", "true", "0"))]
    max_lines: Option<usize>,

    /// Hand the report to the format-comments skill (for hooks run under a coding agent)
    #[arg(long)]
    format: bool,

    /// Hand the report to the no-comments skill (for hooks run under a coding agent)
    #[arg(long, conflicts_with = "format")]
    remove: bool,

    /// Python files to check
    #[arg(value_name = "FILE", required = true)]
    files: Vec<PathBuf>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let max_lines = cli.max_lines.unwrap_or(5);
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

        for (first, last) in find_long_comment_blocks(&source, max_lines) {
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
                max_lines,
            );
            failed = true;
            has_violations = true;
        }
    }

    if has_violations {
        let skill = match (cli.format, cli.remove) {
            (true, _) => Some("format-comments"),
            (_, true) => Some("no-comments"),
            _ => None,
        };
        if let Some(skill) = skill {
            println!(
                "\nRun the `{skill}` skill with the report above as its scope. The flagged\n\
blocks are the whole scope. Leave every other comment alone."
            );
        }
    }

    if failed {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
