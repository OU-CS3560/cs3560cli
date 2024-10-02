# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://packaging.python.org/en/latest/discussions/versioning/).

Note that the log for version before v0.2.1 may not be in the mentioned format.

## [Unreleased]



### Added

- Add `github.GitHubApi.get_team_id_from_team_path`.
- Add `github.is_team_path` function.
- Add `github.get_github_token_from_gh_cli` function.
- Add `github.get_github_token_from_environment_variable` function.
- Add `github.get_github_token` function.
- Add test cases for `github.GitHubApi`.
- Add test cases for the top level CLI command.
- Add test cases for the 'highlight' sub-command.
- Add `version` command.

### Changed

- [BREAKING CHANGE] All `github` related commands now take team's path in the format of `<org-name>/<team-name>` instead of two separate arguments.
- [BREAKING CHANGE] All `github` related commands now take `--with-token` or `--with-github-token` options.
- `highlight` sub-command should now properly handle input and output paths.
- Revise documentation for `highlight` sub-command.
- [BREAKING CHANGE] `create-gitignroe` command now asking for confirmations. The command now also show
  that it is accessing resource on GitHub's repository via the network.
- [BREAKING CHANGE] `path_mappings` and `aliases` (in `commands.create_gitignore`) are now just `ALIASES`. 
- [BREAKING CHANGE] `--root` option of `create-gitignroe` is changed to `--outfile`.

### Removed 

- [BREAKING CHANGE] `get_path`, `normalize`. For the first, you can use `ALIASES` directly.
- [BREAKING CHANGE] `get_content` is renamed to `build_gitignore_content`.

## v0.2.1 - 2024-09-24

### Added

- Add `CanvasApi.get_submissions`.
- Add `CanvasApi.get_groups_by_groupset_name`.
- Add mypy and type annotations.

### Deprecated

- Deprecate `lms.blackboard` and its related commands. Will be removed in v0.3.0.

## v0.2.1a3

- Include `cs3560cli.lms` package.

## v0.2.1a2

- Fix not being able to `Ctrl-C` the `blackboard student-list` command on Windows.
- Fix mypy's errors/warnings.
- Update commands' documentation.
- Add `--file` option for `blackboard student-list`.
- Fix `click.exit` does not exist by using `ctx.exit` instead.
- Add support for Canvas
- Add support for GitHub's API
- Add a command that invites students to a team on GitHub Organization directly from Canvas LMS.

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
