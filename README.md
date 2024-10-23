# cs3560cli

A set of internal tools for [Ohio University](https://www.ohio.edu/)'s CS3560 course.

## Installation

```console
python -m pip install cs3560cli
```

## Features

- `categorize` : Group students submitted files and put them in a folder. One folder for each student.
- `create gh-invite` : Invite students to a team in GitHub organization using data from Canvas.
- `create gitignore` : Create an opinionated `.gitignore` file where `macOS.gitignore` and `Windows.gitignore` are included by default.
- `watch` : Watch for (and extract) the zip file.
- `highlight` : Create HTML fragments of a syntax highlighted snippet of code that can then be embedded in LMS. For an image of the source code, you may want to use [Charm's freeze](https://github.com/charmbracelet/freeze) instead.
- `check github-username` : Check if the GitHub or Codewars username the student provided actually exist or not.

## Examples

<details>
<summary>categorize</summary>

![categorize movie](./tapes/categorize.gif)

</details>

<details>
<summary>highlight</summary>

![highlight movie](./tapes/highlight.gif)

</details>

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
