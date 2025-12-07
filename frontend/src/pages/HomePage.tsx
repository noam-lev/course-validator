import { useState, type FormEvent } from 'react';
import { analyzeIdea } from '../api/ideaService';
import type { CourseIdeaRequest, CourseIdeaResponse } from '../types/idea';
import Alert from '../components/Alert';
import Spinner from '../components/Spinner';
import AnalysisCard from '../components/AnalysisCard';
import ScoreBoard from '../components/ScoreBoard';
import SummaryCard from '../components/SummaryCard';
import ScoreDetails from '../components/ScoreDetails';
import JobMarketCard from '../components/JobMarketCard';
import YouTubeCard from '../components/YouTubeCard';
import { USE_MOCK_API } from '../config';

const HomePage = () => {
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CourseIdeaResponse | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!userInput.trim()) {
      setError('Please enter a course idea before analyzing.');
      return;
    }

    setLoading(true);
    setResult(null);
    const payload: CourseIdeaRequest = { user_input: userInput.trim() };

    try {
      const response = await analyzeIdea(payload);
      setResult(response);
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 py-8">
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-white shadow-lg">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold">Course Idea Validator</h1>
            <p className="text-sm text-slate-300">
              Paste your idea, validate it against demand, competition, and engagement signals.
            </p>
          </div>
          {USE_MOCK_API && (
            <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs font-semibold text-amber-300">
              Mock mode
            </span>
          )}
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Describe your course idea..."
            rows={5}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm text-white outline-none ring-2 ring-transparent transition focus:ring-indigo-500"
          />
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={loading || !userInput.trim()}
              className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow transition disabled:cursor-not-allowed disabled:bg-slate-600"
            >
              {loading ? 'Analyzing...' : 'Analyze Idea'}
            </button>
            <p className="text-xs text-slate-400">
              We&apos;ll score demand, competition, and show engagement signals.
            </p>
          </div>
        </form>
      </div>

      {error && <Alert message={error} />}
      {loading && <Spinner />}

      {result && (
        <div className="grid gap-4">
          <AnalysisCard title="Top-Level Scores">
            <ScoreBoard
              demandScore={result.demand_score}
              competitionScore={result.competition_score}
              goodIdeaScore={result.good_idea_score}
            />
          </AnalysisCard>

          <AnalysisCard
            title="Quick Summary"
            description="Key takeaway, course type, and content gap hints."
          >
            <SummaryCard
              summary={result.summary}
              courseTypeDescription={result.course_type.description}
              contentGapHint={result.content_gap_hint}
            />
          </AnalysisCard>

          <AnalysisCard
            title="Score Details"
            description="How we derived each score."
          >
            <ScoreDetails scoreExplanations={result.score_explanations} />
          </AnalysisCard>

          <div className="grid gap-4 md:grid-cols-2">
            <AnalysisCard
              title="Job Market"
              description="Hiring signals and required skills."
            >
              <JobMarketCard data={result.job_market} />
            </AnalysisCard>
            <AnalysisCard
              title="Engagement (YouTube)"
              description="Channel and video engagement signals."
            >
              <YouTubeCard data={result.youtube_analysis} />
            </AnalysisCard>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;

