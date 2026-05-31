# Contributing to Mana Hyderabad

Thank you for contributing to Mana Hyderabad.

Mana Hyderabad is a multilingual AI-powered civic complaint copilot. Contributions should improve accessibility, reliability, civic usefulness, and responsible AI behaviour.

---

## 1. Code of Conduct

Be respectful, inclusive, and constructive.

Contributors must:

- Treat other contributors respectfully.
- Avoid discriminatory or offensive language.
- Accept technical feedback professionally.
- Protect user privacy.
- Avoid committing personal data, API keys, or confidential information.
- Clearly state when a feature is experimental.

---

## 2. Ways to Contribute

You can contribute through:

- Frontend development
- Backend API development
- Database design
- Map and GIS features
- Multilingual UX
- Translation quality testing
- Speech input support
- Prompt engineering
- Computer-vision datasets
- Model evaluation
- Documentation
- Accessibility improvements
- Test automation
- UI design
- Civic workflow research

---

## 3. Getting Started

### Fork and clone the repository

```bash
git clone <your-fork-url>
cd mana-hyderabad
```

### Create a branch

Use a descriptive branch name:

```bash
git checkout -b feature/telugu-complaint-form
```

Recommended prefixes:

| Prefix      | Use case                 |
| ----------- | ------------------------ |
| `feature/`  | New feature              |
| `fix/`      | Bug fix                  |
| `docs/`     | Documentation            |
| `refactor/` | Code restructuring       |
| `test/`     | Test additions           |
| `ml/`       | Model or dataset changes |
| `prompt/`   | Prompt changes           |

Examples:

```text
feature/admin-hotspot-map
fix/location-permission-error
docs/update-local-setup
prompt/improve-mixed-language-normalisation
ml/add-blocked-drain-training-images
```

---

## 4. Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

```bash
docker compose up -d db
```

Create a local `.env` file from `.env.example`.

Never commit secrets.

---

## 5. Development Workflow

1. Create or select an issue.
2. Create a branch.
3. Make focused changes.
4. Add or update tests.
5. Run linting and tests.
6. Update documentation when behaviour changes.
7. Commit with a clear message.
8. Push the branch.
9. Open a pull request.
10. Respond to review comments.

---

## 6. Commit Message Guide

Use concise, meaningful commit messages.

Recommended format:

```text
type(scope): summary
```

Examples:

```text
feat(frontend): add multilingual complaint form
fix(api): prevent missing GPS coordinates from crashing submission
docs(readme): add proof-of-concept demo flow
feat(map): display complaint hotspots
prompt(normalisation): preserve Hyderabad landmark names
test(duplicates): add nearby complaint matching cases
```

Suggested commit types:

| Type       | Meaning                           |
| ---------- | --------------------------------- |
| `feat`     | New feature                       |
| `fix`      | Bug fix                           |
| `docs`     | Documentation                     |
| `test`     | Test changes                      |
| `refactor` | Internal restructuring            |
| `chore`    | Maintenance                       |
| `prompt`   | Prompt update                     |
| `ml`       | Model, data, or evaluation update |

---

## 7. Pull Request Checklist

Before creating a pull request, confirm that:

- [ ] The change has a clear purpose.
- [ ] The branch contains only related changes.
- [ ] Existing features still work.
- [ ] New behaviour has tests where practical.
- [ ] User-facing changes are documented.
- [ ] No API keys or credentials were committed.
- [ ] No private citizen data was added.
- [ ] AI-generated output is labelled appropriately.
- [ ] Screenshots are included for UI changes.
- [ ] Prompt changes include sample inputs and outputs.
- [ ] Dataset changes include source and licence notes.

---

## 8. Coding Guidelines

### Frontend

- Use TypeScript.
- Build reusable components.
- Ensure mobile responsiveness.
- Use semantic HTML.
- Add clear form labels.
- Ensure keyboard accessibility.
- Avoid hard-coded user-facing text.
- Store translations in language files.

Suggested structure:

```text
frontend/
├── app/
├── components/
│   ├── ComplaintForm.tsx
│   ├── LanguageSelector.tsx
│   ├── LocationPicker.tsx
│   ├── PhotoUploader.tsx
│   └── ComplaintMap.tsx
├── messages/
│   ├── en.json
│   ├── te.json
│   ├── hi.json
│   └── ur.json
└── lib/
```

### Backend

- Use typed request and response models.
- Validate incoming data.
- Keep AI calls inside service modules.
- Handle external API failures gracefully.
- Log errors without logging sensitive personal data.
- Keep prompts versioned in files.
- Add unit tests for routing and validation rules.

Suggested structure:

```text
backend/app/
├── api/
├── models/
├── services/
│   ├── complaint_service.py
│   ├── translation_service.py
│   ├── duplicate_service.py
│   ├── vision_service.py
│   └── llm_service.py
├── prompts/
└── main.py
```

---

## 9. Prompt Engineering Guidelines

Prompts are application logic and must be reviewed carefully.

Each prompt change should include:

- Purpose
- Version number
- Supported languages
- Expected JSON schema
- Example inputs
- Example outputs
- Known edge cases
- Safety constraints

### Example test cases

```text
Input:
"Road pe waterlogging hai near Gachibowli signal"

Expected:
- Category: DRAINAGE
- Subcategory: WATERLOGGING
- Landmark preserved: Gachibowli signal
- No invented coordinates
```

```text
Input:
"Drain block ayyindi"

Expected:
- Category: DRAINAGE
- Subcategory: BLOCKED_DRAIN
- Ask for location
- Ask for photograph when relevant
```

### Prompt rules

- Do not invent missing location details.
- Preserve locality and landmark names.
- Do not mark complaints as resolved.
- Use restricted categories.
- Return valid JSON.
- Keep responses simple.
- Ask only necessary follow-up questions.
- Use human review for escalations.

---

## 10. Multilingual Contribution Guidelines

When adding or updating translations:

- Prefer simple, conversational wording.
- Avoid technical terms.
- Keep meaning consistent across languages.
- Preserve place names.
- Test mixed-language inputs.
- Check right-to-left layout for Urdu.
- Avoid assuming literacy in a single script.
- Provide voice support where possible.

Test cases should cover:

- Telugu script
- Hindi script
- Urdu script
- Romanised Telugu
- Romanised Hindi
- Mixed Telugu-English
- Mixed Hindi-English
- Spelling mistakes
- Short incomplete complaints

Example:

```text
"drain block ayyindi near metro"
```

The system should preserve `metro`, classify the issue correctly, and ask for the precise location.

---

## 11. Computer-Vision Dataset Guidelines

Only use images with clear usage rights.

Before adding images:

- Record the dataset source.
- Check the licence.
- Remove identifiable faces and vehicle number plates where possible.
- Avoid private residential details.
- Remove embedded GPS metadata unless required.
- Use consistent labels.
- Add negative examples.

Initial labels:

```text
garbage_heap
blocked_drain
stagnant_water
pothole
construction_debris
open_manhole
```

A model prediction is not verified evidence. It should be described as a preliminary observation.

---

## 12. Privacy Guidelines

Do not commit:

- Phone numbers
- Email addresses
- Exact home addresses
- Unblurred identity documents
- Faces without permission
- Vehicle number plates
- Private API keys
- Access tokens
- Real complaint data without anonymisation

For demos, use fictional names and sample locations.

---

## 13. Testing Guidelines

### Frontend tests

Test:

- Form validation
- Language selection
- GPS-permission failure
- Photo-upload errors
- Mobile layouts
- Urdu right-to-left layout

### Backend tests

Test:

- Complaint submission
- Missing fields
- Duplicate search
- Invalid category handling
- Translation service failure
- LLM response parsing
- Status updates

### AI tests

Maintain a small evaluation dataset with:

- Input complaint
- Expected category
- Expected subcategory
- Expected missing fields
- Expected language
- Expected preserved landmarks

---

## 14. Reporting Bugs

Include:

- Problem summary
- Steps to reproduce
- Expected result
- Actual result
- Screenshots or logs
- Browser and device
- Language selected
- Whether GPS, image upload, or speech input was used

Do not include API keys or private citizen information.

---

## 15. Suggesting Features

A feature request should explain:

- Civic problem
- Target user
- Proposed workflow
- Expected impact
- Minimum proof-of-concept scope
- Data requirements
- Privacy concerns
- AI limitations
- Whether a non-AI solution would be simpler

---

## 16. Review Priorities

Pull requests are reviewed based on:

1. Civic usefulness
2. User accessibility
3. Data privacy
4. Simplicity
5. Reliability
6. AI safety
7. Test coverage
8. Documentation quality

---

## 17. Questions

Open a Git issue with the label `question` for technical or contribution-related questions.
