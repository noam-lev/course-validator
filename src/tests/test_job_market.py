"""
Quick test script for the job market analysis feature.
Run this to verify the implementation is working correctly.
"""

import asyncio
import sys
from src.app.models.idea import KeywordAnalysis
from src.app.services.job_market import job_market_service


async def test_job_market():
    """Test the job market service with sample data."""
    
    print("=" * 60)
    print("Job Market Analysis - Test Script")
    print("=" * 60)
    
    # Check if API credentials are configured
    if not job_market_service._api_available:
        print("\n❌ Adzuna API credentials not configured")
        print("\nTo enable job market analysis:")
        print("1. Get free credentials at: https://developer.adzuna.com/")
        print("2. Add to .env file:")
        print("   ADZUNA_APP_ID=your_app_id")
        print("   ADZUNA_API_KEY=your_api_key")
        print("\n✅ System will work without it, but job_market will be null")
        return
    
    print("\n✅ Adzuna API credentials found")
    print(f"Country: {job_market_service.country}")
    print(f"Max jobs to analyze: {job_market_service.max_jobs}")
    
    # Test with sample keywords
    print("\n" + "-" * 60)
    print("Testing with: 'Python for Data Science Course'")
    print("-" * 60)
    
    sample_keywords = KeywordAnalysis(
        topic="Python for Data Science",
        subtopics=["pandas", "data visualization", "machine learning"],
        keywords=["learn python data science", "python for data analysis"],
        job_search_terms=["Python", "pandas", "data analysis", "SQL"],
        job_titles=["Data Analyst", "Data Scientist", "Business Analyst"]
    )
    
    print("\nExtracted Keywords:")
    print(f"  Job Titles: {sample_keywords.job_titles}")
    print(f"  Job Search Terms: {sample_keywords.job_search_terms}")
    
    print("\n⏳ Searching job market... (this may take 5-10 seconds)")
    
    try:
        result = await job_market_service.analyze_job_market(sample_keywords)
        
        if result:
            print("\n✅ Job Market Analysis Complete!")
            print("\nResults:")
            print(f"  📊 Total Jobs Found: {result.total_jobs_found}")
            print(f"  🎯 Job Demand Score: {result.job_demand_score}/100")
            print(f"  💰 Average Salary: ${result.avg_salary:,.2f}" if result.avg_salary else "  💰 Average Salary: N/A")
            print(f"  📈 Growth Trend: {result.growth_trend}")
            print(f"\n  🏆 Top Job Titles:")
            for i, title in enumerate(result.top_job_titles[:5], 1):
                print(f"     {i}. {title}")
            print(f"\n  🔧 Required Skills:")
            for i, skill in enumerate(result.required_skills[:5], 1):
                print(f"     {i}. {skill}")
            
            print("\n" + "=" * 60)
            print("✅ Test Successful - Job Market Feature is Working!")
            print("=" * 60)
        else:
            print("\n⚠️  No job market data returned (API may be unavailable)")
            print("System will continue to work with Google Trends data only")
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        print("\nThis could mean:")
        print("  - Invalid API credentials")
        print("  - Rate limit exceeded")
        print("  - Network connectivity issues")
        print("  - API service is down")
        print("\nCheck logs for more details")
        sys.exit(1)


if __name__ == "__main__":
    print("\n🚀 Starting test...")
    asyncio.run(test_job_market())
    print("\n✨ Test complete!\n")

