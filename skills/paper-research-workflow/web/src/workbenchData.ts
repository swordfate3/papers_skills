import { WorkbenchData } from "./domain";

export const WORKBENCH_DATA_URL = "/paper-workbench-data.json";
export const WORKBENCH_POLL_INTERVAL_MS = 5000;

export function emptyWorkbenchData(): WorkbenchData {
  return {
    schemaVersion: 1,
    generatedAt: 0,
    workspace: "",
    papers: [],
    innovations: []
  };
}

export async function loadWorkbenchData(fetcher: typeof fetch = fetch): Promise<WorkbenchData> {
  const response = await fetcher(`${WORKBENCH_DATA_URL}?t=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load workbench data: ${response.status}`);
  }
  const payload = (await response.json()) as Partial<WorkbenchData>;
  return normalizeWorkbenchData(payload);
}

export function normalizeWorkbenchData(payload: Partial<WorkbenchData>): WorkbenchData {
  return {
    schemaVersion: 1,
    generatedAt: Number(payload.generatedAt ?? Date.now() / 1000),
    workspace: String(payload.workspace ?? ""),
    papers: Array.isArray(payload.papers) ? payload.papers : [],
    innovations: Array.isArray(payload.innovations) ? payload.innovations : []
  };
}
