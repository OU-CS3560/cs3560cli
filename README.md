# cs3560cli

A set of internal tools for [Ohio University](https://www.ohio.edu/)'s CS3560 course.

## Installation

```console
python -m pip install cs3560cli
```

## Features

### Import students from Canvas into a team in GitHub Organization

If content of your course is in GitHub repository that requires students to be part of a GitHub's organization. The following command
will automatically send email invitation to students' OHIO email addresses using information from Canvas.

```console
$ python -m cs3560cli github bulk-invite-from-canvas <course-id> <team-path> --with-canvas-token <canvas-token> --with-github-token <github-token>
```

A team must exist in the organization. Access token for Canvas can be generated at https://ohio.instructure.com/profile/settings. Access token for GitHub can be generated at https://github.com/settings/tokens. Please make sure that the token has 'admin:org' permission and it is SSO-SAML authorized for your organization.

### Group students submitted files into folders

To be implemented for Canvas.

### `watch-zip` Command

Watch for an archive file and extract it. This can be useful when you are grading
student's submission, so you do not have to manually unzip it.

Usage

```console
$ python -m cs3560cli watch-zip .
$ python -m cs3560cli watch-zip ~/Downloads
```

### `highlight` Command

Create a syntax highlight code block with in-line style. The result can thus be embed into a content of LMS.

### `create-gitignore` Command

Create a `.gitignore` file using content from [github/gitignore repository](https://github.com/github/gitignore).

Usage

```console
$ python -m cs3560cli create-gitignore python
$ python -m cs3560cli create-gitignore cpp
```

By default, it also add `windows` and `macos` to the `.gitignore` file.

### `check-username` Command

TBD

## Scenario

### New semester preparation

1. Obtain the list of enrolled students.
2. Creating a team in GitHub organization.
3. Add `OU-CS3560/examples` to the team.
3. Invite all students into the team in GitHUb organization.

Requirements

```ps1
gh extension install mislav/gh-repo-collab
```

```ps1
$TeamName = "entire-class-24f"
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /orgs/OU-CS3560/teams \
  -f name="$TeamName" \
  -f notification_setting='notifications_disabled' \
  -f privacy='closed'
gh repo-collab add OU-CS3560/examples "OU-CS3560/$TeamName" --permission read
python -m cs3560cli github bulk-invite
```

### Creating repositories for teams

1. (manual) Obtain team information (internal-id, members).
2. Create a team.
3. Create a repository.
4. Add team to the repository with `maintain` permission.
4. (manual) Invite students to the team.

Requirements

```ps1
gh extension install mislav/gh-repo-collab
```

```ps1
$TeamId = ""
$TeamHandle = "OU-CS3560/" + $TeamId
$RepoHandle = "OU-CS3560/" + $TeamId

$ParentTeamId = python -m cs3560cli github get-team-id OU-CS3560 entire-class-24f | Out-String
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /orgs/OU-CS3560/teams \
  -f parent_team_id=$ParentTeamId \
  -f name="$TeamId" \
  -f notification_setting='notifications_disabled' \
  -f privacy='closed'
gh repo create --private --template OU-CS3560/team-template $RepoHandle
gh repo-collab add $RepoHandle $TeamHandle --permission maintain
```
