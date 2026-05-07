export type ReadingKind = "plain" | "expert" | "reproduction";

export type Platform = "Codex" | "Claude Code" | "OpenClaw";

export interface ReadingCard {
  kind: ReadingKind;
  status: "ready" | "pending";
  title: string;
  version: string;
  updatedAt: string;
  summary: string;
  bullets: string[];
  artifactPath: string;
  markdown?: string;
}

export interface Paper {
  id: string;
  title: string;
  year: number;
  category: string;
  tags: string[];
  status: "ingested" | "reading" | "complete";
  cards: Record<ReadingKind, ReadingCard>;
}

export interface InnovationSource {
  paperId: string;
  cardKind: ReadingKind;
  note: string;
}

export interface InnovationIdea {
  id: string;
  title: string;
  score: number;
  rank: number;
  summary: string;
  sources: InnovationSource[];
  artifactPath: string;
  markdown: string;
}

export interface WorkbenchData {
  schemaVersion: 1;
  generatedAt: number;
  workspace: string;
  papers: Paper[];
  innovations: InnovationIdea[];
}

export interface PlatformRequest {
  platform: Platform;
  paper: Paper;
  card: ReadingCard;
  message: string;
}

export const readingKindLabels: Record<ReadingKind, string> = {
  plain: "通俗易懂",
  expert: "专家阅读",
  reproduction: "复现计划"
};
