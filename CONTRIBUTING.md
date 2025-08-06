# How to contribute

Open an issue on Github if you've found a problem with the project or have a question.

Submit a PR on Github to propose changes. Before doing so make sure that linter
results are clean and tests are passing:

* Install project with test dependencies. This will install `ruff`, `pytest`
  and other test dependencies

```
pip install -e ".[test]"
```

* Run `ruff` to lint the project:

```
ruff check
```

* Run `pytest` to execute tests:

```
python3 -m pytest tests/
```
