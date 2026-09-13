#![cfg(unix)]

use std::fs;
use std::path::PathBuf;
use std::process::{Child, Command, ExitStatus};
use std::thread::sleep;
use std::time::{Duration, Instant};

struct Run {
    dir: PathBuf,
    child: Child,
}

impl Run {
    fn start(name: &str, args: &[&str]) -> Self {
        let dir = std::env::temp_dir().join(format!("commentwall-{name}-{}", std::process::id()));
        fs::create_dir_all(&dir).unwrap();
        for file in ["slow.py", "other.py"] {
            assert!(Command::new("mkfifo")
                .arg(dir.join(file))
                .status()
                .unwrap()
                .success());
        }
        fs::write(dir.join("wall.py"), "# a\n# b\n").unwrap();
        let child = Command::new(env!("CARGO_BIN_EXE_commentwall"))
            .current_dir(&dir)
            .args(args)
            .stdout(fs::File::create(dir.join("stdout")).unwrap())
            .stderr(fs::File::create(dir.join("stderr")).unwrap())
            .spawn()
            .unwrap();
        Self { dir, child }
    }

    fn output(&self, stream: &str) -> String {
        fs::read_to_string(self.dir.join(stream)).unwrap()
    }

    fn assert_quiet_for(&mut self, duration: Duration) {
        let started = Instant::now();
        loop {
            assert!(self.child.try_wait().unwrap().is_none(), "CLI exited early");
            for stream in ["stdout", "stderr"] {
                assert!(self.output(stream).is_empty(), "early {stream} output");
            }
            if started.elapsed() >= duration {
                break;
            }
            sleep(Duration::from_millis(10));
        }
    }

    fn feed(&self, file: &str) {
        let mut writer = Command::new("sh")
            .args(["-c", "printf '# a\n# b\n' > \"$1\"", "sh"])
            .arg(self.dir.join(file))
            .spawn()
            .unwrap();
        assert!(wait(&mut writer, Duration::from_secs(2)).success());
    }
}

impl Drop for Run {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
        fs::remove_dir_all(&self.dir).unwrap();
    }
}

fn wait(child: &mut Child, limit: Duration) -> ExitStatus {
    let start = Instant::now();
    loop {
        if let Some(status) = child.try_wait().unwrap() {
            return status;
        }
        if start.elapsed() > limit {
            child.kill().unwrap();
            child.wait().unwrap();
            panic!("process did not finish within {limit:?}");
        }
        sleep(Duration::from_millis(10));
    }
}

#[test]
fn files_are_analyzed_in_parallel() {
    let mut run = Run::start(
        "parallel",
        &[
            "--file-timeout",
            "0",
            "--max-lines",
            "1",
            "-p",
            "wall.py",
            "slow.py",
            "other.py",
        ],
    );
    // The last file must be read while the preceding file is still blocked.
    run.feed("other.py");
    run.feed("slow.py");
    assert_eq!(wait(&mut run.child, Duration::from_secs(2)).code(), Some(1));
    let report = run.output("stdout");
    let files: Vec<_> = report
        .lines()
        .filter(|line| line.contains("CW001"))
        .collect();
    assert_eq!(files.len(), 3);
    for (line, file) in files.iter().zip(["wall.py", "slow.py", "other.py"]) {
        assert!(line.starts_with(file), "{report}");
    }
    assert_eq!(
        report
            .matches(include_str!("../prompts/comment-guidance.md"))
            .count(),
        1
    );
    assert!(run.output("stderr").is_empty());
}

#[test]
fn report_is_withheld_until_all_files_finish() {
    let mut run = Run::start(
        "buffering",
        &[
            "--file-timeout",
            "0",
            "--max-lines",
            "1",
            "wall.py",
            "missing.py",
            "slow.py",
        ],
    );
    // Observe both streams throughout a window where one file cannot finish.
    run.assert_quiet_for(Duration::from_millis(200));
    run.feed("slow.py");
    assert_eq!(wait(&mut run.child, Duration::from_secs(2)).code(), Some(1));
    assert!(run.output("stdout").is_empty());
    let report = run.output("stderr");
    let lines: Vec<_> = report.lines().collect();
    assert_eq!(lines.len(), 3, "{report}");
    assert!(lines[0].starts_with("wall.py:1:1: CW001"));
    assert!(lines[1].starts_with("missing.py:"));
    assert!(lines[2].starts_with("slow.py:1:1: CW001"));
}

#[test]
fn per_file_timeouts_overlap() {
    let mut run = Run::start(
        "overlapping-timeouts",
        &["--file-timeout", "1", "slow.py", "other.py"],
    );
    assert_eq!(
        wait(&mut run.child, Duration::from_millis(1800)).code(),
        Some(1)
    );
    assert!(run.output("stdout").is_empty());
    assert_eq!(run.output("stderr"), "slow.py: analysis timed out after 1 seconds\nother.py: analysis timed out after 1 seconds\n");
}

#[test]
fn timeout_report_preserves_other_results() {
    let mut run = Run::start(
        "timeouts",
        &[
            "--file-timeout",
            "1",
            "--max-lines",
            "1",
            "-p",
            "slow.py",
            "wall.py",
            "other.py",
            "missing.py",
        ],
    );
    assert_eq!(wait(&mut run.child, Duration::from_secs(3)).code(), Some(1));
    assert!(run.output("stdout").is_empty());
    let report = run.output("stderr");
    let lines: Vec<_> = report.lines().take(4).collect();
    assert_eq!(lines[0], "slow.py: analysis timed out after 1 seconds");
    assert!(lines[1].starts_with("wall.py:1:1: CW001"));
    assert_eq!(lines[2], "other.py: analysis timed out after 1 seconds");
    assert!(lines[3].starts_with("missing.py:"));
    assert_eq!(
        report
            .matches(include_str!("../prompts/comment-guidance.md"))
            .count(),
        1
    );
}

#[test]
fn default_timeout_is_five_seconds() {
    let mut default = Run::start("default", &["-p", "slow.py"]);
    let started = Instant::now();
    assert_eq!(
        wait(&mut default.child, Duration::from_secs(7)).code(),
        Some(1)
    );
    // Allow scheduling around process creation without accepting a shorter timeout.
    assert!(started.elapsed() >= Duration::from_millis(4800));
    assert!(default.output("stdout").is_empty());
    assert_eq!(
        default.output("stderr"),
        "slow.py: analysis timed out after 5 seconds\n"
    );
}

#[test]
fn zero_timeout_waits_beyond_the_default_limit() {
    let mut unlimited = Run::start("unlimited", &["--file-timeout", "0", "slow.py"]);
    unlimited.assert_quiet_for(Duration::from_millis(5200));
    unlimited.feed("slow.py");
    assert!(wait(&mut unlimited.child, Duration::from_secs(2)).success());
    assert!(unlimited.output("stdout").is_empty());
    assert!(unlimited.output("stderr").is_empty());
}
