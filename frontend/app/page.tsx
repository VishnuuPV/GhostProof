import { Activity, AlertTriangle, Database, ShieldCheck } from "lucide-react";
import { EvidencePanel } from "@/components/EvidencePanel";
import { ModalityMatrix } from "@/components/ModalityMatrix";
import { RiskGauge } from "@/components/RiskGauge";
import { ScanTimeline } from "@/components/ScanTimeline";
import { StatCard } from "@/components/StatCard";
import { fetchScanHistory } from "@/lib/api";

export default async function DashboardPage() {
  const reports = await fetchScanHistory();
  const latest = reports[0];
  const highRisk = reports.filter((report) => report.risk_level === "high" || report.risk_level === "critical");
  const averageAuthenticity =
    reports.reduce((sum, report) => sum + report.authenticity_score, 0) / Math.max(reports.length, 1);
  const averageConfidence =
    reports.reduce((sum, report) => sum + report.confidence, 0) / Math.max(reports.length, 1);

  return (
    <main className="min-h-screen px-5 py-5 md:px-8">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-md border border-emerald-400/30 bg-emerald-400/10">
            <ShieldCheck className="h-6 w-6 text-signal" />
          </div>
          <div>
            <h1 className="text-xl font-semibold tracking-normal">GhostProof</h1>
            <p className="text-sm text-slate-400">Synthetic media authenticity operations</p>
          </div>
        </div>
        <div className="rounded-md border border-line bg-panel px-3 py-2 text-xs text-slate-400">
          API evidence log / {latest ? new Date(latest.created_at).toLocaleString() : "no scans"}
        </div>
      </header>

      <section className="mb-5 grid gap-3 md:grid-cols-4">
        <StatCard icon={Activity} label="Total scans" value={reports.length.toString()} />
        <StatCard icon={AlertTriangle} label="High-risk findings" value={highRisk.length.toString()} tone="bad" />
        <StatCard
          icon={ShieldCheck}
          label="Avg authenticity"
          value={`${Math.round(averageAuthenticity)}%`}
          tone="good"
        />
        <StatCard icon={Database} label="Evidence hashes" value={reports.length.toString()} tone="neutral" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[360px_1fr]">
        <div className="grid content-start gap-5">
          <RiskGauge authenticity={averageAuthenticity} confidence={averageConfidence} />
          <EvidencePanel reports={reports} />
        </div>
        <div className="grid content-start gap-5">
          <ModalityMatrix reports={reports} />
          <ScanTimeline reports={reports} />
        </div>
      </section>
    </main>
  );
}
