import type { ReactNode } from 'react';

type AnalysisCardProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

const AnalysisCard = ({ title, description, children }: AnalysisCardProps) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-sm backdrop-blur">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {description && (
            <p className="text-sm text-slate-300">{description}</p>
          )}
        </div>
      </div>
      <div className="text-slate-100">{children}</div>
    </div>
  );
};

export default AnalysisCard;

