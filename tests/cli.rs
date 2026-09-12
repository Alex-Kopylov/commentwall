use std::process::Command;

const GUIDANCE: &str = include_str!("../prompts/comment-guidance.md");

#[test]
fn guidance_is_opt_in_and_once_per_invocation() {
    let dir = std::env::temp_dir().join(format!("commentwall-cli-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(
        dir.join("one.py"),
        "if True:\n    # a\n    # b\n    pass\n# c\n# d\n",
    )
    .unwrap();
    std::fs::write(dir.join("two.py"), "# e\r\n# f\r\n").unwrap();
    std::fs::write(dir.join("clean.py"), "x = 1\n").unwrap();

    let diagnostics = "one.py:2:5: CW001 Standalone comment block of 2 lines exceeds max-lines 1\n\
one.py:5:1: CW001 Standalone comment block of 2 lines exceeds max-lines 1\n\
two.py:1:1: CW001 Standalone comment block of 2 lines exceeds max-lines 1\n";
    for prompt_flag in [None, Some("--with-prompt"), Some("-p")] {
        let mut command = Command::new(env!("CARGO_BIN_EXE_commentwall"));
        command.current_dir(&dir).args(["--max-lines", "1"]);
        if let Some(prompt_flag) = prompt_flag {
            command.arg(prompt_flag);
        }
        let output = command.args(["one.py", "two.py"]).output().unwrap();
        assert_eq!(output.status.code(), Some(1));
        assert!(output.stderr.is_empty());
        let expected = if prompt_flag.is_some() {
            format!("{diagnostics}\n{GUIDANCE}")
        } else {
            diagnostics.to_owned()
        };
        assert_eq!(String::from_utf8(output.stdout).unwrap(), expected);
    }

    for (file, code) in [("clean.py", 0), ("missing.py", 1)] {
        let output = Command::new(env!("CARGO_BIN_EXE_commentwall"))
            .current_dir(&dir)
            .args(["--with-prompt", file])
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(code));
        assert!(output.stdout.is_empty());
        assert_eq!(output.stderr.is_empty(), code == 0);
    }
    std::fs::remove_dir_all(dir).unwrap();
}

#[test]
fn help_needs_no_files_and_lists_options() {
    for flag in ["--help", "-h"] {
        let output = Command::new(env!("CARGO_BIN_EXE_commentwall"))
            .arg(flag)
            .output()
            .unwrap();
        assert!(output.status.success());
        assert!(output.stderr.is_empty());
        let help = String::from_utf8(output.stdout).unwrap();
        for option in [
            "--with-prompt",
            "-p",
            "--max-lines",
            "--file-timeout",
            "--help",
        ] {
            assert!(help.contains(option), "missing {option}: {help}");
        }
        assert!(!help.contains(GUIDANCE));
        assert!(help.contains("0 waits indefinitely"));
        assert!(help.contains("[default: 5]"));
        assert!(help.contains("one report"));
    }
}

#[test]
fn invalid_file_timeouts_are_rejected() {
    for value in ["-1", "1.5", "abc", "18446744073709551616"] {
        let output = Command::new(env!("CARGO_BIN_EXE_commentwall"))
            .args(["--file-timeout", value, "file.py"])
            .output()
            .unwrap();
        assert_eq!(output.status.code(), Some(2));
        assert!(output.stdout.is_empty());
    }
}
