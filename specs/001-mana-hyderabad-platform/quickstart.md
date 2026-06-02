# Quickstart: Spec Kit for Mana Hyderabad

## Optional CLI Installation

Spec Kit uses the `specify` CLI. Install it only if you want local slash-command workflow support:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Replace `vX.Y.Z` with the release your team standardizes on.

## Current Artifacts

- Constitution: `.specify/memory/constitution.md`
- Baseline spec: `specs/001-mana-hyderabad-platform/spec.md`
- Technical plan: `specs/001-mana-hyderabad-platform/plan.md`
- Tasks: `specs/001-mana-hyderabad-platform/tasks.md`
- Data model: `specs/001-mana-hyderabad-platform/data-model.md`
- Research notes: `specs/001-mana-hyderabad-platform/research.md`

## Future Phase Workflow

For each new phase:

1. Create `specs/00X-feature-name/spec.md`.
2. Write WHAT and WHY first.
3. Add technical choices in `plan.md`.
4. Break work into `tasks.md`.
5. Run relevant checks after implementation.

## Validation

```bash
npm run format:check
npm run build
cd mana-hyderabad-backend
.venv/bin/pytest
```
