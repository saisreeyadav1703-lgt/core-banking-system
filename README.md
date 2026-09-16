# Core Banking System — Real-time Transaction Dashboard

A full-stack real-time banking application with a live web dashboard, REST API, SQLite database, and complete DevOps pipeline.

## Live Features
- Real-time transaction dashboard (auto-refreshes every 3 seconds)
- Create credit/debit transactions via web UI or API
- Live account balance tracking
- CI/CD pipeline status display
- AWS CloudWatch metrics simulation

## Tech Stack
| Layer | Tools |
|---|---|
| Frontend | HTML, CSS, JavaScript (real-time fetch polling) |
| Backend | Python Flask + Gunicorn |
| Database | SQLite (persistent Docker volume) |
| Container | Docker + Docker Compose |
| CI/CD | Jenkins + GitHub Actions |
| Cloud | AWS EC2, S3, CloudWatch |

## Quick Start (Windows)

```powershell
git clone https://github.com/saisreeyadav1703-lgt/core-banking-system.git
cd core-banking-system
docker compose up -d
```

Open browser: http://localhost:8080

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Health check |
| GET | /api/stats | Dashboard statistics |
| GET | /api/accounts | All account balances |
| GET | /api/transactions | All transactions |
| POST | /api/transactions | Create new transaction |
| GET | /api/transactions/:id | Single transaction |

## Stop the app
```powershell
docker compose down
```

*Project by Yadava Saisree — AI Engineer | DevOps Intern Candidate*
