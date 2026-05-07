import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { buildPlatformPrompt } from "./promptBuilder";
import { papers } from "./sampleData";

describe("Paper research workbench", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders category navigation and reading document entry buttons", () => {
    render(<App />);

    expect(screen.getByRole("navigation")).toHaveTextContent("差分论文");
    expect(screen.getByRole("button", { name: /通俗易懂/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /专家阅读/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /复现计划/ })).toBeInTheDocument();
    expect(screen.queryByLabelText("三列阅读卡")).not.toBeInTheDocument();
  });

  it("filters papers by category", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "积分论文" }));

    expect(screen.getByRole("heading", { name: "Integral Operator Learning for Scientific Simulation" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Differential Transformer/ })).not.toBeInTheDocument();
  });

  it("links innovation ideas back to source papers", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "创新挖掘" }));
    await user.click(screen.getByRole("button", { name: /Integral Operator Learning/ }));

    expect(screen.getByRole("heading", { name: "Integral Operator Learning for Scientific Simulation" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /通俗易懂/ }));
    expect(screen.getByLabelText("Markdown 文档阅读器")).toHaveTextContent("连续版神经网络");
  });

  it("generates platform prompts from card chat input", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /通俗易懂/ }));
    await user.type(screen.getByLabelText("优化请求"), "请把通俗解释讲得更细");
    await user.click(screen.getByRole("button", { name: /生成平台请求/ }));

    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("请把通俗解释讲得更细");
    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("Codex");
  });

  it("opens a full markdown document reader from a reading entry", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /专家阅读/ }));

    expect(screen.getByLabelText("Markdown 文档阅读器")).toHaveTextContent("机制、证据与可疑点");
    expect(screen.getByRole("button", { name: "返回论文详情" })).toBeInTheDocument();
  });

  it("replaces sample papers with hot workspace data", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        generatedAt: 1778120000,
        workspace: "/tmp/live-paper-library",
        papers: [
          {
            id: "live-paper-1",
            title: "Live Differential Paper",
            year: 2026,
            category: "实时分类",
            tags: ["live"],
            status: "complete",
            cards: {
              plain: {
                kind: "plain",
                title: "实时通俗解释",
                version: "v1",
                updatedAt: "2026-05-07",
                summary: "这是从工作区 JSON 热读取出来的解释。",
                bullets: ["热读取成功"],
                artifactPath: "/tmp/live-paper-library/knowledge/cards/live-paper-1.md",
                markdown: "# 实时通俗解释\n\n这是完整文档内容。"
              },
              expert: {
                kind: "expert",
                title: "实时专家阅读",
                version: "v1",
                updatedAt: "2026-05-07",
                summary: "专家卡来自工作区。",
                bullets: ["检查真实数据"],
                artifactPath: "/tmp/live-paper-library/knowledge/expert-readings/live-paper-1.md",
                markdown: "# 实时专家阅读\n\n专家卡来自工作区。"
              },
              reproduction: {
                kind: "reproduction",
                title: "实时复现计划",
                version: "v1",
                updatedAt: "2026-05-07",
                summary: "复现卡来自工作区。",
                bullets: ["运行最小实验"],
                artifactPath: "/tmp/live-paper-library/knowledge/reproductions/live-paper-1.md",
                markdown: "# 实时复现计划\n\n复现卡来自工作区。"
              }
            }
          }
        ],
        innovations: []
      })
    } as Response);

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Live Differential Paper" })).toBeInTheDocument();
    expect(screen.getByRole("navigation")).toHaveTextContent("实时分类");
    expect(screen.queryByRole("heading", { name: "Differential Transformer for Long Context Reasoning" })).not.toBeInTheDocument();
  });
});

describe("buildPlatformPrompt", () => {
  it("includes platform, paper, card type, and version policy", () => {
    const paper = papers[0];
    const prompt = buildPlatformPrompt({
      platform: "Claude Code",
      paper,
      card: paper.cards.expert,
      message: "专家阅读再关注实验缺陷"
    });

    expect(prompt).toContain("Claude Code");
    expect(prompt).toContain(paper.id);
    expect(prompt).toContain("专家阅读");
    expect(prompt).toContain("另存新版本");
  });
});
