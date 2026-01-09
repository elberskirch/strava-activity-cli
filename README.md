# strava-activity-cli

Manage your Strava activities from the command line.

## Features

- List activities with filtering by date
- Get detailed information about specific activities
- Update activity metadata (name, description, type, etc.)
- JSON output support for all commands
- Automatic token refresh

## Installation

```bash
# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

## Configuration

Create a `.env` file with your Strava API credentials:

```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
```

Ensure you have a `strava-token.json` file with valid access and refresh tokens:

```json
{
  "access_token": "your_access_token",
  "refresh_token": "your_refresh_token",
  "expires_at": 1234567890
}
```

## Usage

### List Activities

```bash
# List 10 most recent activities (default)
uv run strava list

# List specific number of activities
uv run strava list --limit 20

# Filter by date range
uv run strava list --after 2025-01-01 --before 2025-12-31

# Output as JSON
uv run strava list --json

# Use custom token file
uv run strava list --token-file /path/to/token.json
```

### Get Activity Details

```bash
# Get details of a specific activity
uv run strava get 16955758802

# Output as JSON
uv run strava get 16955758802 --json
```

### Update Activity

```bash
# Update activity name
uv run strava update 16955758802 --name "Morning Run"

# Update description
uv run strava update 16955758802 --description "Great workout!"

# Update activity type
uv run strava update 16955758802 --type Run

# Mark as commute
uv run strava update 16955758802 --commute

# Mark as not a commute
uv run strava update 16955758802 --no-commute

# Mark as trainer workout
uv run strava update 16955758802 --trainer

# Multiple updates at once
uv run strava update 16955758802 --name "Evening Run" --description "Easy pace" --type Run
```

## Project Structure

```
strava-activity-cli/
├── strava_cli/
│   ├── __init__.py
│   ├── cli.py          # CLI commands and interface
│   ├── client.py       # Strava API client with token management
│   └── models.py       # Data models for activities
├── pyproject.toml      # Project configuration
├── strava-token.json   # Authentication tokens
└── .env                # API credentials
```

## Development

```bash
# Format code with ruff
uv run ruff format strava_cli/

# Check code with ruff
uv run ruff check strava_cli/

# Auto-fix issues
uv run ruff check --fix strava_cli/
``` 
