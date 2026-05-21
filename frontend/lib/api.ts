import { mockReports } from "./mockData";
import type { DashboardReport, ScanHistoryItem } from "./types";

const API_URL = process.env.NEXT_PUBLIC_GHOSTPROOF_API_URL ?? "http://localhost:8000";

export async function fetchScanHistory(): Promise<DashboardReport[]> {
  try {
    const response = await fetch(`${API_URL}/api/v1/history?limit=25`, {
      cache: "no-store"
    });
    if (!response.ok) {
      return mockReports;
    }
    const reports = (await response.json()) as ScanHistoryItem[];
    return reports.length ? reports : mockReports;
  } catch {
    return mockReports;
  }
}
