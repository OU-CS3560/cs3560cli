# cs3560cli

A set of internal tools for [Ohio University](https://www.ohio.edu/)'s CS3560 course.

## Installation

```console
python -m pip install cs3560cli
```

## Features

### `blackboard student-list` Command

Offer a link to get student enrollment data and offer to parse the JSON data into TSV data for
an Excel sheet or [Google Sheet](https://sheets.new/)

Usage
```console
$ python -m cs3560cli blackboard student-list https://blackboard.ohio.edu/ultra/courses/_642196_1/cl/outline

Student list link:

https://blackboard.ohio.edu/learn/api/public/v1/courses/_642196_1/users?fields=id,userId,user,courseRoleId

Visit the link above in your browser.
Then copy and paste in the JSON data below and hit Ctrl-D (EOF) when you are done:

... [JSON Data pasted in by the user] ...

TSV data of the students:


firstName       lastName        emailHandle     isDrop  github-username team-id team-name       m1      m2      m3      m4      final   assigned-ta      note    discord-username        codewars-username       userId  courseMembershipId
... [formatted row of TSV data] ...
```

You can then copy this TSV data and paste into Excel sheet or [Google Sheet](https://sheets.new/).

### `blackboard categorize` Command

When you download all submissions from an assignment, you will get a zip file with files from all students
together in one place. This command can group files from a student together in a folder of their username.

```console
$ python -m cs3560cli blackboard categorize gradebook_CS_3560_100_LEC_SPRG_2023-24_HW2.zip hw2
Categorizing files ...
$ ls hw2/
kc555014 ...
```

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
