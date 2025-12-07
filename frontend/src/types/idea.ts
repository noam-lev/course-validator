export interface CourseIdeaRequest {
  user_input: string;
}

export interface CourseType {
  type: 'professional' | 'personal' | 'life_skills' | 'educational';
  description: string;
  focus_areas: string[];
}

export interface ScoreExplanation {
  demand: string;
  competition: string;
  good_idea: string;
}

export interface JobMarketData {
  total_jobs_found: number;
  job_demand_score: number;
  avg_salary?: number | null;
  top_job_titles: string[];
  required_skills: string[];
  growth_trend: 'growing' | 'stable' | 'declining';
}

export interface YouTubeAnalysis {
  total_videos_found: number;
  top_videos: CourseInfo[];
  avg_views?: number | null;
  avg_rating?: number | null;
  top_channels: string[];
  total_views: number;
  engagement_score: number;
}

export interface CourseInfo {
  title: string;
  price: number;
  student_count?: number | null;
  rating?: number | null;
  url: string;
  platform: string;
  instructor?: string | null;
  last_updated?: string | null;
  level?: string | null;
}

export interface CourseIdeaResponse {
  idea: string;
  course_type: CourseType;
  demand_score: string;
  competition_score: string;
  good_idea_score: string;
  score_explanations: ScoreExplanation;
  content_gap_hint?: string | null;
  summary: string;
  job_market?: JobMarketData | null;
  youtube_analysis?: YouTubeAnalysis | null;
  created_at: string;
}

