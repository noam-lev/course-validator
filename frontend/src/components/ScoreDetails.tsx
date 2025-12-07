import { useState } from 'react';
import type { ScoreExplanation } from '../types/idea';

type ScoreDetailsProps = {
  scoreExplanations: ScoreExplanation;
};

const ScoreDetails = ({ scoreExplanations }: ScoreDetailsProps) => {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50">
      <button
        type="button"
        className="flex w-full items-center justify-between px-4 py-3 text-left text-slate-100"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="font-semibold">Score Explanations</span>
        <span className="text-sm text-indigo-300">{open ? 'Hide' : 'Show'}</span>
      </button>
      {open && (
        <div className="space-y-3 border-t border-slate-800 px-4 py-3 text-sm text-slate-200">
          <div>
            <p className="font-medium text-indigo-200">Demand</p>
            <p>{scoreExplanations.demand}</p>
          </div>
          <div>
            <p className="font-medium text-indigo-200">Competition</p>
            <p>{scoreExplanations.competition}</p>
          </div>
          <div>
            <p className="font-medium text-indigo-200">Good Idea</p>
            <p>{scoreExplanations.good_idea}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScoreDetails;

