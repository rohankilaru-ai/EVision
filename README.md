# EVision - Sports Betting EV Calculator

EVision is a web application that identifies positive expected value (EV) opportunities in sports betting by comparing Kalshi prediction markets against sportsbook odds.

## 🎯 Features

### Free Tier
- Real-time EV opportunity detection
- Kalshi market vs sportsbook odds comparison
- Advanced vig removal algorithms
- Kelly Criterion bet sizing
- View opportunities with 2%+ edge
- Basic market statistics

### Paid Tier
- All free tier features
- Access to ALL EV opportunities (no minimum edge filter)
- Historical backtesting framework
- Advanced analytics and insights
- Priority data updates

## 🏗️ Architecture

### Backend (Python FastAPI)
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Database for storing market data
- **SQLAlchemy** - ORM for database operations
- **Google OAuth 2.0** - Authentication
- **Web Scraping** - BeautifulSoup, Selenium for data collection

### Frontend (Next.js 14)
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management

## 📊 How It Works

1. **Data Collection**: Scrapes Kalshi prediction markets and sportsbook odds from free sources
2. **Vig Removal**: Removes bookmaker margins to calculate true probabilities
3. **EV Calculation**: Identifies markets where Kalshi prices differ from true odds
4. **Kelly Sizing**: Calculates optimal bet sizes for long-term growth
5. **Backtesting**: Validates strategies with historical data

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for task queue)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up database:
```bash
# Create PostgreSQL database
createdb evision

# Run migrations
alembic upgrade head
```

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## 🔑 Configuration

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:3000/login`
   - `http://localhost:3000/auth/callback`
6. Copy Client ID and Client Secret to `.env` files

### Database Configuration

Update `backend/.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/evision
```

### API Keys (Optional)

For The Odds API (free tier):
1. Sign up at [The Odds API](https://the-odds-api.com/)
2. Get free API key
3. Add to environment variables

## 📈 Analytics Modules

### Probability Calculator
- American odds to implied probability conversion
- Decimal odds conversion
- Multiple vig removal methods:
  - Additive (standard normalization)
  - Multiplicative (equal vig assumption)
  - Power method (advanced)
- Consensus probability calculation

### EV Calculator
- Expected value calculation
- EV percentage (return on stake)
- Edge calculation

### Kelly Criterion
- Optimal bet sizing
- Fractional Kelly support (quarter, half)
- Bankroll safety caps

### Backtesting
- Historical performance analysis
- Win rate, ROI, Sharpe ratio
- Maximum drawdown tracking
- Regime analysis (by sport, edge size, etc.)
- Monte Carlo simulation

## 🔧 Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
black app/
flake8 app/

# Frontend linting
npm run lint
```

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Tech Stack

**Backend:**
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas, NumPy (analytics)
- BeautifulSoup, Selenium (scraping)
- Google OAuth

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- TanStack Query
- Zustand

## 📜 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This software is for educational and research purposes only. Sports betting involves risk. Always gamble responsibly and within your means. Past performance does not guarantee future results.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub