import { AudioLines, FileText, ImageIcon, Video } from "lucide-react";
import type { DashboardReport, MediaType } from "@/lib/types";

const icons = {
  image: ImageIcon,
  video: Video,
  audio: AudioLines,
  text: FileText,
  multimodal: FileText
};

const modalities: MediaType[] = ["image", "video", "audio", "text"];

export function ModalityMatrix({ reports }: { reports: DashboardReport[] }) {
  return (
    <section className="rounded-md border border-line bg-panel p-5">
      <div className="mb-4">
        <h2 className="text-sm font-semibold">Modality Coverage</h2>
        <p className="text-xs text-slate-400">Signal volume and average authenticity by type</p>
      </div>
      <div className="grid gap-3 md:grid-cols-4">
        {modalities.map((modality) => {
          const scoped = reports.filter((report) => report.media_type === modality);
          const average = scoped.length
            ? scoped.reduce((sum, report) => sum + report.authenticity_score, 0) / scoped.length
            : 0;
          const Icon = icons[modality];
          return (
            <article key={modality} className="rounded-md border border-slate-800 p-3">
              <Icon className="mb-3 h-5 w-5 text-cobalt" />
              <div className="text-sm font-semibold capitalize">{modality}</div>
              <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                <span>{scoped.length} scans</span>
                <span>{scoped.length ? `${Math.round(average)}%` : "--"}</span>
              </div>
              <div className="mt-2 h-1.5 rounded-full bg-slate-800">
                <div className="h-1.5 rounded-full bg-signal" style={{ width: `${average}%` }} />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
