import axiosClient from './axiosClient';
import type {
  CourseIdeaRequest,
  CourseIdeaResponse,
  CourseType,
  JobMarketData,
  ScoreExplanation,
  YouTubeAnalysis,
} from '../types/idea';
import { USE_MOCK_API } from '../config';

type ApiError = {
  message: string;
  detail?: string;
  status?: number;
};

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const mockResponse = (payload: CourseIdeaRequest): CourseIdeaResponse => {
  const now = new Date().toISOString();
  const course_type: CourseType = {
    type: 'professional',
    description: 'Professional upskilling course',
    focus_areas: ['skills', 'market-ready'],
  };
  const score_explanations: ScoreExplanation = {
    demand: 'Strong search and job volume signals demand.',
    competition: 'Moderate competition in marketplaces.',
    good_idea: 'Idea has clear audience and monetization path.',
  };
  const job_market: JobMarketData = {
    total_jobs_found: 142,
    job_demand_score: 78,
    avg_salary: 92000,
    top_job_titles: ['Instructor', 'Curriculum Designer', 'Content Strategist'],
    required_skills: ['Curriculum Design', 'SME Collaboration', 'Video Editing'],
    growth_trend: 'growing',
  };
  const youtube_analysis: YouTubeAnalysis = {
    total_videos_found: 85,
    top_videos: [],
    avg_views: 12000,
    avg_rating: 4.5,
    top_channels: ['LearnHub', 'SkillForge'],
    total_views: 550000,
    engagement_score: 72,
  };

  return {
    idea: payload.user_input,
    course_type,
    demand_score: '78',
    competition_score: '62',
    good_idea_score: '74',
    score_explanations,
    content_gap_hint:
      'Emphasize project-based modules and real-world case studies.',
    summary:
      'A professional course with strong demand and moderate competition. Focus on applied learning to differentiate.',
    job_market,
    youtube_analysis,
    created_at: now,
  };
};

export const analyzeIdea = async (
  payload: CourseIdeaRequest,
): Promise<CourseIdeaResponse> => {
  if (USE_MOCK_API) {
    await delay(800);
    return mockResponse(payload);
  }

  try {
    const { data } = await axiosClient.post<CourseIdeaResponse>(
      '/ideas/analyze',
      payload,
    );
    return data;
  } catch (error) {
    if (error && typeof error === 'object' && 'response' in error) {
      const err = error as any;
      const status = err.response?.status;
      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Request failed';
      const apiError: ApiError = { message, status };
      throw apiError;
    }
    throw { message: 'Network error' } as ApiError;
  }
};

