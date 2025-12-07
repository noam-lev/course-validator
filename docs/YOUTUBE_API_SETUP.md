# YouTube Data API Setup Guide

This guide will help you set up the YouTube Data API to enable real course competition analysis using YouTube educational content.

## Why YouTube API?

- ✅ **Free**: 10,000 quota units per day (enough for ~100 searches)
- ✅ **Official**: Google's official API, stable and reliable
- ✅ **No scraping**: No Cloudflare challenges or anti-bot issues
- ✅ **Rich data**: Views, likes, duration, channel info, etc.
- ✅ **Fast**: Direct API access, no browser automation needed

## Step-by-Step Setup

### 1. Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 2. Create or Select a Project

- Click the project dropdown at the top
- Click "New Project"
- Give it a name (e.g., "Course Validator")
- Click "Create"

### 3. Enable YouTube Data API v3

- In the search bar, type "YouTube Data API v3"
- Click on "YouTube Data API v3"
- Click "ENABLE"

### 4. Create API Credentials

- Go to "Credentials" in the left sidebar
- Click "Create Credentials" → "API Key"
- Your API key will be generated
- **IMPORTANT**: Copy this key immediately

### 5. (Optional) Restrict Your API Key

For security, you can restrict the API key:
- Click on your API key to edit it
- Under "API restrictions":
  - Select "Restrict key"
  - Choose "YouTube Data API v3"
- Under "Application restrictions" (optional):
  - Set IP restrictions if you want
- Click "Save"

### 6. Add API Key to Your Environment

#### Option A: .env File (Recommended for development)

Add to your `.env` file:
```
YOUTUBE_API_KEY=your_api_key_here
```

#### Option B: Environment Variable (For production)

**Windows:**
```powershell
$env:YOUTUBE_API_KEY="your_api_key_here"
```

**Linux/Mac:**
```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

### 7. Restart Your Server

If your server is already running, restart it to pick up the new environment variable:

```bash
# Stop the server (Ctrl+C)
# Then restart:
uv run python -m uvicorn src.app.main:app --reload
```

## Testing Your Setup

### Quick Test Script

Create a file `test_youtube_api.py`:

```python
import asyncio
from src.app.services.market_competition import YouTubeAPIScraper

async def test():
    scraper = YouTubeAPIScraper()
    courses = await scraper.fetch_courses("python programming")
    
    print(f"\n✅ Found {len(courses)} YouTube videos!")
    if courses:
        print("\nSample:")
        for course in courses[:3]:
            print(f"  - {course.title}")
            print(f"    Views: {course.student_count:,}")
            print(f"    Channel: {course.instructor}")
            print()

asyncio.run(test())
```

Run it:
```bash
uv run python test_youtube_api.py
```

### Test via API Endpoint

```bash
curl -X POST http://localhost:8000/api/ideas/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_input": "python for beginners"}'
```

Check the logs - you should see:
```
INFO: YouTube API key found - using YouTube Data API for competition analysis
INFO: Searching YouTube for: python for beginners tutorial course
INFO: Found 20 YouTube videos for: python for beginners
```

## API Quota Information

YouTube Data API has a quota of **10,000 units per day**.

**Quota costs:**
- Search request: 100 units
- Video details request: 1 unit per video

**Example calculation:**
- 1 search (100 units) + 20 video details (20 units) = 120 units
- You can perform ~83 topic searches per day
- More than enough for development and moderate production use

## Troubleshooting

### "YouTube API key not configured"

- Check your `.env` file has `YOUTUBE_API_KEY=...`
- Make sure you restarted the server after adding the key
- Verify the environment variable is set: `echo $env:YOUTUBE_API_KEY` (Windows) or `echo $YOUTUBE_API_KEY` (Linux/Mac)

### "YouTube API quota exceeded"

- You've used your 10,000 daily quota
- Wait until midnight Pacific Time for quota reset
- Consider caching results to reduce API calls

### "Invalid API key"

- Double-check you copied the full API key
- Make sure YouTube Data API v3 is enabled in your Google Cloud project
- Verify API key restrictions aren't blocking your requests

## Cost

✅ **FREE** for up to 10,000 quota units per day

If you need more quota, you can request an increase from Google (usually approved for legitimate use cases).

## Alternative: Use Mock Data

If you don't want to set up YouTube API right now, the system will automatically fall back to mock data. You'll still be able to test the full system!

To explicitly use mock data, simply don't set `YOUTUBE_API_KEY`.

## Next Steps

Once YouTube API is working, you can:
- Add additional scrapers (Coursera, edX, etc.)
- Implement caching to reduce API calls
- Add more platforms to the MarketCompetitionService


