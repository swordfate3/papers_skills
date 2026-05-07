import { PlatformRequest, readingKindLabels } from "./domain";

export function buildPlatformPrompt(request: PlatformRequest): string {
  const label = readingKindLabels[request.card.kind];
  return [
    `平台：${request.platform}`,
    "请使用 paper-research-workflow 技能继续优化论文阅读结果。",
    `论文 ID：${request.paper.id}`,
    `论文标题：${request.paper.title}`,
    `阅读模块：${label}`,
    `当前产物：${request.card.artifactPath}`,
    `用户要求：${request.message}`,
    "请基于现有知识库和当前卡片重新生成更好的版本。",
    "默认保留旧版本并另存新版本，除非用户明确要求覆盖。"
  ].join("\n");
}
