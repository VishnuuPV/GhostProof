import { Clock3 } from "lucide-react";
import type { DashboardReport, RiskLevel } from "@/lib/types";

const riskClass: Record<RiskLevel, string> = {
  low: "bg-signal",
  medium: "bg-amber",
  high: "bg-danger",
  critical: "bg-danger"
};

export function ScanTimeline({ reports }: { reports: DashboardReport[] }) {
  return (
    <section className="rounded-md border border-line bg-panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Scan Timeline</h2>
          <p className="text-xs text-slate-400">Recent browser and API reports</p>
        </div>
        <Clock3 className="h-5 w-5 text-signal" />
      </div>
      <div className="grid gap-3">
        {reports.map((report) => (
          <article key={report.scan_id} className="grid grid-cols-[12px_1fr_auto] gap-3">
            <div className={`mt-1.5 h-3 w-3 rounded-full ${riskClass[report.risk_level]}`} />
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-semibold">{report.media_type}</span>
                <span className="rounded border border-slate-700 px-1.5 py-0.5 text-[11px] uppercase text-slate-400">
                  {report.risk_level}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-300">{report.summary}</p>
              <p className="mt-1 truncate text-xs text-slate-500">{report.source_url ?? report.content_hash}</p>
            </div>
            <div className="text-right text-sm font-semibold">{Math.round(report.authenticity_score)}%</div>
          </article>
        ))}
      </div>
    </section>
  );
}
