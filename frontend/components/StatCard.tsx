import type { LucideIcon } from "lucide-react";

export function StatCard({
  icon: Icon,
  label,
  value,
  tone = "neutral"
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  tone?: "neutral" | "good" | "warn" | "bad";
}) {
  const color = {
    neutral: "text-cobalt",
    good: "text-signal",
    warn: "text-amber",
    bad: "text-danger"
  }[tone];

  return (
    <section className="rounded-md border border-line bg-panel p-4">
      <div className={`mb-3 ${color}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-2xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-slate-400">{label}</div>
    </section>
  );
}
