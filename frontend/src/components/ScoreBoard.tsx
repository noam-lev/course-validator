type ScoreBoardProps = {
  demandScore: string;
  competitionScore: string;
  goodIdeaScore: string;
};

const scoreColor = (score: string) => {
  const numeric = parseInt(score, 10);
  if (Number.isNaN(numeric)) return 'bg-slate-700 text-white';
  if (numeric >= 75) return 'bg-emerald-600 text-white';
  if (numeric >= 50) return 'bg-amber-500 text-slate-900';
  return 'bg-rose-600 text-white';
};

const ScoreCard = ({ label, value }: { label: string; value: string }) => (
  <div className="flex flex-1 flex-col gap-2 rounded-xl border border-slate-800 bg-slate-900/70 p-4">
    <p className="text-sm text-slate-300">{label}</p>
    <div
      className={`inline-flex w-fit items-center gap-2 rounded-lg px-3 py-2 text-lg font-semibold ${scoreColor(value)}`}
    >
      {value}
    </div>
  </div>
);

const ScoreBoard = ({
  demandScore,
  competitionScore,
  goodIdeaScore,
}: ScoreBoardProps) => {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <ScoreCard label="Demand Score" value={demandScore} />
      <ScoreCard label="Competition Score" value={competitionScore} />
      <ScoreCard label="Good Idea Score" value={goodIdeaScore} />
    </div>
  );
};

export default ScoreBoard;

