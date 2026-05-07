import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "./App";
import { buildPlatformPrompt } from "./promptBuilder";
import { papers } from "./sampleData";

describe("Paper research workbench", () => {
  it("renders category navigation and three reading cards", () => {
    render(<App />);

    expect(screen.getByRole("navigation")).toHaveTextContent("差分论文");
    expect(screen.getByLabelText("通俗易懂")).toBeInTheDocument();
    expect(screen.getByLabelText("专家阅读")).toBeInTheDocument();
    expect(screen.getByLabelText("复现计划")).toBeInTheDocument();
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
    expect(screen.getByLabelText("通俗易懂")).toHaveTextContent("连续版神经网络");
  });

  it("generates platform prompts from card chat input", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getAllByLabelText("优化请求")[0], "请把通俗解释讲得更细");
    await user.click(screen.getAllByRole("button", { name: /生成平台请求/ })[0]);

    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("请把通俗解释讲得更细");
    expect(screen.getByLabelText("通俗易懂平台请求")).toHaveTextContent("Codex");
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
