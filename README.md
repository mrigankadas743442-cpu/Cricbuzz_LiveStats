# 🏏 Cricbuzz LiveStats - Cricket Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![SQLite](https://img.shields.io/badge/SQLite-Database-green)
![Plotly](https://img.shields.io/badge/Plotly-Charts-purple)
![Tests](https://img.shields.io/badge/Tests-pytest-orange)

A cricket analytics platform that pulls live and historical data from the **Cricbuzz API**, stores it in a **SQLite** database and presents it through an interactive **Streamlit** dashboard with live scorecards, player statistics, 25 SQL analytics questions, full CRUD management and charts.

## 🚀 Live Demo
👉 **[Try Cricbuzz LiveStats](https://cricbuzzlivestats743442.streamlit.app)**

Open the dashboard, browse live matches, run SQL questions and explore the charts.



## 📌 Project Overview
Cricket produces a huge amount of data, but it is scattered across match pages and scorecards. This project collects that data, cleans it and stores it in a relational database so that it can be queried, visualised and managed from one place.

The app is built in layers (pages → services → API / database), so the user interface, business logic and data access stay separate and easy to test.

## 🎯 Problem Statement
Raw cricket data is hard to analyse directly. The objective of this project is to build an end-to-end data application that can:

- Fetch live match data and scorecards from a REST API
- Store clean, structured data in a relational database
- Answer analytical questions with SQL
- Let users view, add, edit and delete player records
- Turn results into charts

Such systems are useful for:
- Sports analytics
- Fantasy cricket research
- Performance tracking
- Learning SQL on real data

## ✨ Features
✅ Live and recent match list with full scorecards

✅ Top player statistics (runs, wickets, averages, strike rates) by format

✅ **25 SQL analytics questions** (beginner → advanced) with SQL shown for each

✅ Custom read-only SQL runner with CSV download

✅ Player Management (create, read, update, delete) with validation

✅ Interactive charts (bar, line, pie, scatter) built with Plotly

✅ Quota-safe **raw cache**, so the app keeps working when the daily API limit is used up

✅ Error handling and rotating log files with friendly on-screen messages

✅ Automated tests with pytest

## 📄 Pages
| Page | What it does |
|---|---|
| 🏠 Dashboard | Database totals and project overview |
| 🏏 Live Matches | Live, recent and upcoming matches with scorecards |
| 📊 Top Player Stats | Leaderboards by format and category, with a chart |
| 🔎 SQL Analytics | 25 curated questions plus a custom read-only SQL box |
| 🛠️ Player Management | Add, edit, search and delete players |
| 📈 Charts & Trends | Four chart tabs built from the database |
| ⚙️ Settings | App and data settings |

## 🛠️ Technologies Used
| Technology | Purpose |
|---|---|
| Python | Programming language |
| Streamlit | Web interface (multipage app) |
| SQLite | Relational database |
| Pandas | Data handling |
| Plotly | Interactive charts |
| Requests | Cricbuzz RapidAPI calls |
| Pytest | Automated testing |
| Jupyter Notebook | Data-fetching walkthrough |
| VS Code + Git/GitHub | Development and version control |
| Streamlit Community Cloud | Deployment |

## 🧠 Architecture
```
Cricbuzz RapidAPI
      │
      ▼
 Raw cache (api_cache.db)  ──►  Parsers  ──►  SQLite (cricket.db)
                                                    │
                                   Services (analytics, charts, CRUD)
                                                    │
                                          Streamlit pages (UI)
```

- **Raw cache first:** every API response is saved, so data is fetched once and reused.
- **Parameterised SQL** everywhere, with foreign keys enforced.
- **Custom errors and logging** so failures never show a raw traceback.

## 🗄️ Database Design
Main tables: `teams`, `venues`, `series`, `matches`, `innings`, `players`, `batting_scorecard`, `bowling_scorecard` and `player_career_stats`, linked with foreign keys.

Current dataset: about **119 real matches**, **450+ players with career statistics**, and thousands of scorecard rows.

## 📁 Project Structure
```
Cricbuzz_LiveStats/
├── app.py                  # Dashboard / entry point
├── pages/                  # Streamlit pages
├── services/               # Business logic (analytics, charts, ingestion, parsers)
├── api/                    # Cricbuzz API client
├── database/               # Connection and helpers
├── sql/
│   ├── schema.sql          # Table definitions
│   └── queries/            # The 25 analytics queries (q01 ... q25b)
├── scripts/                # Harvesting, cleanup and data-building scripts
├── tests/                  # Pytest suite
├── utils/                  # Logging, validation, UI helpers
├── data/cricket.db         # SQLite database
├── data_fetching.ipynb     # Data pipeline walkthrough
└── requirements.txt
```

## ⚙️ Installation
```bash
git clone https://github.com/mrigankadas743442-cpu/Cricbuzz_LiveStats.git
cd Cricbuzz_LiveStats
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file with your RapidAPI key:
```
RAPIDAPI_KEY=your-key-here
```

Run the app:
```bash
streamlit run app.py
```

## 🧪 Run the Tests
```bash
python -m pytest -v
```

## 📊 SQL Analytics Questions
The app includes 25 questions across three levels, for example:
- Players by country and role
- Highest scores and top run scorers by format
- Venues with the largest capacity
- Team win counts and toss decisions
- All-rounders with 1000+ runs and 50+ wickets
- Partnerships, bowling economy and consistency
- Quarterly batting trend and career phase (Q25)

> **Note on Q25:** the brief asks for quarterly trends over 6+ quarters. The free API tier provides only a few weeks of matches, so Q25 uses weekly periods and relaxed minimums on the live data. The original quarterly logic is verified on synthetic multi-year history in `tests/test_history_queries.py`. Other history-based questions (Q14, Q16, Q18, Q22-Q24) use relaxed minimums for the same reason, and each SQL file says so in its header comment.

## ⚠️ Known Limitations
- The free API tier limits daily calls, so only about two weeks of matches are loaded.
- Some player roles, batting styles and fielding statistics are not available from the scorecards.
- On Streamlit Community Cloud the file system is temporary, so Player Management edits do not persist after the app restarts.

## 🔮 Future Improvements
- Parse catches and stumpings from dismissal text for full fielding analysis
- Fill missing player countries and roles from player profiles
- Harvest more match history to enrich trend queries
- Move to a hosted database (PostgreSQL) so edits persist online
- Add team head-to-head and venue analysis pages
- Scheduled automatic data refresh

## 👨‍💻 Author
**Mriganka Das**

MCA Graduate | AI & Data Science Enthusiast

GitHub: https://github.com/mrigankadas743442-cpu
