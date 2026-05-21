import { analyzeCandidate } from "../shared/api";
import type { MediaCandidate, ScanReport } from "../shared/types";

const HISTORY_KEY = "ghostproof_scan_history";
const MAX_HISTORY = 50;

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "ghostproof-scan-media",
      title: "Scan with GhostProof",
      contexts: ["image", "video", "audio", "selection", "page"]
    });
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type !== "GHOSTPROOF_SCAN_CANDIDATE") {
    return false;
  }

  void scanCandidate(message.candidate as MediaCandidate, sender.tab?.id)
    .then(sendResponse)
    .catch((error) => sendResponse({ error: String(error) }));
  return true;
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId !== "ghostproof-scan-media" || !tab?.id) {
    return;
  }
  const candidate = candidateFromContext(info);
  if (!candidate) {
    return;
  }
  void scanCandidate(candidate, tab.id);
});

async function scanCandidate(candidate: MediaCandidate, tabId?: number): Promise<ScanReport> {
  let report: ScanReport;
  try {
    report = await analyzeCandidate(candidate);
    void chrome.storage.local.set({ ghostproof_backend_status: "ok" });
  } catch (err) {
    void chrome.storage.local.set({ ghostproof_backend_status: "error" });
    throw err;
  }
  await persistReport(report);
  if (tabId) {
    void chrome.tabs.sendMessage(tabId, {
      type: "GHOSTPROOF_RENDER_REPORT",
      candidateId: candidate.id,
      report
    });
  }
  return report;
}

function candidateFromContext(info: chrome.contextMenus.OnClickData): MediaCandidate | undefined {
  if (info.srcUrl) {
    const mediaType = inferMediaType(info.mediaType, info.srcUrl);
    return {
      id: `gp_context_${crypto.randomUUID()}`,
      mediaType,
      sourceUrl: info.srcUrl,
      metadata: {
        context: "context_menu",
        pageUrl: info.pageUrl
      }
    };
  }
  if (info.selectionText && info.selectionText.trim().length > 40) {
    return {
      id: `gp_context_${crypto.randomUUID()}`,
      mediaType: "text",
      content: info.selectionText.trim(),
      metadata: {
        context: "context_menu",
        pageUrl: info.pageUrl,
        selected: true
      }
    };
  }
  return undefined;
}

function inferMediaType(
  menuType: chrome.contextMenus.OnClickData["mediaType"],
  srcUrl: string
): MediaCandidate["mediaType"] {
  if (menuType === "video" || /\.(mp4|webm|mov|m4v)(\?|$)/i.test(srcUrl)) {
    return "video";
  }
  if (menuType === "audio" || /\.(mp3|wav|m4a|ogg)(\?|$)/i.test(srcUrl)) {
    return "audio";
  }
  return "image";
}

async function persistReport(report: ScanReport): Promise<void> {
  const stored = await chrome.storage.local.get(HISTORY_KEY);
  const history = (stored[HISTORY_KEY] as ScanReport[] | undefined) ?? [];
  await chrome.storage.local.set({
    [HISTORY_KEY]: [report, ...history].slice(0, MAX_HISTORY)
  });
}
