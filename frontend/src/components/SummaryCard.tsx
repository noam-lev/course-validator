type SummaryCardProps = {
  summary: string;
  courseTypeDescription: string;
  contentGapHint?: string | null;
};

const SummaryCard = ({
  summary,
  courseTypeDescription,
  contentGapHint,
}: SummaryCardProps) => {
  return (
    <div className="space-y-3">
      <p className="text-sm text-indigo-300">{courseTypeDescription}</p>
      <p className="text-sm leading-relaxed text-slate-100">{summary}</p>
      {contentGapHint && (
        <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-3 text-sm text-indigo-100">
          <p className="font-semibold text-indigo-200">Content Gap Hint</p>
          <p>{contentGapHint}</p>
        </div>
      )}
    </div>
  );
};

export default SummaryCard;

