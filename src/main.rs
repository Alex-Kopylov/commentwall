use std::path::PathBuf;
use std::process::ExitCode;
use std::sync::mpsc::{self, RecvTimeoutError};
use std::time::{Duration, Instant};

use clap::Parser;
use commentwall::find_long_comment_blocks;

mod output;

/// Fail Python files that contain walls of standalone comments.
#[derive(Parser)]
#[command(version, about, long_about = None)]
struct Cli {
    /// Longest run of consecutive standalone comment lines that is accepted
    #[arg(long, default_value_t = 5, value_name = "N")]
    max_lines: usize,

    /// Maximum seconds per file, including reading; 0 waits indefinitely
    #[arg(long, default_value_t = 5, value_name = "SECONDS")]
    file_timeout: u64,

    /// Print comment-writing guidance once if any comment blocks exceed the limit
    #[arg(short = 'p', long = "with-prompt")]
    with_prompt: bool,

    /// Python files to check in parallel; print one report after all checks finish or time out
    #[arg(value_name = "FILE", required = true)]
    files: Vec<PathBuf>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    let mut failed = false;
    let mut has_violations = false;
    let mut has_errors = false;
    let mut report = String::new();

    // Start every file before waiting, so one slow file cannot serialize the checks.
    let jobs: Vec<_> = cli
        .files
        .iter()
        .map(|path| {
            let (sender, receiver) = mpsc::channel();
            let path = path.clone();
            let max_lines = cli.max_lines;
            let started = Instant::now();
            let worker = std::thread::Builder::new().spawn(move || {
                let result = std::fs::read_to_string(&path).map(|source| {
                    find_long_comment_blocks(&source, max_lines)
                        .into_iter()
                        .map(|(first, last)| {
                            output::diagnostic(&path, &source, first, last, max_lines) + "\n"
                        })
                        .collect::<String>()
                });
                // A timed-out receiver is gone; this CLI exits without joining stalled workers.
                let _ = sender.send((started.elapsed(), result));
            });
            (started, receiver, worker)
        })
        .collect();

    let timeout = Duration::from_secs(cli.file_timeout);
    for (path, (started, receiver, worker)) in cli.files.iter().zip(jobs) {
        let result = match worker {
            Err(err) => Err(format!("cannot start analysis: {err}")),
            Ok(_worker) => {
                let received = if timeout.is_zero() {
                    receiver.recv().map_err(|_| RecvTimeoutError::Disconnected)
                } else {
                    receiver.recv_timeout(timeout.saturating_sub(started.elapsed()))
                };
                match received {
                    Ok((elapsed, _)) if !timeout.is_zero() && elapsed > timeout => Err(format!(
                        "analysis timed out after {} seconds",
                        cli.file_timeout
                    )),
                    Ok((_, result)) => result.map_err(|err| err.to_string()),
                    Err(RecvTimeoutError::Timeout) => Err(format!(
                        "analysis timed out after {} seconds",
                        cli.file_timeout
                    )),
                    Err(RecvTimeoutError::Disconnected) => Err("analysis worker failed".to_owned()),
                }
            }
        };
        match result {
            Ok(diagnostics) => {
                has_violations |= !diagnostics.is_empty();
                failed |= !diagnostics.is_empty();
                report.push_str(&diagnostics);
            }
            Err(err) => {
                report.push_str(&format!("{}: {err}\n", path.display()));
                has_errors = true;
                failed = true;
            }
        }
    }

    if cli.with_prompt && has_violations {
        report.push('\n');
        report.push_str(output::COMMENT_GUIDANCE);
    }

    if has_errors {
        eprint!("{report}");
    } else {
        print!("{report}");
    }

    if failed {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
