Treat comments as production code. They must make sense to a reader
who never saw this chat.

- Comment only the non-obvious why: invariant, protocol constraint,
  external bug workaround, ordering that looks arbitrary.
- One line when one line is enough. Delete anything that restates
  the next line of code.
- Describe what the code is now. Never what it used to be, what we
  tried, what the user asked, or which ticket prompted the change.
- No memorializing decisions. That belongs in the commit message.
