# Mana Hyderabad: AI-Powered Civic Complaint Copilot

Mana Hyderabad is a multilingual civic-tech platform that helps residents report civic issues quickly and helps municipal teams prioritise complaints intelligently.

- **Website Link**: https://mana-hyderabad.vercel.app/

**License:** GNU Affero General Public License v3.0 or later. See [LICENSE](LICENSE).

## Repository Layout

This repository is organised as a small monorepo:

```text
.
├── app/                         # Next.js frontend routes
├── components/                  # Frontend UI components
├── lib/                         # Frontend types, mock API boundary, utilities
├── messages/                    # Frontend translations
├── mana-hyderabad-backend/      # FastAPI backend, Alembic, PostGIS config
├── .specify/                    # Spec Kit project memory and templates
├── specs/                       # Spec Kit feature specifications and plans
├── package.json                 # Frontend dependencies and scripts
└── README.md
```

Run the frontend from the repository root:

```bash
npm install
cp .env.example .env.local
npm run dev
```

To use mock frontend data, leave `NEXT_PUBLIC_API_BASE_URL` unset. To connect the frontend to the FastAPI backend, set:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Run the backend from `mana-hyderabad-backend/`:

```bash
cd mana-hyderabad-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Frontend: `http://localhost:3000`

Backend Swagger: `http://127.0.0.1:8000/docs`

## Spec Kit Workflow

This repository includes GitHub Spec Kit artifacts for spec-driven development.

Current Spec Kit files:

- `.specify/memory/constitution.md` — project principles and quality rules
- `.specify/templates/` — local spec, plan, and task templates
- `specs/001-mana-hyderabad-platform/` — baseline platform specification, implementation plan, tasks, data model, research notes, and quickstart

The team workflow follows:

```text
/speckit.constitution → /speckit.specify → /speckit.clarify
→ /speckit.plan → /speckit.tasks → /speckit.analyze
→ /speckit.implement
```

For future phases, create a new folder under `specs/` before implementing code. Write requirements in `spec.md` first, add technology choices in `plan.md`, then break work into `tasks.md`.

---

The platform accepts text, voice, photographs, and GPS location. It can understand complaints written in English, Telugu, Hindi, Urdu, or mixed-language formats such as Telugu-English and Hindi-English. It converts each complaint into a structured ticket, identifies likely duplicates, estimates urgency, and displays complaints on a map-based operations dashboard.

> This repository contains a proof-of-concept implementation. It is not an official GHMC or Government of Telangana service.

---

## 1. Problem Statement

Residents often face practical barriers while reporting civic issues:

- They may not know which department handles the issue.
- They may be more comfortable using Telugu, Hindi, Urdu, or mixed-language messages.
- Complaints may be incomplete, duplicated, or difficult to prioritise.
- Municipal teams may receive multiple reports for the same location without a consolidated view.
- Photographs, GPS coordinates, and written descriptions are often stored separately instead of being analysed together.

Mana Hyderabad addresses these gaps with a multilingual AI-assisted complaint workflow.

---

## 2. Core Use Cases

The first version focuses on visible and easily verifiable civic issues:

| Category      | Example complaints                                          |
| ------------- | ----------------------------------------------------------- |
| Sanitation    | Garbage accumulation, overflowing bins, construction debris |
| Drainage      | Blocked drains, stagnant water, open drains                 |
| Roads         | Potholes, damaged road surfaces, broken manhole covers      |
| Street lights | Non-functional lights, damaged poles                        |
| Water supply  | Leakage, low pressure, suspected contamination              |
| Traffic       | Signal malfunction, unsafe congestion point                 |
| Public health | Mosquito-breeding risk, stagnant water near residences      |

---

## 3. Key Features

### Citizen-facing features

- Submit a complaint through text, voice, or photo upload.
- Share GPS location or enter a landmark manually.
- Select a preferred language.
- Receive AI-generated follow-up questions when details are missing.
- Receive a complaint reference number.
- Track complaint status.

### Municipal dashboard features

- View complaints on an interactive city map.
- Filter by category, urgency, language, date, and status.
- Group likely duplicate complaints.
- Review uploaded photographs and AI-generated findings.
- View hotspot clusters.
- Update complaint status.
- View a concise field-inspection summary.

### AI features

- Language detection.
- Translation and mixed-language normalisation.
- Structured complaint extraction.
- Department routing.
- Missing-information detection.
- Duplicate complaint detection.
- Photograph analysis.
- Severity scoring.
- Multilingual response generation.

---

## 4. Example Complaint Flow

A citizen submits:

```text
Kukatpally metro daggara garbage chaala undi. Drain kuda block ayyindi.
```

The application normalises the message:

```json
{
  "category": "SANITATION",
  "subcategory": "BLOCKED_DRAIN_WITH_GARBAGE",
  "normalized_text": "Garbage has accumulated near Kukatpally Metro and appears to be blocking the drain.",
  "location_text": "Kukatpally Metro",
  "location_missing": false,
  "requires_photo": true,
  "requires_gps": true,
  "urgency": "MEDIUM"
}
```

The assistant replies in the citizen's selected language and asks only for missing details:

```text
Please share your current location and upload a photograph so the issue can be recorded accurately.
```

---

## 5. Proposed Architecture

```text
Citizen Web App
Text | Voice | Photo | GPS | Language
        |
        v
FastAPI Backend
Authentication | Uploads | Complaint APIs
        |
        +----------------------+
        |                      |
        v                      v
Language Layer            Vision Layer
Language detection        Garbage detection
Translation               Pothole detection
Speech-to-text            Blocked-drain detection
Text-to-speech            Stagnant-water detection
        |                      |
        +----------+-----------+
                   |
                   v
Complaint Intelligence Layer
Extraction | Routing | Severity | Duplicate detection
                   |
                   v
PostgreSQL
PostGIS | pgvector | Complaint records
                   |
                   v
Operations Dashboard
Map | Filters | Hotspots | Status updates
```

---

## 6. Recommended Technology Stack

| Layer              | Technology                                             | Purpose                                             |
| ------------------ | ------------------------------------------------------ | --------------------------------------------------- |
| Frontend           | Next.js, TypeScript, Tailwind CSS                      | Mobile-friendly citizen portal and admin dashboard  |
| Mapping            | MapLibre GL JS                                         | Interactive complaint map                           |
| Backend            | FastAPI, Python                                        | REST APIs and AI orchestration                      |
| Database           | PostgreSQL                                             | Complaint storage                                   |
| Geospatial queries | PostGIS                                                | Radius search, hotspot mapping, ward-level analysis |
| Similarity search  | pgvector                                               | Semantic duplicate detection                        |
| File storage       | Supabase Storage, Cloudinary, or S3-compatible storage | Uploaded images and audio                           |
| Translation        | BHASHINI APIs or AI4Bharat IndicTrans2                 | Indian-language translation                         |
| Speech             | BHASHINI ASR and TTS                                   | Voice input and spoken responses                    |
| LLM layer          | Multilingual LLM API or locally hosted instruct model  | Extraction, routing, follow-up questions, summaries |
| Computer vision    | YOLO or a lightweight image classifier                 | Detect visible civic issues                         |
| Deployment         | Docker, Render, Railway, or a cloud VM                 | Hosting                                             |
| Optional analytics | Metabase or custom dashboard                           | Trends and hotspot analysis                         |

---

## 7. Multilingual Design

The system supports:

- English
- Telugu
- Hindi
- Urdu
- Mixed-language and transliterated text

Examples:

```text
Road pe waterlogging hai near Gachibowli signal.
Drain block ayyindi since yesterday.
Charminar ke paas street light kaam nahi kar rahi.
```

The application stores both the original text and an internal normalised version:

```json
{
  "original_text": "Drain block ayyindi since yesterday",
  "detected_language": "mixed",
  "normalized_english_text": "The drain has been blocked since yesterday.",
  "response_language": "te"
}
```

### Why store both versions?

- Local landmarks must be preserved.
- Translation may lose informal wording.
- Officers may want to review the citizen's original message.
- Future models can be improved using anonymised real-world examples.

---

## 8. AI Prompt Design

### Complaint extraction prompt

```text
You are an AI assistant for a municipal complaint platform.

The input may contain English, Telugu, Hindi, Urdu, transliterated text,
spelling errors, or mixed-language phrases.

Tasks:
1. Preserve locality names, landmarks, road names, and proper nouns.
2. Convert the complaint into clear internal English.
3. Identify the department and subcategory.
4. Estimate urgency using only the available evidence.
5. Identify missing details.
6. Never invent a location.
7. Never claim that a complaint has been resolved.
8. Return valid JSON only.
```

### Follow-up prompt

```text
Generate a short and polite response in the citizen's selected language.
Ask only for missing information.
Do not promise a resolution date.
Use simple language.
```

### Field-inspection summary prompt

```text
Create a concise inspection note for a municipal field team.

Include:
- complaint type
- location
- photograph findings
- duplicate complaint count
- risk factors
- recommended priority

Treat photograph analysis as preliminary.
Use phrases such as "appears to show" and "requires field verification."
```

---

## 9. Suggested Database Schema

### complaints

| Field           | Description                                 |
| --------------- | ------------------------------------------- |
| id              | Unique complaint reference                  |
| original_text   | Citizen's original complaint                |
| normalized_text | Internal English version                    |
| language_code   | en, te, hi, ur, or mixed                    |
| category        | Main complaint type                         |
| subcategory     | Detailed issue type                         |
| severity        | LOW, MEDIUM, HIGH, or EMERGENCY             |
| latitude        | GPS latitude                                |
| longitude       | GPS longitude                               |
| landmark        | Optional typed landmark                     |
| image_url       | Uploaded photograph                         |
| audio_url       | Optional voice recording                    |
| vision_labels   | AI-detected image labels                    |
| status          | SUBMITTED, UNDER_REVIEW, ASSIGNED, RESOLVED |
| duplicate_of    | Existing complaint ID, when applicable      |
| created_at      | Submission timestamp                        |
| updated_at      | Last modified timestamp                     |

### departments

| Field                | Description                                   |
| -------------------- | --------------------------------------------- |
| id                   | Department identifier                         |
| name                 | Department name                               |
| supported_categories | Complaint categories routed to the department |

### status_history

| Field        | Description       |
| ------------ | ----------------- |
| id           | History record ID |
| complaint_id | Related complaint |
| old_status   | Previous status   |
| new_status   | Updated status    |
| updated_by   | Admin or system   |
| updated_at   | Update timestamp  |

---

## 10. Duplicate Detection Logic

A new complaint can be compared with existing records using:

1. PostGIS radius search within 100 to 300 metres.
2. Category and subcategory matching.
3. Time-window matching.
4. Text-embedding similarity using pgvector.
5. Optional image similarity.

Example:

```text
New complaint:
"Garbage is blocking the drain near Kukatpally Metro."

Existing complaint:
"Waste piled up beside the drain outside Kukatpally station."

Possible duplicate:
Location distance: 42 metres
Semantic similarity: 0.91
Category match: Yes
```

An admin should confirm the duplicate match before records are merged.

---

## 11. Proof of Concept Scope

A realistic proof of concept should demonstrate one complete workflow instead of attempting every feature.

### Minimum working flow

1. Citizen selects a language.
2. Citizen types a complaint or submits a sample voice transcript.
3. Citizen uploads a photograph.
4. Citizen shares GPS coordinates.
5. AI extracts the complaint type, subcategory, severity, and missing details.
6. Application translates the response into the selected language.
7. Complaint is stored in PostgreSQL.
8. Complaint appears on an admin map.
9. System checks for nearby duplicate complaints.
10. Admin updates the status.

### Recommended demo categories

Use only these four categories initially:

```text
garbage_heap
blocked_drain
stagnant_water
pothole
```

### Strong demo script

1. Submit a Telugu-English complaint about garbage blocking a drain.
2. Upload a photograph and share a location.
3. Show the generated structured ticket.
4. Submit a similar complaint from a nearby location.
5. Show duplicate detection.
6. Open the admin map and inspect the hotspot.
7. Change the status to `UNDER_REVIEW`.
8. Show the multilingual status response.

---

## 12. Local Development Setup

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose
- Git

### Clone the repository

```bash
git clone <repository-url>
cd mana-hyderabad
```

### Environment variables

Frontend environment variables live in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=false
NEXT_PUBLIC_MAP_STYLE_URL=https://demotiles.maplibre.org/style.json
NEXT_PUBLIC_ENABLE_SPEECH_INPUT=true
NEXT_PUBLIC_ENABLE_TTS_RESPONSES=false
```

Backend environment variables live in `mana-hyderabad-backend/.env`. Never commit `.env`, `.env.local`, API keys, BHASHINI credentials, Cloudinary secrets, uploaded citizen data, or database dumps.

### Start PostgreSQL

```bash
cd mana-hyderabad-backend
docker compose up -d
```

### Start the backend

```bash
cd mana-hyderabad-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Start the frontend

```bash
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## 13. Suggested Repository Structure

```text
mana-hyderabad/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── prompts/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── ml/
│   ├── notebooks/
│   ├── datasets/
│   └── models/
├── docs/
│   ├── USER_MANUAL.md
│   └── architecture.md
├── .env.example
├── docker-compose.yml
├── CONTRIBUTING.md
├── README.md
└── LICENSE
```

---

## 14. API Endpoints

| Method | Endpoint                           | Purpose                   |
| ------ | ---------------------------------- | ------------------------- |
| POST   | `/api/complaints`                  | Submit complaint          |
| GET    | `/api/complaints/{id}`             | Retrieve complaint        |
| GET    | `/api/complaints`                  | Filter complaint list     |
| POST   | `/api/complaints/{id}/attachments` | Upload image or audio     |
| POST   | `/api/complaints/{id}/analyse`     | Run AI analysis           |
| GET    | `/api/complaints/{id}/duplicates`  | Find possible duplicates  |
| PATCH  | `/api/complaints/{id}/status`      | Update status             |
| GET    | `/api/hotspots`                    | Retrieve hotspot clusters |
| POST   | `/api/translate`                   | Translate message         |
| POST   | `/api/transcribe`                  | Convert voice to text     |

---

## 15. Responsible AI Guidelines

- Do not claim that AI output is verified evidence.
- Use AI findings for prioritisation, not automatic punishment.
- Require human review for duplicate merging and escalation.
- Do not expose personal phone numbers or exact household details publicly.
- Store only necessary information.
- Avoid collecting identity documents in the proof of concept.
- Add confidence scores where possible.
- Log model decisions for testing.
- Do not promise a government response unless the platform is officially integrated.

---

## 16. Current Limitations

The proof of concept may not include:

- Official GHMC integration.
- Production-scale identity verification.
- Automated field-force assignment.
- Reliable emergency-response guarantees.
- Large-scale image-model accuracy.
- Full ward-boundary mapping.
- Production-grade moderation and abuse prevention.

---

## 17. Future Enhancements

- WhatsApp integration.
- Voice-based chatbot.
- Ward-level routing.
- Escalation workflows.
- Officer mobile application.
- SLA tracking.
- Open-data dashboard.
- Heatmap-based resource planning.
- Image-based before-and-after resolution verification.
- Citizen feedback and satisfaction score.
- Real-time rainfall integration for waterlogging risk.

---

## 18. License

Mana Hyderabad is released under the GNU Affero General Public License v3.0 or later. See [LICENSE](LICENSE).

---

## 19. Disclaimer

Mana Hyderabad is a student civic-tech proof of concept. It is not affiliated with GHMC, the Government of Telangana, or any municipal authority unless an official partnership is established.
