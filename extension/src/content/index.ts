import { extractMediaCandidates } from "./mediaExtractor";
import { renderRiskBadge } from "./overlay";
import type { MediaCandidate, ScanReport } from "../shared/types";

const seen = new Set<string>();
let observer: MutationObserver | undefined;

void scheduleScan();

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "GHOSTPROOF_RENDER_REPORT") {
    return false;
  }
  renderReport(message.candidateId, message.report);
  sendResponse({ ok: true });
  return true;
});

function scheduleScan(): void {
  window.setTimeout(() => void scanPage(), 900);
  observer = new MutationObserver(debounce(() => void scanPage(), 1200));
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ["src", "srcset", "data-src"]
  });
}

async function scanPage(): Promise<void> {
  watchUnloadedImages();
  const candidates = extractMediaCandidates().filter((candidate) => !seen.has(candidate.id));
  await Promise.allSettled(
    candidates.slice(0, 24).map((candidate) => {
      seen.add(candidate.id);
      return requestScan(candidate);
    })
  );
}

function watchUnloadedImages(): void {
  document.querySelectorAll<HTMLImageElement>("img").forEach((img) => {
    if (img.complete || img.dataset.ghostproofWatch) return;
    img.dataset.ghostproofWatch = "1";
    img.addEventListener("load", () => void scanPage(), { once: true });
  });
}

async function requestScan(candidate: MediaCandidate): Promise<void> {
  try {
    const report = await chrome.runtime.sendMessage({
      type: "GHOSTPROOF_SCAN_CANDIDATE",
      candidate
    });
    if (report?.scan_id) {
      renderReport(candidate.id, report as ScanReport);
    }
  } catch {
    seen.delete(candidate.id);
  }
}

function renderReport(candidateId: string, report: ScanReport): void {
  const element = document.querySelector(`[data-ghostproof-id='${candidateId}']`);
  if (!element) {
    return;
  }
  if (report.risk_level === "medium" || report.risk_level === "high" || report.risk_level === "critical") {
    renderRiskBadge(element, report);
  }
}

function debounce(callback: () => void, delay: number): () => void {
  let timer: number | undefined;
  return () => {
    if (timer) {
      window.clearTimeout(timer);
    }
    timer = window.setTimeout(callback, delay);
  };
}

window.addEventListener("beforeunload", () => observer?.disconnect());
