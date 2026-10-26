# ARPINIA ODYSSEY — DEVELOPMENT RULES

## 1. Environment Constraints
- **Containerization:** Docker Desktop is mandatory.
- **Backend:** Python 3.11, FastAPI.
- **Frontend:** Node 22 LTS, Next.js.
- **Database:** PostgreSQL + PostGIS extension.
- **Message Broker:** Redis.

## 2. Git & PR Discipline
- **Main Branch:** `main` is protected. Direct pushes are forbidden.
- **Two-Person Rule:** All Pull Requests require at least one approving review from a different Pod member before merging.
- **No Force Pushing:** `git push -f` is forbidden on shared branches.

## 3. Data Discipline
- Never commit large datasets (SAR `.zip`, ERA5 `.nc`) to Git.
- Use `manifest.json` and tracking mechanisms.
- Keep `ground_truth.json` strictly isolated from inference logic.
