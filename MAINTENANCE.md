# Maintaining

## Build

Build time dependencies

```console
python -m pip install --upgrade build twine
```

To build

```console
python -m build
```

To locally install

```console
python -m pip install -e ".[dev,typ]" --config-settings editable_mode=compat
```

## Running the tests

Please make sure that the package is installed with `.[dev]`, then run

```console
pytest tests/
```

Run the test for various python's versions, run

```console
tox
```

With test coverage in py313 environment

```console
pytest --cov=cs3560cli tests/
```

If you want to view the HTML report instead, run 

```console
coverage html
```

then open the HTML file in your browser.

## Publishing

For the detail about version specifier, please see [version specifier](https://packaging.python.org/en/latest/specifications/version-specifiers/)

### Publish to the test PyPI

```console
python -m twine upload -r testpypi dist/*
```

### Publish to the real PyPI

```console
python -m twine upload dist/*
```
