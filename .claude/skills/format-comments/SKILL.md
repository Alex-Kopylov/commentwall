---
name: format-comments
description: "Use whenever the user wants comment blocks rewritten, shortened, or tidied in files or a diff, or when a commentwall report hands off to format-comments. Rewrites each block in place as the shortest comment that states the non-obvious why."
argument-hint: "[files, diff, or commentwall report]"
---

# Format comments

Treat comments as production code. They must make sense to a reader
who never saw this chat.

## Scope

`$ARGUMENTS` may name files, a diff, or a `commentwall` report (`file:line:column: CW001 ...`). With a report, only the flagged blocks are in scope. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Rules

- Comment only the non-obvious why: invariant, protocol constraint,
  external bug workaround, ordering that looks arbitrary.
- One line when one line is enough. Delete anything that restates
  the next line of code.
- Describe what the code is now. Never what it used to be, what we
  tried, what the user asked, or which ticket prompted the change.
- No memorializing decisions. That belongs in the commit message.

## Steps

1. Rewrite each comment block in scope in place under the rules. A block that only restates the code is deleted.
2. Touch no code and no comment outside the scope.
3. Report touched files and the number of blocks rewritten or deleted.
