# ASSA Event Management Platform

**Portfolio code sample · Python / Flask / SQLAlchemy / SQLite**

## Overview
A Flask web application for browsing and managing events, registering and signing in, making bookings, issuing ticket views, collecting feedback, and viewing administration information. The codebase includes optional components for event recommendations, booking fraud scoring, and feedback sentiment. These optional modules should not be described as deployed or benchmarked without proof.

## Verified project features
- Flask Blueprints for auth, events, bookings, feedback, payments, admin, and site views.
- SQLAlchemy models for users, events, bookings, feedback, and fraud logs.
- Server-rendered templates and static CSS / JavaScript.
- Ticket and booking workflows; **payment flow is a mock/simulation**.
- Optional ML modules; may require extra dependencies, models, or training.

## Run locally (development only)
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # or create the file manually on Windows
python app.py
```
Open `http://127.0.0.1:5000`. SQLite is the default if `DATABASE_URL` is not set. `LOAD_ML_MODELS=0` avoids loading optional sentiment models for a lightweight preview. Dependencies and database version have not been integration-tested in this environment.

## Source and privacy notes
This package excludes `.env`, Git history, the local SQLite instance, and uploaded event images. **Never publish real API keys, secret values, account records, or unlicensed event imagery.** Because the uploaded source README pointed to an existing collaborator's GitHub repository, confirm permission and project ownership before publishing under another account; credit team contributors as applicable.

## What to include in a job portfolio
Explain Shravya's individual responsibilities accurately. Add genuine screenshots and observed test results after review.
