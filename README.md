# cs3560cli

A set of internal tools for [Ohio University](https://www.ohio.edu/)'s CS3560 course, open-sourced.

## Installation

```console
python -m pip install cs3560cli
```

## Usage

```console
python -m cs3560cli --help
```

## Features

### watch-zip

Watch for an archive file and extract it.

Usage

```console
$ python -m cs3560cli watch-zip .
$ python -m cs3560cli watch-zip ~/Downloads
```

### highlight

Create a syntax highlight code block with in-line style. The result can thus be embed into a content of LMS.

### create-gitignore

Create a `.gitignore` file using content from [github/gitignore repository](https://github.com/github/gitignore).

Usage

```console
$ python -m cs3560cli create-gitignore python
$ python -m cs3560cli create-gitignore cpp
```

By default, it also add `windows` and `macos` to the `.gitignore` file.

### check-username
