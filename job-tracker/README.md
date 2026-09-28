# Job Tracker (standalone, local copy)

A simple local web app for tracking job applications — status, next steps,
interview dates, contract vs. perm details, recruiter contact log, and a
dashboard of stats. Runs entirely on your own machine; nothing leaves your
laptop and there's no shared or online database.

## Requirements

- macOS
- Python 3.11+

Check what you have:

```bash
python3 --version
```

If it's older than 3.11, install a newer one with [Homebrew](https://brew.sh):

```bash
brew install python@3.11
```

## Setup (one-time)

Open Terminal, `cd` into this folder, then:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

The `.env` file is fine as-is to start. It just points the app at a local
SQLite database file (`job_tracker.db`) that gets created automatically the
first time you run it — completely private to this folder, on this machine.

## Running it

```bash
source venv/bin/activate   # if not already active
uvicorn main:app --reload
```

Then open **http://localhost:8000** in your browser.

To stop it, press `Ctrl+C` in the terminal. To run it again later, just
repeat the `source venv/bin/activate` + `uvicorn main:app --reload` steps
from this folder — no need to redo the setup.

## Your data

Everything you enter is stored in a single file: `job_tracker.db`, right
in this folder. Back it up by copying that file somewhere safe (e.g. iCloud
Drive, Dropbox) whenever you like — there's no server-side copy anywhere.

## Optional: AI auto-extract from job postings

There's a feature to paste in a job posting (or its URL) and have an AI
pull out the company, title, salary, location, etc. automatically. It's
**off by default** in this copy — everything else works fine without it,
you'll just fill those fields in by hand.

To turn it on, you need access to some OpenAI-compatible chat API. The
easiest free option is [Ollama](https://ollama.com) running locally:

```bash
brew install ollama
ollama pull llama3.2
```

Then uncomment the `LLM_BASE_URL` / `LLM_MODEL` lines in `.env` (see the
comments in that file for the exact values) and restart the app.

## Questions

Ping Ed if anything breaks.
