import type { YouTubeAnalysis } from '../types/idea';

type YouTubeCardProps = {
  data?: YouTubeAnalysis | null;
};

const YouTubeCard = ({ data }: YouTubeCardProps) => {
  if (!data) {
    return <p className="text-sm text-slate-300">No data</p>;
  }

  return (
    <div className="space-y-2 text-sm text-slate-100">
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Total videos found</span>
        <span className="font-semibold text-indigo-200">{data.total_videos_found}</span>
      </div>
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Total views</span>
        <span className="font-semibold text-indigo-200">
          {data.total_views.toLocaleString()}
        </span>
      </div>
      {data.avg_views && (
        <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
          <span>Avg views</span>
          <span className="font-semibold text-indigo-200">
            {data.avg_views.toLocaleString()}
          </span>
        </div>
      )}
      {data.avg_rating && (
        <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
          <span>Avg rating</span>
          <span className="font-semibold text-indigo-200">{data.avg_rating}</span>
        </div>
      )}
      <div className="rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <p className="font-semibold text-indigo-200">Top channels</p>
        <p>{data.top_channels.join(', ') || 'N/A'}</p>
      </div>
      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2">
        <span>Engagement score</span>
        <span className="font-semibold text-indigo-200">{data.engagement_score}</span>
      </div>
    </div>
  );
};

export default YouTubeCard;

