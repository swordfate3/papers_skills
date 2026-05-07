import { InnovationIdea, Paper, WorkbenchData } from "./domain";

export const papers: Paper[] = [
  {
    id: "2024-differential-transformer-a1b2c3",
    title: "Differential Transformer for Long Context Reasoning",
    year: 2024,
    category: "差分论文",
    tags: ["Transformer", "差分注意力", "长上下文"],
    status: "complete",
    cards: {
      plain: {
        kind: "plain",
        title: "为什么差分注意力能过滤噪声",
        version: "v2",
        updatedAt: "2026-05-07",
        summary: "这篇论文可以理解为给注意力机制加了一组对照信号，让模型更容易削弱无关上下文。",
        bullets: ["核心直觉是两路注意力相减", "适合解释长上下文里的干扰项", "局限在于训练和推理成本需要继续验证"],
        artifactPath: "workspace/knowledge/cards/2024-differential-transformer-a1b2c3.v2.md"
      },
      expert: {
        kind: "expert",
        title: "专家阅读：机制、证据与可疑点",
        version: "v1",
        updatedAt: "2026-05-07",
        summary: "专家视角重点关注差分结构是否真的带来因果性改进，以及 ablation 是否排除了参数量因素。",
        bullets: ["需要核对同参数量 baseline", "关注注意力热图是否只是后验解释", "可扩展到检索增强场景"],
        artifactPath: "workspace/knowledge/expert-readings/2024-differential-transformer-a1b2c3.md"
      },
      reproduction: {
        kind: "reproduction",
        title: "最小可行复现路径",
        version: "v1",
        updatedAt: "2026-05-07",
        summary: "先复现一个小型语言模型上的差分注意力层，再比较困惑度和长上下文 QA。",
        bullets: ["实现差分注意力模块", "用公开小语料跑 sanity check", "增加长上下文干扰项评测"],
        artifactPath: "workspace/knowledge/reproductions/2024-differential-transformer-a1b2c3.md"
      }
    }
  },
  {
    id: "2023-integral-operator-learning-d4e5f6",
    title: "Integral Operator Learning for Scientific Simulation",
    year: 2023,
    category: "积分论文",
    tags: ["Neural Operator", "积分算子", "科学计算"],
    status: "reading",
    cards: {
      plain: {
        kind: "plain",
        title: "把函数映射理解成连续版神经网络",
        version: "v1",
        updatedAt: "2026-05-06",
        summary: "这类方法不是预测一个点，而是学习从一个函数到另一个函数的整体变换。",
        bullets: ["适合 PDE 和物理仿真", "积分核像可学习的连续卷积", "泛化依赖采样分辨率"],
        artifactPath: "workspace/knowledge/cards/2023-integral-operator-learning-d4e5f6.md"
      },
      expert: {
        kind: "expert",
        title: "算子学习的假设边界",
        version: "v1",
        updatedAt: "2026-05-06",
        summary: "专家阅读关注算子泛化是否来自结构先验，还是来自数据分布相对稳定。",
        bullets: ["检查跨网格泛化", "关注边界条件变化", "比较 Fourier 和 kernel 表达"],
        artifactPath: "workspace/knowledge/expert-readings/2023-integral-operator-learning-d4e5f6.md"
      },
      reproduction: {
        kind: "reproduction",
        title: "PDE 小任务复现计划",
        version: "v1",
        updatedAt: "2026-05-06",
        summary: "选择 Burgers 方程数据集，用低分辨率训练，高分辨率测试来验证核心说法。",
        bullets: ["准备公开 PDE 数据", "实现积分核层", "报告跨分辨率误差"],
        artifactPath: "workspace/knowledge/reproductions/2023-integral-operator-learning-d4e5f6.md"
      }
    }
  }
];

export const innovations: InnovationIdea[] = [
  {
    id: "innovation-diff-integral-memory",
    title: "差分注意力与积分算子的连续记忆层",
    score: 91,
    rank: 1,
    summary: "把差分注意力的噪声抵消思想引入神经算子，让模型在连续函数空间里学习正负证据的积分核。",
    sources: [
      {
        paperId: "2024-differential-transformer-a1b2c3",
        cardKind: "expert",
        note: "差分结构提供了去噪和对照机制。"
      },
      {
        paperId: "2023-integral-operator-learning-d4e5f6",
        cardKind: "plain",
        note: "积分算子提供连续函数映射框架。"
      }
    ],
    artifactPath: "workspace/knowledge/innovations/innovation-diff-integral-memory.md"
  }
];

export const sampleWorkbenchData: WorkbenchData = {
  generatedAt: 0,
  workspace: "sample",
  papers,
  innovations
};
