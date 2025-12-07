# Job Market Analysis Setup Guide

This guide explains how to set up the job market analysis feature for the Course Validator.

## Overview

The job market analysis feature searches real job listings to provide insights about:
- Number of relevant job openings
- Average salaries for the skill
- Most common job titles
- Required skills employers are looking for
- Market growth trends

## API Provider: Adzuna

We use **Adzuna API** which provides:
- ✅ Free tier available (250 calls/month)
- ✅ Official API with good documentation
- ✅ Coverage: US, UK, Germany, Australia, Canada, France, and more
- ✅ Salary data included
- ✅ No complex authentication

## Setup Instructions

### Step 1: Get Adzuna API Credentials

1. Visit [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Click "Register for an API Key"
3. Fill out the registration form (it's free!)
4. You'll receive:
   - **App ID** (like: `12345678`)
   - **API Key** (like: `abcdef1234567890abcdef1234567890`)

### Step 2: Add Credentials to Your `.env` File

Create or update your `.env` file in the project root:

```bash
# Job Market API Settings (Adzuna)
ADZUNA_APP_ID=your_app_id_here
ADZUNA_API_KEY=your_api_key_here
JOB_SEARCH_COUNTRY=us  # Options: us, gb, de, au, ca, fr, etc.
MAX_JOBS_TO_ANALYZE=100
```

### Step 3: Test the Feature

Run your FastAPI server and test the endpoint:

```bash
# Start the server
uvicorn src.app.main:app --reload

# Test with curl or Postman
curl -X POST "http://localhost:8000/api/ideas/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Python for data science course"}'
```

## Configuration Options

### Country Codes

Set `JOB_SEARCH_COUNTRY` to one of:
- `us` - United States
- `gb` - United Kingdom
- `de` - Germany
- `au` - Australia
- `ca` - Canada
- `fr` - France
- `nl` - Netherlands
- `br` - Brazil
- `in` - India
- `pl` - Poland

### Rate Limits

**Free Tier:**
- 250 API calls per month
- No credit card required

**Paid Plans:**
- Standard: 2,500 calls/month - $99/month
- Professional: 25,000 calls/month - $499/month

Our implementation includes:
- ✅ Automatic retry with exponential backoff
- ✅ Rate limit handling
- ✅ Graceful degradation (continues without job data if API fails)

## How It Works

### 1. Keyword Extraction
The LLM extracts:
```json
{
  "job_titles": ["Data Analyst", "Data Scientist", "Business Analyst"],
  "job_search_terms": ["Python", "data analysis", "pandas", "SQL"]
}
```

### 2. Job Search
- Searches Adzuna for each job title
- Fetches up to 50 jobs per title
- Deduplicates results
- Limits to `MAX_JOBS_TO_ANALYZE` total

### 3. Relevance Filtering
Keeps only jobs that mention:
- 2+ of the `job_search_terms`, OR
- 1+ term + the main topic

### 4. Metrics Extraction
Analyzes relevant jobs to extract:
- Total count
- Average salary
- Top job titles
- Required skills frequency
- Growth trend

### 5. Scoring
Calculates job demand score (0-100) based on:
- **40%** Job Volume
- **30%** Salary Premium  
- **20%** Skill Relevance
- **10%** Growth Trend

## Response Structure

When job market data is available, the API response includes:

```json
{
  "idea": "Python for data science course",
  "demand_score": 75,
  "competition_score": 65,
  "good_idea_score": 72,
  "job_market": {
    "total_jobs_found": 147,
    "job_demand_score": 85,
    "avg_salary": 78500.0,
    "top_job_titles": [
      "Data Analyst",
      "Business Analyst",
      "Junior Data Scientist"
    ],
    "required_skills": [
      "Python",
      "SQL",
      "Excel",
      "pandas",
      "Tableau"
    ],
    "growth_trend": "growing"
  }
}
```

## Running Without Job Market API

The system is designed to work without job market credentials:

- ✅ If credentials are not set, job analysis is **skipped**
- ✅ The API continues to work with Google Trends data
- ✅ The `job_market` field will be `null` in responses
- ✅ Viability score falls back to trends + competition only

## Troubleshooting

### "Job market analysis will be skipped"
**Cause:** API credentials not configured  
**Solution:** Add `ADZUNA_APP_ID` and `ADZUNA_API_KEY` to `.env`

### "Rate limit exceeded"
**Cause:** Exceeded 250 calls/month (free tier)  
**Solution:** Wait for monthly reset or upgrade to paid plan

### "No jobs found"
**Cause:** Topic too niche or poor keyword extraction  
**Solution:** This is expected for very niche topics; not an error

### Jobs seem irrelevant
**Cause:** Filtering may need tuning  
**Solution:** Adjust the relevance threshold in `_filter_relevant_jobs()` method

## Future Enhancements

Planned improvements:
- [ ] Cache job data for 24 hours to reduce API calls
- [ ] Add MongoDB/Redis caching
- [ ] Compare current data with historical trends
- [ ] Support additional job APIs (LinkedIn, Indeed, etc.)
- [ ] Add geographic filtering
- [ ] Track job market changes over time

## API Documentation

Full Adzuna API docs: https://api.adzuna.com/v1/doc/

## Support

If you encounter issues:
1. Check `.env` file has correct credentials
2. Verify country code is valid
3. Check API rate limits haven't been exceeded
4. Review logs for detailed error messages

For Adzuna API support: support@adzuna.com


