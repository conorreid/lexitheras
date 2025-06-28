# Publishing to PyPI

## Prerequisites

1. Create accounts at:
   - https://pypi.org/account/register/
   - https://test.pypi.org/account/register/

2. Create API tokens:
   - Go to https://pypi.org/manage/account/token/
   - Create a token with scope "Entire account"
   - Save it securely

## First Time: Test on TestPyPI

1. Upload to TestPyPI:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   (Use your TestPyPI username and password/token)

2. Test installation from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ lexitheras
   ```

## Publish to PyPI

Once tested, publish to real PyPI:

```bash
python -m twine upload dist/*
```

Use your PyPI username and password/token.

## Using API Tokens (Recommended)

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Then you can upload without entering credentials:
```bash
python -m twine upload dist/*
```

## Updating Version

1. Update version in `pyproject.toml` and `setup.py`
2. Clean old builds: `rm -rf dist/ build/`
3. Build new version: `python -m build`
4. Upload: `python -m twine upload dist/*`