# EVision Setup Guide

This guide will walk you through setting up EVision from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Google OAuth Setup](#google-oauth-setup)
3. [Database Setup](#database-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Running with Docker](#running-with-docker)
7. [Data Collection](#data-collection)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
- **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
- **PostgreSQL 14+**: Download from [postgresql.org](https://www.postgresql.org/download/)
- **Git**: Download from [git-scm.com](https://git-scm.com/)

### Optional
- **Docker & Docker Compose**: For containerized deployment
- **Redis**: For caching and task queues

## Google OAuth Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "New Project"
   - Name it "EVision" and create

2. **Enable Google+ API**
   - In your project, go to "APIs & Services" → "Library"
   - Search for "Google+ API"
   - Click and enable it

3. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     ```
     http://localhost:3000/login
     http://localhost:3000/auth/callback
     ```
   - Click "Create"
   - Copy the Client ID and Client Secret

## Database Setup

### PostgreSQL Installation

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE evision;
CREATE USER evision WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE evision TO evision;
\q
```

## Backend Setup

1. **Clone and Navigate**
```bash
git clone <repository-url>
cd EVision/backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
DATABASE_URL=postgresql://evision:your_password@localhost:5432/evision
SECRET_KEY=generate-a-random-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback
```

To generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

5. **Initialize Database**
```bash
# Create tables
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

6. **Run Backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs to see the API documentation.

## Frontend Setup

1. **Navigate to Frontend**
```bash
cd ../frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Configure Environment**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

4. **Run Frontend**
```bash
npm run dev
```

Visit http://localhost:3000

## Running with Docker

The easiest way to run EVision is using Docker Compose:

1. **Configure Environment Files**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local
```

2. **Build and Run**
```bash
docker-compose up --build
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on port 8000
- Frontend on port 3000

3. **Stop Services**
```bash
docker-compose down
```

## Data Collection

### Setting Up The Odds API (Optional)

1. Sign up at [The Odds API](https://the-odds-api.com/)
2. Get your free API key (500 requests/month)
3. Add to `backend/.env`:
```env
ODDS_API_KEY=your-api-key
```

### Running Scrapers

Create a script to run scrapers periodically:

```python
# backend/scripts/collect_data.py
from app.scraping.kalshi import KalshiScraper
from app.scraping.sportsbooks import TheOddsAPIScraper
from app.core.database import SessionLocal

def collect_data():
    db = SessionLocal()

    # Scrape Kalshi
    kalshi_scraper = KalshiScraper()
    kalshi_markets = kalshi_scraper.scrape_sports_markets()
    kalshi_scraper.save_markets_to_db(db, kalshi_markets)

    # Scrape sportsbooks
    odds_scraper = TheOddsAPIScraper(api_key='your-api-key')
    for sport in ['americanfootball_nfl', 'basketball_nba']:
        odds = odds_scraper.scrape_sport_odds(sport)
        # Save to database

    db.close()

if __name__ == "__main__":
    collect_data()
```

Run it:
```bash
python scripts/collect_data.py
```

### Schedule Data Collection

Use cron (Linux/macOS) or Task Scheduler (Windows):

```bash
# Crontab entry - run every hour
0 * * * * cd /path/to/EVision/backend && python scripts/collect_data.py
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Test connection: `psql -h localhost -U evision -d evision`

### Google OAuth Error
- Verify Client ID in both backend and frontend .env
- Check redirect URIs in Google Console
- Ensure they match exactly (including http/https)

### Module Not Found
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### CORS Errors
- Verify ALLOWED_ORIGINS in backend/.env includes frontend URL
- Check that both services are running

## Next Steps

1. Create your first user by logging in with Google
2. Run the data collection script
3. Check the dashboard for EV opportunities
4. Configure automated data collection
5. Set up monitoring and alerts

For more information, see the main README.md
