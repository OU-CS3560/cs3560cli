# cs3560cli

A set of internal tooling, open-sourced.

## Installation

```console
python -m pip install cs3560cli
```

## Usage

```console
python -m cs3560cli --help
```

## Features

### check-username

### watch-zip

### (TODO) create-gitignore

## Maintaining

### Build

Build time dependencies

```console
python -m pip install --upgrade build twine
```

To build

```console
python -m build
```

### Upload

#### Upload to test PyPI

```console
twine upload -r testpypi dist/*
```

#### Upload to real PyPI

```console
twine upload dist/*
```