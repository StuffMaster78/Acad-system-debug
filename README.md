# Writing Project Monorepo

This repository now contains both the Django backend and the Vite/Vue frontend in a single Git history.

## Repository Layout

```
writing_project/
├── backend/    # Django project (migrated from original writing_system_backend)
├── frontend/   # Vite/Vue SPA (migrated from writing_system_frontend)
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
└── README.md   # (this file)
```

- Backend specific docs, scripts, and env files all continue to live under `backend/`.
- Frontend retains its own README and tooling inside `frontend/`.
- Root-level compose files orchestrate both services together.

## Working on the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend README and all previous documentation are still available inside `backend/README.md` (and the various `*.md` files that were moved under `backend/`).

## Working on the Frontend

```bash
cd frontend
npm install
npm run dev
```

See `frontend/README.md` for more detailed SPA instructions.

## Running Everything with Docker

From the repository root:

```bash
docker compose up --build
```

The compose files expect the backend service context to be `./backend` and frontend to be `./frontend`.

## Git Tips

- Work from the repo root (`writing_project/`).
- Backend code lives under `backend/…`; frontend under `frontend/…`.
- CI/CD or deployment scripts that referenced the old root paths should be updated to include the new directory prefix.
