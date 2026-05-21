import { AlertTriangle, FileSearch } from "lucide-react";
import type { DashboardReport } from "@/lib/types";

export function EvidencePanel({ reports }: { reports: DashboardReport[] }) {
  const evidence = reports
    .flatMap((report) =>
      (report.evidence ?? []).map((item) => ({
        ...item,
        scanId: report.scan_id,
        riskLevel: report.risk_level
      }))
    )
    .sort((a, b) => b.severity - a.severity)
    .slice(0, 6);

  return (
    <section className="rounded-md border border-line bg-panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold">Evidence Queue</h2>
          <p className="text-xs text-slate-400">Highest-severity explainability signals</p>
        </div>
        <FileSearch className="h-5 w-5 text-cobalt" />
      </div>
      <div className="grid gap-3">
        {evidence.map((item) => (
          <article key={`${item.scanId}-${item.code}`} className="rounded-md border border-slate-800 p-3">
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber" />
                <h3 className="text-sm font-semibold">{item.title}</h3>
              </div>
              <span className="text-xs text-slate-400">{Math.round(item.severity * 100)}%</span>
            </div>
            <p className="text-sm text-slate-300">{item.description}</p>
            <div className="mt-2 text-xs text-slate-500">
              {item.modality} / {item.riskLevel}
            </div>
          </article>
        ))}
        {evidence.length === 0 && (
          <div className="rounded-md border border-slate-800 p-4 text-sm text-slate-400">
            No evidence above review threshold.
          </div>
        )}
      </div>
    </section>
  );
}
