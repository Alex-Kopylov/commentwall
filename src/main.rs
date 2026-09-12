use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;
use commentwall::find_long_comment_blocks;

/// Fail Python files that contain walls of standalone comments.
#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Longest run of consecutive standalone comment lines that is accepted
    #[arg(long, default_value_t = 5, value_name = "N")]
    max_lines: usize,

    /// Python files to check
    #[arg(value_name = "FILE", required = true)]
    files: Vec<PathBuf>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let mut failed = false;

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
            println!(
                "{}:{}: standalone comment block of {} lines exceeds max-lines {}",
                path.display(),
                first,
                last - first + 1,
                cli.max_lines
            );
            failed = true;
        }
    }

    if failed {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
