# Course Validator

Validate course ideas and help creators sharpen their ideas into better ones.

## Features

### ✅ Implemented
- **Keyword Extraction**: AI-powered topic and keyword analysis using OpenAI
- **Google Trends Analysis**: Market demand analysis using real search trends
- **Job Market Analysis**: Real job listing data from Adzuna API
  - Job demand scoring
  - Salary insights
  - Required skills identification
  - Growth trend analysis
- **Viability Scoring**: Combined score from trends, jobs, and competition
- **Content Gap Analysis**: Smart suggestions based on market data

### 🚧 In Progress
- Marketplace competition analysis (Udemy, Coursera, etc.)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up environment variables:**
   Create a `.env` file with:
   ```bash
   OPENAI_API_KEY=your_key_here
   ADZUNA_APP_ID=your_app_id     # Optional - for job market data
   ADZUNA_API_KEY=your_api_key   # Optional - for job market data
   ```

3. **Run the server:**
   ```bash
   uvicorn src.app.main:app --reload
   ```

4. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/api/ideas/analyze" \
     -H "Content-Type: application/json" \
     -d '{"user_input": "Python for data science course"}'
   ```

## Job Market Feature Setup

The job market analysis feature is **optional** but highly recommended for better insights.

📖 See [SETUP_JOB_MARKET.md](./SETUP_JOB_MARKET.md) for detailed setup instructions.

**Quick setup:**
1. Get free API credentials at [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Add to `.env`: `ADZUNA_APP_ID` and `ADZUNA_API_KEY`
3. That's it! Job market data will now be included in responses

## API Response Example

```json
{
  "idea": "Python for data science course",
  "demand_score": 75,
  "competition_score": 65,
  "good_idea_score": 78,
  "content_gap_hint": "Most in-demand skills: Python, SQL, pandas",
  "summary": "Main topic: Python for Data Science...",
  "job_market": {
    "total_jobs_found": 147,
    "job_demand_score": 85,
    "avg_salary": 78500.0,
    "top_job_titles": ["Data Analyst", "Data Scientist"],
    "required_skills": ["Python", "SQL", "pandas", "Tableau"],
    "growth_trend": "growing"
  }
}
```

## Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB
- **AI**: OpenAI GPT
- **Data Sources**: 
  - Google Trends (via pytrends)
  - Adzuna Job API
- **Python**: 3.12+

## Project Structure

```
src/
├── app/
│   ├── models/       # Pydantic models
│   ├── routes/       # API endpoints
│   └── services/     # Business logic
│       ├── keyword_extraction.py   # OpenAI integration
│       ├── google_trends.py        # Trends analysis
│       ├── job_market.py           # Job market analysis
│       └── course_analyzer.py      # Main orchestrator
├── core/
│   └── config.py     # Settings and env vars
└── README.md
```

## Contributing

This is an MVP in active development. More features coming soon!
