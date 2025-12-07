import type { JobMarketData } from '../types/idea';

type JobMarketCardProps = {
  data?: JobMarketData | null;
};

const JobMarketCard = ({ data }: JobMarketCardProps) => {
  if (!data) {
    return <p className="text-sm text-slate-300">No data</p>;
  }

  return (
    <div className="space-y-2 text-sm text-slate-100">
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Total jobs found</span>
        <span className="font-semibold text-indigo-200">{data.total_jobs_found}</span>
      </div>
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Job demand score</span>
        <span className="font-semibold text-indigo-200">{data.job_demand_score}</span>
      </div>
      {data.avg_salary && (
        <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
          <span>Avg salary</span>
          <span className="font-semibold text-indigo-200">
            ${data.avg_salary.toLocaleString()}
          </span>
        </div>
      )}
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <p className="font-semibold text-indigo-200">Top job titles</p>
        <p>{data.top_job_titles.join(', ')}</p>
      </div>
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <p className="font-semibold text-indigo-200">Required skills</p>
        <p>{data.required_skills.join(', ')}</p>
      </div>
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Growth trend</span>
        <span className="font-semibold capitalize text-indigo-200">
          {data.growth_trend}
        </span>
      </div>
    </div>
  );
};

export default JobMarketCard;

