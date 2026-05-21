import { ShieldAlert } from "lucide-react";

export function RiskGauge({ authenticity, confidence }: { authenticity: number; confidence: number }) {
  const syntheticRisk = Math.round(100 - authenticity);
  const radius = 74;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (syntheticRisk / 100) * circumference;

  return (
    <section className="rounded-md border border-line bg-panel p-5 shadow-glow">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Current Risk</h2>
          <p className="text-xs text-slate-400">Weighted across latest scans</p>
        </div>
        <ShieldAlert className="h-5 w-5 text-danger" />
      </div>
      <div className="grid place-items-center">
        <div className="relative h-44 w-44">
          <svg viewBox="0 0 180 180" className="h-full w-full -rotate-90">
            <circle
              cx="90"
              cy="90"
              r={radius}
              stroke="#263245"
              strokeWidth="12"
              fill="transparent"
            />
            <circle
              cx="90"
              cy="90"
              r={radius}
              stroke="#ff5c75"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              fill="transparent"
            />
          </svg>
          <div className="absolute inset-0 grid place-items-center text-center">
            <div>
              <div className="text-4xl font-semibold text-white">{syntheticRisk}%</div>
              <div className="text-xs text-slate-400">synthetic risk</div>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 h-2 rounded-full bg-slate-800">
        <div className="h-2 rounded-full bg-cobalt" style={{ width: `${Math.round(confidence * 100)}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-xs text-slate-400">
        <span>Confidence</span>
        <span>{Math.round(confidence * 100)}%</span>
      </div>
    </section>
  );
}
