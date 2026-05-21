import { Activity, AlertTriangle, Gauge, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { RiskLevel, ScanReport } from "../shared/types";

const HISTORY_KEY = "ghostproof_scan_history";

const riskColor: Record<RiskLevel, string> = {
  low: "text-signal",
  medium: "text-amber",
  high: "text-danger",
  critical: "text-danger"
};

export function Popup() {
  const [reports, setReports] = useState<ScanReport[]>([]);
  const [backendStatus, setBackendStatus] = useState<"ok" | "error" | "unknown">("unknown");

  useEffect(() => {
    void chrome.storage.local.get([HISTORY_KEY, "ghostproof_backend_status"]).then((stored) => {
      setReports((stored[HISTORY_KEY] as ScanReport[] | undefined) ?? []);
      const status = stored["ghostproof_backend_status"] as string | undefined;
      setBackendStatus(status === "ok" ? "ok" : status === "error" ? "error" : "unknown");
    });
  }, []);

  const latest = reports[0];
  const highRiskCount = useMemo(
    () => reports.filter((report) => report.risk_level === "high" || report.risk_level === "critical").length,
    [reports]
  );

  return (
    <main className="w-[380px] bg-ink text-slate-100">
      <header className="border-b border-slate-800 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-md border border-emerald-400/30 bg-emerald-400/10">
            <ShieldCheck className="h-5 w-5 text-signal" />
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-normal">GhostProof</h1>
            <p className="text-xs text-slate-400">Synthetic media scanner</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <span
              className={`h-2 w-2 rounded-full ${
                backendStatus === "ok"
                  ? "bg-emerald-400"
                  : backendStatus === "error"
                    ? "bg-red-500"
                    : "bg-slate-500"
              }`}
            />
            <span className="text-[11px] text-slate-500">
              {backendStatus === "ok" ? "API connected" : backendStatus === "error" ? "API unreachable" : "API unknown"}
            </span>
          </div>
        </div>
      </header>

      <section className="grid grid-cols-3 gap-2 px-4 py-4">
        <Metric icon={<Activity />} label="Scans" value={reports.length.toString()} />
        <Metric icon={<AlertTriangle />} label="High risk" value={highRiskCount.toString()} />
        <Metric
          icon={<Gauge />}
          label="Latest"
          value={latest ? `${Math.round(latest.authenticity_score)}%` : "--"}
        />
      </section>

      <section className="px-4 pb-4">
        <h2 className="mb-2 text-xs font-semibold uppercase text-slate-500">Recent evidence</h2>
        <div className="grid gap-2">
          {reports.slice(0, 5).map((report) => (
            <article key={report.scan_id} className="rounded-md border border-slate-800 bg-panel p-3">
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="text-xs uppercase text-slate-500">{report.media_type}</span>
                <span className={`text-xs font-semibold ${riskColor[report.risk_level]}`}>
                  {report.risk_level}
                </span>
              </div>
              <p className="text-sm text-slate-100">{report.summary}</p>
              <div className="mt-2 h-1.5 rounded-full bg-slate-800">
                <div
                  className="h-1.5 rounded-full bg-signal"
                  style={{ width: `${report.authenticity_score}%` }}
                />
              </div>
            </article>
          ))}
          {reports.length === 0 && (
            <div className="rounded-md border border-slate-800 bg-panel p-4 text-sm text-slate-400">
              No scans stored yet. Open a page with media to start analysis.
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }: { icon: JSX.Element; label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-800 bg-panel p-3">
      <div className="mb-2 text-slate-500 [&>svg]:h-4 [&>svg]:w-4">{icon}</div>
      <div className="text-lg font-semibold">{value}</div>
      <div className="text-[11px] text-slate-500">{label}</div>
    </div>
  );
}
