# Swecha Corpus Client CLI

Mana Hyderabad can use the external Swecha Corpus Client CLI when the team needs to upload approved civic-tech documents, images, audio, OCR output, ASR transcripts, or translation artifacts to the Swecha Corpus API.

Source project: <https://code.swecha.org/corpus/corpus-client-cli>

This repository does not vendor or reimplement the CLI. Install and run it separately, then point it at curated files exported from Mana Hyderabad.

## Prerequisites

- Python 3.14 or higher for the Corpus Client CLI.
- `uv` 0.5.0 or higher.
- A Corpus API account.
- Approved, non-sensitive upload artifacts.

Do not upload citizen PII, secrets, local `.env` files, database dumps, or unreviewed complaint evidence.

## Install the CLI

```bash
git clone https://code.swecha.org/corpus/corpus-client-cli.git
cd corpus-client-cli
uv sync
```

For development dependencies:

```bash
uv sync --dev
```

## Authenticate

Use the Corpus API URL and credentials provided by the Swecha team.

```bash
uv run corpus-client login
```

Or pass options explicitly:

```bash
uv run corpus-client login \
  --url https://dev.api.corpus.swecha.org \
  --phone +91XXXXXXXXXX \
  --password "<password>"
```

Check the saved session:

```bash
uv run corpus-client status
```

Log out when finished:

```bash
uv run corpus-client logout
```

## Upload Mana Hyderabad Files

Use `upload-files` for approved raw files such as public demo documents, cleaned images, or reviewed audio samples.

```bash
uv run corpus-client upload-files /path/to/approved-mana-hyderabad-files
```

The CLI prompts for metadata:

- Categories fetched from the Corpus API.
- Language from the scheduled-language list.
- Release rights.
- Media type.
- Description.
- Source label.

Suggested source labels:

```text
Mana Hyderabad civic-tech demo
Mana Hyderabad reviewed complaint media
Mana Hyderabad QA transcript sample
```

Resume an interrupted upload:

```bash
uv run corpus-client resume
```

Clear saved progress state:

```bash
uv run corpus-client clear
```

## Upload Extracted Text

Use `extract` for reviewed OCR, ASR, transcription, or translation JSON files linked to existing Corpus record IDs.

```bash
uv run corpus-client extract /path/to/mapping.csv /path/to/json-directory
```

Expected CSV format:

```csv
uid,filename
record-uuid-1,complaint-audio-001
record-uuid-2,complaint-image-ocr-002
```

Expected ASR-style JSON:

```json
{
  "transcription": "Garbage is blocking the drain near Madhapur Metro.",
  "segments": [
    { "start": 0.0, "end": 2.5, "text": "Garbage is blocking the drain" },
    { "start": 2.5, "end": 5.0, "text": "near Madhapur Metro." }
  ]
}
```

Expected OCR layout JSON:

```json
[
  {
    "type": "text",
    "text": "Garbage near Madhapur Metro",
    "bbox": [10, 20, 300, 80]
  }
]
```

## Generated State and Logs

The Corpus CLI writes local progress and debug files:

```text
upload_state.json
extracted_text_state.json
corpus_client_state.json
upload_log.txt
uploaded_extracted_text.log
```

These files are ignored in this repository. They may contain session metadata or upload details and should not be committed.

## Quality Commands for CLI Contributors

When contributing to the external CLI repository, use its own quality commands:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
uv run bandit -r src/corpus_client_cli
uv run pre-commit run --all-files
```

These commands belong to the external `corpus-client-cli` project, not the Mana Hyderabad web application.

## Troubleshooting

- `409 Conflict`: The upload already exists. The CLI treats this as completed for resume purposes.
- `422 Unprocessable Entity`: The server rejected the payload. Check CLI debug logs and metadata fields.
- `Authentication Failed`: Verify phone number, password, and API base URL.
- `Not Authenticated`: Run `uv run corpus-client login`.
