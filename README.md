# metrolina-code-challenge

## Setup

### Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows, use `python -m venv venv` if `python3` isn't available.

**OS-specific activation**

- macOS/Linux (bash/zsh): `source venv/bin/activate`
- Windows PowerShell: `.\venv\Scripts\Activate.ps1`
- Windows Command Prompt: `.\venv\Scripts\activate.bat`

### Install dependencies

```bash
pip install -r requirements.txt
```

### Provide the API key

Set the API key as an environment variable before running tests.

```bash
export API_KEY="your-api-key-here"
```

## Tests

```bash
pytest -v
```

## Assumptions

- The API key is supplied via the `API_KEY` environment variable for all authenticated requests.
- UPC is internally reformatted in the backend by adding a leading zero

## Additional tests to add

### Auth endpoint

- Expired or revoked API key is handled gracefully.
- API key is not accepted when passed via query string (header-only enforcement).

### Items endpoint

- UPC filtering correctly handles both 11 and 12-digit formats, returning consistent results.