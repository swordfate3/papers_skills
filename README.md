# Paper Research Workflow 论文研究技能

这是一个面向论文阅读、论文复现和创新点挖掘的自包含 Skills 技能包。它的发布形态是 **单个主技能**：

```text
skills/paper-research-workflow/
```

主技能内部已经包含运行所需的脚本、schema、模板和参考文档；六个子流程不会作为独立技能安装，而是作为内部参考文档打包在：

```text
skills/paper-research-workflow/references/child-skills/
```

## 安装

发布到 GitHub 后，用户可以使用 `npx skills add` 安装：

```bash
npx skills add <owner>/<repo> --skill paper-research-workflow
```

将 `<owner>/<repo>` 替换成真实 GitHub 仓库名即可。

## 包含能力

`paper-research-workflow` 内置以下论文研究流程：

- 论文输入、PDF 提取、分类和归档
- 通俗易懂解释论文
- 专家式深度阅读论文
- 论文复现计划和最小可行复现分析
- 文件型论文知识库写入与校验
- 从知识库检索相关论文并挖掘创新方向

## 目录结构

安装单元是一个完整技能目录：

```text
skills/paper-research-workflow/
  SKILL.md
  agents/openai.yaml
  scripts/
  schemas/
  templates/
  references/
    child-skills/
```

其中：

- `scripts/`：工作流 CLI、PDF 提取、分类、知识库检索、schema 校验
- `schemas/`：论文记忆、论文卡片、复现计划、创新简报的数据契约
- `templates/`：Markdown 和 JSON 输出模板
- `references/`：PDF/MinerU 说明和六个内部子流程

## 快速验证

安装后，进入已安装的 `paper-research-workflow` 技能目录，运行：

```bash
python scripts/paper_workflow.py setup --workspace workspace
python scripts/paper_workflow.py status --workspace workspace
```

如果输出类似下面内容，说明基础工作区初始化正常：

```json
{
  "papers": {}
}
```

## 读取本地 PDF

处理普通本地 PDF，可以先不启用 MinerU：

```bash
python scripts/paper_workflow.py ingest /path/to/paper.pdf --workspace workspace --no-mineru
```

运行后会生成：

```text
workspace/
  extracted/<paper-id>/
  knowledge/papers/<paper-id>.json
  papers/
  state/papers.json
```

## PDF 提取依赖

轻量 PDF 提取优先使用：

```text
pdftotext -layout
```

如果系统没有 `pdftotext`，脚本会尝试使用 Python 包 `pypdf`。

复杂 PDF、扫描件、公式/表格较多的论文可以使用 MinerU。MinerU 引擎本身不打包在本仓库中，本仓库只提供 portable adapter。用户可以：

- 将 `mineru` 安装到 `PATH`
- 或提供自己的 MinerU wrapper：

```bash
MINERU_TO_MD=/path/to/mineru_to_md.sh python scripts/paper_workflow.py ingest /path/to/paper.pdf --workspace workspace
```

## 输出说明

每篇论文都会维护一份结构化论文记忆：

```text
workspace/knowledge/papers/<paper-id>.json
```

这份 JSON 是机器可读的核心记录，包含：

- 论文基础信息
- 分类结果
- 核心问题、动机、方法、贡献
- 数据集、指标、baseline、ablation
- 假设、局限、失败模式
- 复现难度和最小可行复现
- 创新启发和相关论文链接

Markdown 输出会放在：

```text
workspace/knowledge/cards/
workspace/knowledge/expert-readings/
workspace/knowledge/reproductions/
workspace/knowledge/innovations/
```

## 开发验证

在仓库根目录运行：

```bash
uv run pytest -q
```

校验技能结构：

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/paper-research-workflow
```

当前设计目标是：别人只安装 `paper-research-workflow` 这一个技能目录，也能完成基础的论文读取、分类、入库和后续阅读流程。
