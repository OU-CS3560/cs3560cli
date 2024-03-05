# Changelog

## Unreleased

- Fix not being able to `Ctrl-C` the `blackboard student-list` command on Windows.
- Fix mypy's errors/warnings.
- Update commands' documentation.
- Add `--file` option for `blackboard student-list`.
- Fix `click.exit` does not exist by using `ctx.exit` instead.

## v0.2.1a1

- Add `blackboard categorize` command from `krerkkiat/ta-tooling`.
- Add `github get-team-id` command from `OU-CS3560/org-bulk-invite`.

## v0.2.0

See changes from v0.2.0a1 to v0.2.0rc1.

## v0.2.0rc1

- Finalize the format of the TSV data `blackboard student-list` outputs.

## v0.2.0a1

- BREAKING CHANGE: Rename `cs3560cli.functions` to `cs3560cli.commands`.
- Centralize version number location.
- Add `cs3560cli.blackboard` with utilities for Blackboard.
- Add `help` command.
- Add `blackboard student-list` command.
- Add the web UI version of the `blackboard student-list` command.

## v0.1.4

- Revise project metadata. No change to the codebase.

## v0.1.3

- Fix bug in the highlight command.

## v0.1.2

- Adding `highlight` command
- Fix the command line setting for setuptools.

## v0.1.1

- Add `create-gitignore` command.
- Fix missing dependency for `watchdog`.
