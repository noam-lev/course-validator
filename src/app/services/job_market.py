import httpx
import logging
from typing import List, Dict, Any, Optional
from ..models.idea import KeywordAnalysis, JobMarketData
from ...core.config import settings
import time

logger = logging.getLogger(__name__)


class JobMarketService:
    """
    Service to analyze job market demand for course topics using Adzuna API.
    Searches for relevant jobs and extracts insights about demand, salaries, and skills.
    """
    
    def __init__(self, max_retries: int = 3):
        """Initialize Job Market service with API configuration."""
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.app_id = settings.ADZUNA_APP_ID
        self.api_key = settings.ADZUNA_API_KEY
        self.country = settings.JOB_SEARCH_COUNTRY
        self.max_jobs = settings.MAX_JOBS_TO_ANALYZE
        self.max_retries = max_retries
        self.retry_delay = 2
        
        # Check if API credentials are configured
        logger.info(f"Initializing JobMarketService with app_id: {'SET' if self.app_id else 'NOT SET'}, api_key: {'SET' if self.api_key else 'NOT SET'}")
        
        if not self.app_id or not self.api_key:
            logger.warning("Adzuna API credentials not configured. Job market analysis will be skipped.")
            self._api_available = False
        else:
            logger.info("Adzuna credentials found, enabling job market analysis")
            self._api_available = True
    
    async def analyze_job_market(self, keywords: KeywordAnalysis) -> Optional[JobMarketData]:
        """
        Perform complete job market analysis for a course topic.
        
        Args:
            keywords: KeywordAnalysis with job_titles and job_search_terms
            
        Returns:
            JobMarketData with job market insights, or None if API unavailable
        """
        if not self._api_available:
            logger.info("Skipping job market analysis - API not configured")
            return None
        
        logger.info(f"Starting job market analysis for topic: {keywords.topic}")
        logger.info(f"Job titles to search: {keywords.job_titles}")
        logger.info(f"Job search terms: {keywords.job_search_terms}")
        
        try:
            # Step 1: Search for jobs using job titles
            logger.info("Step 1: Searching jobs by titles...")
            all_jobs = await self._search_all_jobs(keywords)
            
            if not all_jobs:
                logger.warning("No jobs found for any of the job titles")
                logger.info("Job search results by title:")
                for title in keywords.job_titles[:3]:
                    logger.info(f"- {title}: 0 jobs")
                return self._create_empty_result()
            
            # Step 2: Filter relevant jobs based on job_search_terms
            logger.info(f"Step 2: Filtering {len(all_jobs)} jobs for relevance...")
            relevant_jobs = self._filter_relevant_jobs(all_jobs, keywords)
            
            if not relevant_jobs:
                logger.warning("No relevant jobs found after filtering")
                logger.info("Filtering details:")
                logger.info(f"- Total jobs before filter: {len(all_jobs)}")
                logger.info(f"- Search terms used: {keywords.job_search_terms}")
                logger.info("- Filter criteria: 2+ term matches OR 1 term + topic match")
                return self._create_empty_result()
            
            # Step 3: Extract metrics from relevant jobs
            metrics = self._extract_job_metrics(relevant_jobs, keywords)
            
            # Step 4: Calculate job demand score
            job_demand_score = self._calculate_job_demand_score(metrics, relevant_jobs)
            
            # Step 5: Build and return JobMarketData
            return JobMarketData(
                total_jobs_found=len(relevant_jobs),
                job_demand_score=job_demand_score,
                avg_salary=metrics.get('avg_salary'),
                top_job_titles=metrics['top_job_titles'],
                required_skills=metrics['required_skills'],
                growth_trend=metrics['growth_trend']
            )
            
        except Exception as e:
            logger.error(f"Error in job market analysis: {str(e)}")
            return None
    
    async def _search_all_jobs(self, keywords: KeywordAnalysis) -> List[Dict[str, Any]]:
        """
        Search for jobs using job titles from keywords.
        
        Args:
            keywords: KeywordAnalysis with job_titles
            
        Returns:
            List of job postings
        """
        all_jobs = []
        seen_job_ids = set()
        jobs_per_title = {}  # Track jobs found per title
        
        # Search by each job title (limit to top 3 to avoid too many API calls)
        for job_title in keywords.job_titles[:3]:
            try:
                logger.info(f"Searching for jobs with title: {job_title}")
                jobs = await self._search_jobs_by_query(job_title)
                jobs_per_title[job_title] = len(jobs)
                
                # Deduplicate jobs
                new_jobs = 0
                for job in jobs:
                    job_id = job.get('id')
                    if job_id and job_id not in seen_job_ids:
                        all_jobs.append(job)
                        seen_job_ids.add(job_id)
                        new_jobs += 1
                
                logger.info(f"- Found {len(jobs)} jobs, {new_jobs} unique")
                
                # Small delay to avoid rate limiting
                time.sleep(0.3)
                
            except Exception as e:
                logger.warning(f"Failed to search jobs for '{job_title}': {str(e)}")
                jobs_per_title[job_title] = 0
                continue
        
        logger.info(f"Found {len(all_jobs)} total jobs before filtering")
        return all_jobs[:self.max_jobs]  # Limit total jobs
    
    async def _search_jobs_by_query(self, query: str, results_per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Search Adzuna API for jobs matching the query.
        
        Args:
            query: Search query string
            results_per_page: Number of results to fetch
            
        Returns:
            List of job postings from API
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    url = f"{self.base_url}/{self.country}/search/1"
                    
                    params = {
                        'app_id': self.app_id,
                        'app_key': self.api_key,
                        'what': query,
                        'results_per_page': results_per_page,
                        'sort_by': 'date',  # Get most recent jobs
                    }
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    jobs = data.get('results', [])
                    
                    logger.info(f"Found {len(jobs)} jobs for query: '{query}'")
                    return jobs
                    
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP error {e.response.status_code}"
                logger.warning(f"Attempt {attempt + 1} failed for '{query}': {last_error}")
                
                if e.response.status_code == 429:  # Rate limit
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Rate limited, waiting {delay}s before retry")
                    time.sleep(delay)
                    continue
                else:
                    break  # Don't retry other HTTP errors
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed for '{query}': {last_error}")
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
        
        logger.error(f"All retries failed for '{query}': {last_error}")
        return []
    
    def _filter_relevant_jobs(self, jobs: List[Dict[str, Any]], keywords: KeywordAnalysis) -> List[Dict[str, Any]]:
        """
        Filter jobs to keep only those relevant to the course topic.
        
        Args:
            jobs: List of all job postings
            keywords: KeywordAnalysis with job_search_terms and topic
            
        Returns:
            Filtered list of relevant jobs
        """
        relevant_jobs = []
        term_match_counts = {0: 0, 1: 0, 2: 0, 3: 0, '4+': 0}  # Track match distribution
        
        # Normalize search terms for matching
        search_terms_lower = [term.lower() for term in keywords.job_search_terms]
        topic_lower = keywords.topic.lower()
        
        logger.info("Filtering jobs with search terms:")
        for term in search_terms_lower:
            logger.info(f"- {term}")
        
        for job in jobs:
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            
            # Count how many search terms appear in title or description
            term_matches = sum(
                1 for term in search_terms_lower
                if term in title or term in description
            )
            
            # Track match distribution
            if term_matches >= 4:
                term_match_counts['4+'] += 1
            else:
                term_match_counts[term_matches] += 1
            
            # Also check if topic appears
            topic_match = topic_lower in title or topic_lower in description
            
            # Keep job if it matches at least 2 search terms, or 1 term + topic
            if term_matches >= 2 or (term_matches >= 1 and topic_match):
                relevant_jobs.append(job)
                if term_matches >= 2:
                    logger.debug(f"Keeping job '{title}' with {term_matches} term matches")
                else:
                    logger.debug(f"Keeping job '{title}' with topic match + {term_matches} term match")
        
        logger.info(f"Filtered to {len(relevant_jobs)} relevant jobs from {len(jobs)} total")
        return relevant_jobs
    
    def _extract_job_metrics(self, jobs: List[Dict[str, Any]], keywords: KeywordAnalysis) -> Dict[str, Any]:
        """
        Extract useful metrics from job postings.
        
        Args:
            jobs: List of relevant job postings
            keywords: KeywordAnalysis for context
            
        Returns:
            Dictionary of metrics
        """
        salaries = []
        job_titles = {}
        skills_mentioned = {}
        
        # Extract data from each job
        for job in jobs:
            # Extract salary
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            if salary_min and salary_max:
                avg_salary = (salary_min + salary_max) / 2
                salaries.append(avg_salary)
            
            # Count job titles
            title = job.get('title', 'Unknown')
            job_titles[title] = job_titles.get(title, 0) + 1
            
            # Count mentions of our search terms in descriptions
            description = job.get('description', '').lower()
            for term in keywords.job_search_terms:
                if term.lower() in description:
                    skills_mentioned[term] = skills_mentioned.get(term, 0) + 1
        
        # Calculate average salary
        avg_salary = sum(salaries) / len(salaries) if salaries else None
        
        # Get top 5 job titles
        top_job_titles = sorted(job_titles.items(), key=lambda x: x[1], reverse=True)[:5]
        top_job_titles = [title for title, _ in top_job_titles]
        
        # Get top 5 required skills
        top_skills = sorted(skills_mentioned.items(), key=lambda x: x[1], reverse=True)[:5]
        required_skills = [skill for skill, _ in top_skills]
        
        # Determine growth trend (simplified - based on job volume)
        growth_trend = self._determine_growth_trend(len(jobs))
        
        return {
            'avg_salary': avg_salary,
            'top_job_titles': top_job_titles,
            'required_skills': required_skills,
            'growth_trend': growth_trend
        }
    
    def _determine_growth_trend(self, job_count: int) -> str:
        """
        Determine growth trend based on number of jobs found.
        This is a simplified heuristic - in a production system, 
        you'd compare current data with historical data.
        
        Args:
            job_count: Number of relevant jobs found
            
        Returns:
            Growth trend: "growing", "stable", or "declining"
        """
        # Simple heuristic based on job volume
        if job_count >= 50:
            return "growing"
        elif job_count >= 20:
            return "stable"
        else:
            return "declining"
    
    def _calculate_job_demand_score(self, metrics: Dict[str, Any], jobs: List[Dict[str, Any]]) -> int:
        """
        Calculate job demand score (0-100) based on various factors.
        
        Scoring breakdown:
        - Job Volume (40%): More jobs = higher demand
        - Salary Premium (30%): Higher salaries = higher demand
        - Skill Relevance (20%): More matching skills = better fit
        - Growth Trend (10%): Growing market = bonus
        
        Args:
            metrics: Extracted metrics
            jobs: List of relevant jobs
            
        Returns:
            Job demand score (0-100)
        """
        score = 0
        
        # 1. Job Volume Score (40 points max)
        job_count = len(jobs)
        if job_count >= 100:
            volume_score = 40
        elif job_count >= 50:
            volume_score = 35
        elif job_count >= 20:
            volume_score = 25
        elif job_count >= 10:
            volume_score = 15
        else:
            volume_score = max(5, job_count)  # Minimum 5 points if any jobs found
        
        score += volume_score
        
        # 2. Salary Premium Score (30 points max)
        avg_salary = metrics.get('avg_salary')
        if avg_salary:
            # Rough salary brackets (US market - adjust for other countries)
            if avg_salary >= 100000:
                salary_score = 30
            elif avg_salary >= 75000:
                salary_score = 25
            elif avg_salary >= 50000:
                salary_score = 20
            elif avg_salary >= 40000:
                salary_score = 15
            else:
                salary_score = 10
        else:
            salary_score = 15  # Neutral score if no salary data
        
        score += salary_score
        
        # 3. Skill Relevance Score (20 points max)
        required_skills_count = len(metrics.get('required_skills', []))
        skill_score = min(20, required_skills_count * 4)
        score += skill_score
        
        # 4. Growth Trend Bonus (10 points max)
        growth_trend = metrics.get('growth_trend', 'stable')
        if growth_trend == 'growing':
            trend_score = 10
        elif growth_trend == 'stable':
            trend_score = 6
        else:  # declining
            trend_score = 2
        
        score += trend_score
        
        # Ensure score is within 0-100 range
        return max(0, min(100, score))
    
    def _create_empty_result(self) -> JobMarketData:
        """Create an empty result when no jobs are found."""
        return JobMarketData(
            total_jobs_found=0,
            job_demand_score=0,
            avg_salary=None,
            top_job_titles=[],
            required_skills=[],
            growth_trend="declining"
        )


# Create singleton instance
job_market_service = JobMarketService()

