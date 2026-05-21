import type { RiskLevel, ScanReport } from "../shared/types";

const COLORS: Record<RiskLevel, string> = {
  low: "#38e8a1",
  medium: "#f5b84b",
  high: "#ff7a59",
  critical: "#ff3b65"
};

export function renderRiskBadge(target: Element, report: ScanReport): void {
  const element = target as HTMLElement;
  const container = ensureContainer(element);
  const badge = document.createElement("button");
  const color = COLORS[report.risk_level];
  badge.type = "button";
  badge.className = "ghostproof-risk-badge";
  badge.innerHTML = `
    <span class="ghostproof-dot"></span>
    <span>${Math.round(report.authenticity_score)}% authentic</span>
  `;
  badge.style.setProperty("--ghostproof-risk", color);
  badge.title = report.summary;
  badge.addEventListener("click", () => showEvidencePanel(report));
  container.appendChild(badge);
}

function ensureContainer(element: HTMLElement): HTMLElement {
  injectStyles();
  const existing = element.parentElement?.querySelector<HTMLElement>(
    `.ghostproof-overlay[data-for='${element.dataset.ghostproofId}']`
  );
  if (existing) {
    existing.replaceChildren();
    return existing;
  }

  if (getComputedStyle(element).position === "static") {
    element.style.position = "relative";
  }

  const container = document.createElement("div");
  container.className = "ghostproof-overlay";
  container.dataset.for = element.dataset.ghostproofId ?? "";
  element.insertAdjacentElement("afterend", container);
  return container;
}

function showEvidencePanel(report: ScanReport): void {
  injectStyles();
  document.querySelector(".ghostproof-evidence-panel")?.remove();
  const panel = document.createElement("aside");
  panel.className = "ghostproof-evidence-panel";
  const topEvidence = report.evidence.slice(0, 4);
  panel.innerHTML = `
    <header>
      <strong>GhostProof</strong>
      <button type="button" aria-label="Close">x</button>
    </header>
    <div class="ghostproof-score">
      <span>${report.risk_level.toUpperCase()}</span>
      <b>${Math.round(report.ai_probability * 100)}%</b>
      <small>synthetic risk</small>
    </div>
    <p>${escapeHtml(report.summary)}</p>
    <ul>
      ${topEvidence
        .map(
          (item) => `
        <li>
          <span>${escapeHtml(item.title)}</span>
          <small>${escapeHtml(item.description)}</small>
        </li>
      `
        )
        .join("")}
    </ul>
  `;
  panel.querySelector("button")?.addEventListener("click", () => panel.remove());
  document.body.appendChild(panel);
}

function injectStyles(): void {
  if (document.getElementById("ghostproof-overlay-styles")) {
    return;
  }
  const style = document.createElement("style");
  style.id = "ghostproof-overlay-styles";
  style.textContent = `
    .ghostproof-overlay {
      display: inline-flex;
      position: relative;
      z-index: 2147483646;
      margin: 4px 0 0 0;
      pointer-events: auto;
    }
    .ghostproof-risk-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      height: 26px;
      padding: 0 9px;
      border: 1px solid color-mix(in srgb, var(--ghostproof-risk), transparent 42%);
      border-radius: 6px;
      background: rgba(8, 11, 16, 0.92);
      color: #f8fbff;
      font: 600 11px/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.36);
      cursor: pointer;
    }
    .ghostproof-dot {
      width: 7px;
      height: 7px;
      border-radius: 999px;
      background: var(--ghostproof-risk);
      box-shadow: 0 0 10px var(--ghostproof-risk);
    }
    .ghostproof-evidence-panel {
      position: fixed;
      top: 18px;
      right: 18px;
      width: min(360px, calc(100vw - 36px));
      z-index: 2147483647;
      border: 1px solid rgba(148, 163, 184, 0.24);
      border-radius: 8px;
      background: #080b10;
      color: #e7edf7;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.55);
      padding: 16px;
      font: 13px/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .ghostproof-evidence-panel header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .ghostproof-evidence-panel button {
      border: 0;
      background: #172032;
      color: #cbd5e1;
      border-radius: 4px;
      height: 24px;
      width: 24px;
      cursor: pointer;
    }
    .ghostproof-score {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 2px 10px;
      margin-bottom: 10px;
    }
    .ghostproof-score span {
      color: #94a3b8;
      font-size: 11px;
      letter-spacing: 0;
    }
    .ghostproof-score b {
      grid-row: span 2;
      color: #ff5c75;
      font-size: 26px;
    }
    .ghostproof-score small {
      color: #64748b;
    }
    .ghostproof-evidence-panel ul {
      list-style: none;
      padding: 0;
      margin: 12px 0 0;
      display: grid;
      gap: 8px;
    }
    .ghostproof-evidence-panel li {
      border-left: 2px solid #38e8a1;
      padding-left: 8px;
    }
    .ghostproof-evidence-panel li span {
      display: block;
      font-weight: 700;
    }
    .ghostproof-evidence-panel li small {
      color: #aab6c7;
    }
  `;
  document.documentElement.appendChild(style);
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    };
    return entities[char];
  });
}
