import { WorkbenchData } from "./domain";
import { sampleWorkbenchData } from "./sampleData";

export const WORKBENCH_DATA_URL = "/paper-workbench-data.json";
export const WORKBENCH_POLL_INTERVAL_MS = 5000;

export async function loadWorkbenchData(fetcher: typeof fetch = fetch): Promise<WorkbenchData> {
  const response = await fetcher(WORKBENCH_DATA_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load workbench data: ${response.status}`);
  }
  const payload = (await response.json()) as Partial<WorkbenchData>;
  return {
    generatedAt: Number(payload.generatedAt ?? Date.now() / 1000),
    workspace: String(payload.workspace ?? ""),
    papers: Array.isArray(payload.papers) ? payload.papers : [],
    innovations: Array.isArray(payload.innovations) ? payload.innovations : []
  };
}

export function dataOrSample(data: WorkbenchData): WorkbenchData {
  if (data.papers.length > 0 || data.innovations.length > 0) {
    return data;
  }
  return {
    ...sampleWorkbenchData,
    generatedAt: data.generatedAt,
    workspace: data.workspace || sampleWorkbenchData.workspace
  };
}
