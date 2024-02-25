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
