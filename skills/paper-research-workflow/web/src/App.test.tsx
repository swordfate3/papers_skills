import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { Paper, WorkbenchData } from "./domain";
import { buildPlatformPrompt } from "./promptBuilder";

const livePaper: Paper = {
  id: "live-paper-1",
  title: "Live Differential Paper",
  year: 2026,
  category: "实时分类",
  tags: ["live"],
  status: "complete",
  cards: {
    plain: {
      kind: "plain",
      status: "ready",
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
      status: "ready",
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
      status: "ready",
      title: "实时复现计划",
      version: "v1",
      updatedAt: "2026-05-07",
      summary: "复现卡来自工作区。",
      bullets: ["运行最小实验"],
      artifactPath: "/tmp/live-paper-library/knowledge/reproductions/live-paper-1.md",
      markdown: "# 实时复现计划\n\n复现卡来自工作区。"
    }
  }
};

const relatedPaper: Paper = {
  ...livePaper,
  id: "related-paper-2",
  title: "Related Integral Paper",
  category: "积分分类",
  cards: {
    ...livePaper.cards,
    plain: {
      ...livePaper.cards.plain,
      title: "积分通俗解释",
      markdown: "# 积分通俗解释\n\n连续版神经网络。"
    }
  }
};

function workspaceData(overrides: Partial<WorkbenchData> = {}): WorkbenchData {
  return {
    schemaVersion: 1,
    generatedAt: 1778120000,
    workspace: "/tmp/live-paper-library",
    papers: [livePaper, relatedPaper],
    innovations: [
      {
        id: "idea-1",
        title: "组合创新",
        score: 91,
        rank: 1,
        summary: "把两篇论文组合。",
        sources: [{ paperId: "related-paper-2", cardKind: "plain", note: "来源阅读" }],
        artifactPath: "/tmp/live-paper-library/knowledge/innovations/idea-1.md",
        markdown: "# 组合创新\n\n把两篇论文组合。"
      }
    ],
    ...overrides
  };
}

function mockFetch(data: WorkbenchData) {
  vi.spyOn(globalThis, "fetch").mockResolvedValue({
    ok: true,
    json: async () => data
  } as Response);
}

describe("Paper research workbench", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows an empty workspace without sample fallback", async () => {
    mockFetch(workspaceData({ papers: [], innovations: [] }));

    render(<App />);

    expect(await screen.findByLabelText("空工作区")).toHaveTextContent("/tmp/live-paper-library");
    expect(screen.queryByText("Legacy Demo Paper")).not.toBeInTheDocument();
  });

  it("renders category navigation and reading document entry buttons from live data", async () => {
    mockFetch(workspaceData());
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Live Differential Paper" })).toBeInTheDocument();
    expect(screen.getByRole("navigation")).toHaveTextContent("实时分类");
    expect(screen.getByRole("button", { name: /通俗易懂/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /专家阅读/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /复现计划/ })).toBeInTheDocument();
    expect(screen.queryByLabelText("三列阅读卡")).not.toBeInTheDocument();
  });

  it("filters papers by category", async () => {
    const user = userEvent.setup();
    mockFetch(workspaceData());
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "积分分类" }));

    expect(screen.getByRole("heading", { name: "Related Integral Paper" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Live Differential Paper/ })).not.toBeInTheDocument();
  });

  it("links innovation ideas back to source paper documents", async () => {
    const user = userEvent.setup();
    mockFetch(workspaceData());
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "创新挖掘" }));
    await user.click(screen.getByRole("button", { name: /Related Integral Paper/ }));

    expect(screen.getByRole("heading", { name: "Related Integral Paper" })).toBeInTheDocument();
    expect(screen.getByLabelText("Markdown 文档阅读器")).toHaveTextContent("连续版神经网络");
  });

  it("generates platform prompts from reader chat input", async () => {
    const user = userEvent.setup();
    mockFetch(workspaceData());
    render(<App />);

    await user.click(await screen.findByRole("button", { name: /通俗易懂/ }));
    await user.type(screen.getByLabelText("优化请求"), "请把通俗解释讲得更细");
    await user.click(screen.getByRole("button", { name: /生成平台请求/ }));

    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("请把通俗解释讲得更细");
    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("Codex");
  });

  it("opens a full markdown document reader from a reading entry", async () => {
    const user = userEvent.setup();
    mockFetch(workspaceData());
    render(<App />);

    await user.click(await screen.findByRole("button", { name: /专家阅读/ }));

    expect(screen.getByLabelText("Markdown 文档阅读器")).toHaveTextContent("专家卡来自工作区");
    expect(screen.getByRole("button", { name: "返回论文详情" })).toBeInTheDocument();
  });

  it("shows load errors without sample fallback", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({ ok: false, status: 404 } as Response);

    render(<App />);

    expect(await screen.findByLabelText("空工作区")).toHaveTextContent("无法读取 paper-workbench-data.json");
    expect(screen.queryByText("Legacy Demo Paper")).not.toBeInTheDocument();
  });
});

describe("buildPlatformPrompt", () => {
  it("includes platform, paper, card type, and version policy", () => {
    const prompt = buildPlatformPrompt({
      platform: "Claude Code",
      paper: livePaper,
      card: livePaper.cards.expert,
      message: "专家阅读再关注实验缺陷"
    });

    expect(prompt).toContain("Claude Code");
    expect(prompt).toContain(livePaper.id);
    expect(prompt).toContain("专家阅读");
    expect(prompt).toContain("另存新版本");
  });
});
