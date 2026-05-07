import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { ArrowLeft, BookOpen, Brain, Code2, FileText, Lightbulb, MessageSquare, Network, Search } from "lucide-react";
import { InnovationIdea, Paper, Platform, ReadingCard, ReadingKind, WorkbenchData, readingKindLabels } from "./domain";
import { buildInnovationPlatformPrompt, buildPlatformPrompt } from "./promptBuilder";
import { WORKBENCH_POLL_INTERVAL_MS, emptyWorkbenchData, loadWorkbenchData } from "./workbenchData";
import { MarkdownReader } from "./MarkdownReader";

const cardIcons: Record<ReadingKind, ReactNode> = {
  plain: <BookOpen aria-hidden="true" />,
  expert: <Brain aria-hidden="true" />,
  reproduction: <Code2 aria-hidden="true" />
};

const platforms: Platform[] = ["Codex", "Claude Code", "OpenClaw"];

function categoriesFor(items: Paper[]) {
  return ["全部论文", ...Array.from(new Set(items.map((paper) => paper.category))), "创新挖掘"];
}

function EmptyWorkspace({ workspace, error }: { workspace: string; error?: string }) {
  return (
    <section className="empty-workspace" aria-label="空工作区">
      <h2>还没有可视化论文数据</h2>
      <p>{workspace ? `当前工作区：${workspace}` : "请先在论文工作区导入论文或刷新 Web 数据。"}</p>
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}

function PlatformRequestBox({
  paper,
  card
}: {
  paper: Paper;
  card: ReadingCard;
}) {
  const [platform, setPlatform] = useState<Platform>("Codex");
  const [message, setMessage] = useState("");
  const [prompt, setPrompt] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanMessage = message.trim() || "请基于当前阅读卡继续优化，生成更清楚的新版本。";
    setPrompt(buildPlatformPrompt({ platform, paper, card, message: cleanMessage }));
  }

  return (
    <section className="reader-action-panel">
      <form className="card-chat" onSubmit={submit}>
        <label>
          平台
          <select value={platform} onChange={(event) => setPlatform(event.target.value as Platform)}>
            {platforms.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          优化请求
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={`${readingKindLabels[card.kind]}再详细一点，保留旧版本并生成新版本`}
          />
        </label>
        <button type="submit">
          <MessageSquare aria-hidden="true" />
          生成平台请求
        </button>
      </form>

      {prompt && (
        <pre className="prompt-preview" aria-label={`${readingKindLabels[card.kind]}平台请求`}>
          {prompt}
        </pre>
      )}
    </section>
  );
}

function InnovationRequestBox({ idea }: { idea: InnovationIdea }) {
  const [platform, setPlatform] = useState<Platform>("Codex");
  const [message, setMessage] = useState("");
  const [prompt, setPrompt] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleanMessage = message.trim() || "请基于当前知识库继续优化这个创新点，并重新给出合理性排序。";
    setPrompt(buildInnovationPlatformPrompt({ platform, idea, message: cleanMessage }));
  }

  return (
    <section className="reader-action-panel">
      <form className="card-chat" onSubmit={submit}>
        <label>
          平台
          <select value={platform} onChange={(event) => setPlatform(event.target.value as Platform)}>
            {platforms.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </label>
        <label>
          优化请求
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="继续挖掘这个创新点，补充可行性、风险和与知识库论文的关系"
          />
        </label>
        <button type="submit">
          <MessageSquare aria-hidden="true" />
          生成平台请求
        </button>
      </form>

      {prompt && (
        <pre className="prompt-preview" aria-label="创新挖掘平台请求">
          {prompt}
        </pre>
      )}
    </section>
  );
}

function ReadingEntryBoard({
  paper,
  onOpen
}: {
  paper: Paper;
  onOpen: (kind: ReadingKind) => void;
}) {
  return (
    <section className="reading-entry-board" aria-label="阅读入口">
      {(["plain", "expert", "reproduction"] as ReadingKind[]).map((kind) => {
        const card = paper.cards[kind];
        return (
          <button key={kind} type="button" className="reading-entry-button" onClick={() => onOpen(kind)}>
            <span className="card-icon">{cardIcons[kind]}</span>
            <span>
              <small>{readingKindLabels[kind]}</small>
              <strong>{card.title}</strong>
              <em>{card.summary}</em>
            </span>
            <FileText aria-hidden="true" />
          </button>
        );
      })}
    </section>
  );
}

function DocumentReaderView({
  paper,
  card,
  onBack
}: {
  paper: Paper;
  card: ReadingCard;
  onBack: () => void;
}) {
  const markdown = card.markdown?.trim() || `# ${card.title}\n\n${card.summary}\n\n${card.bullets.map((item) => `- ${item}`).join("\n")}`;
  return (
    <article className="document-view">
      <header className="document-toolbar">
        <button type="button" onClick={onBack}>
          <ArrowLeft aria-hidden="true" />
          返回论文详情
        </button>
        <div>
          <p>{paper.title}</p>
          <h3>{readingKindLabels[card.kind]}：{card.title}</h3>
        </div>
      </header>
      <div className="document-meta">
        <span>{card.version}</span>
        <span>{card.updatedAt || "等待生成"}</span>
        <code>{card.artifactPath}</code>
      </div>
      <MarkdownReader markdown={markdown} />
      <PlatformRequestBox paper={paper} card={card} />
    </article>
  );
}

function InnovationReaderView({
  idea,
  papersById,
  onBack,
  onSelectPaper
}: {
  idea: InnovationIdea;
  papersById: Map<string, Paper>;
  onBack: () => void;
  onSelectPaper: (paper: Paper, kind?: ReadingKind) => void;
}) {
  const markdown = idea.markdown?.trim() || `# ${idea.title}\n\n${idea.summary}`;
  return (
    <article className="document-view">
      <header className="document-toolbar">
        <button type="button" onClick={onBack}>
          <ArrowLeft aria-hidden="true" />
          返回创新挖掘
        </button>
        <div>
          <p>合理性分数 {idea.score} · 排名 #{idea.rank}</p>
          <h3>创新挖掘：{idea.title}</h3>
        </div>
      </header>
      <div className="document-meta">
        <span>score {idea.score}</span>
        <span>rank #{idea.rank}</span>
        <code>{idea.artifactPath}</code>
      </div>
      <MarkdownReader markdown={markdown} />
      <section className="reader-action-panel" aria-label="创新来源">
        <div className="source-list">
          {idea.sources.map((source) => {
            const paper = papersById.get(source.paperId);
            return (
              <button
                key={`${source.paperId}-${source.cardKind}`}
                type="button"
                onClick={() => paper && onSelectPaper(paper, source.cardKind)}
              >
                <Network aria-hidden="true" />
                <span>{paper?.title ?? source.paperId}</span>
                <small>{readingKindLabels[source.cardKind]}：{source.note}</small>
              </button>
            );
          })}
        </div>
      </section>
      <InnovationRequestBox idea={idea} />
    </article>
  );
}

function InnovationBoard({
  ideas,
  papersById,
  onSelectPaper,
  onOpenIdea
}: {
  ideas: InnovationIdea[];
  papersById: Map<string, Paper>;
  onSelectPaper: (paper: Paper, kind?: ReadingKind) => void;
  onOpenIdea: (idea: InnovationIdea) => void;
}) {
  return (
    <section className="innovation-board" aria-label="创新挖掘">
      {ideas.map((idea) => (
        <article className="innovation-card" key={idea.id}>
          <div className="rank-badge">#{idea.rank}</div>
          <div>
            <h3>{idea.title}</h3>
            <p>{idea.summary}</p>
            <div className="score-row">
              <span>合理性分数</span>
              <strong>{idea.score}</strong>
            </div>
            <button className="open-innovation-button" type="button" onClick={() => onOpenIdea(idea)}>
              <FileText aria-hidden="true" />
              阅读创新文档
            </button>
            <div className="source-list">
              {idea.sources.map((source) => {
                const paper = papersById.get(source.paperId);
                return (
                  <button
                    key={`${source.paperId}-${source.cardKind}`}
                    type="button"
                    onClick={() => paper && onSelectPaper(paper, source.cardKind)}
                  >
                    <Network aria-hidden="true" />
                    <span>{paper?.title ?? source.paperId}</span>
                    <small>{readingKindLabels[source.cardKind]}：{source.note}</small>
                  </button>
                );
              })}
            </div>
            <code>{idea.artifactPath}</code>
          </div>
        </article>
      ))}
    </section>
  );
}

export default function App() {
  const [liveData, setLiveData] = useState<WorkbenchData>(() => emptyWorkbenchData());
  const [hasLoadedWorkspaceData, setHasLoadedWorkspaceData] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [activeCategory, setActiveCategory] = useState("全部论文");
  const [selectedPaperId, setSelectedPaperId] = useState("");
  const [activeReaderKind, setActiveReaderKind] = useState<ReadingKind | null>(null);
  const [activeInnovationId, setActiveInnovationId] = useState("");
  const papers = liveData.papers;
  const innovations = liveData.innovations;
  const hasRealWorkspaceContent = hasLoadedWorkspaceData && (liveData.papers.length > 0 || liveData.innovations.length > 0);
  const categories = useMemo(() => categoriesFor(papers), [papers]);
  const papersById = useMemo(() => new Map(papers.map((paper) => [paper.id, paper])), [papers]);
  const filteredPapers = activeCategory === "全部论文" || activeCategory === "创新挖掘"
    ? papers
    : papers.filter((paper) => paper.category === activeCategory);
  const currentPaper = papersById.get(selectedPaperId);
  const activeInnovation = innovations.find((idea) => idea.id === activeInnovationId);
  const selectedPaper =
    currentPaper && filteredPapers.some((paper) => paper.id === currentPaper.id)
      ? currentPaper
      : filteredPapers[0] ?? papers[0];

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      try {
        const data = await loadWorkbenchData();
        if (!cancelled) {
          setLiveData(data);
          setHasLoadedWorkspaceData(true);
          setLoadError("");
        }
      } catch {
        if (!cancelled) {
          setHasLoadedWorkspaceData(true);
          setLoadError("无法读取 paper-workbench-data.json，请运行 refresh-data 后重试。");
        }
      }
    }

    void refresh();
    const timer = window.setInterval(refresh, WORKBENCH_POLL_INTERVAL_MS);
    window.addEventListener("focus", refresh);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
      window.removeEventListener("focus", refresh);
    };
  }, []);

  useEffect(() => {
    if (!papersById.has(selectedPaperId) && papers[0]) {
      setSelectedPaperId(papers[0].id);
      setActiveReaderKind(null);
    }
    if (selectedPaperId && !papersById.has(selectedPaperId) && !papers[0]) {
      setSelectedPaperId("");
      setActiveReaderKind(null);
    }
  }, [papers, papersById, selectedPaperId]);

  useEffect(() => {
    if (!categories.includes(activeCategory)) {
      setActiveCategory("全部论文");
    }
  }, [activeCategory, categories]);

  function selectPaper(paper: Paper, kind?: ReadingKind) {
    setSelectedPaperId(paper.id);
    setActiveCategory(paper.category);
    setActiveReaderKind(kind ?? null);
  }

  return (
    <main className="workbench-shell">
      <aside className="sidebar" aria-label="论文分类">
        <div className="brand-block">
          <Lightbulb aria-hidden="true" />
          <div>
            <h1>论文阅读工作台</h1>
            <p>Paper Research Workflow</p>
          </div>
        </div>
        <div className="search-box">
          <Search aria-hidden="true" />
          <span>分类与创新线索</span>
        </div>
        <nav className="category-list">
          {categories.map((category) => (
            <button
              key={category}
              type="button"
              className={category === activeCategory ? "active" : ""}
              onClick={() => {
                setActiveCategory(category);
                setActiveReaderKind(null);
                setActiveInnovationId("");
              }}
            >
              {category}
            </button>
          ))}
        </nav>
      </aside>

      <section className="content-area">
        <header className="workspace-header">
          <div>
            <p>{activeCategory}</p>
            <h2>{activeCategory === "创新挖掘" ? "创新挖掘与来源追踪" : selectedPaper?.title ?? "等待论文数据"}</h2>
          </div>
          <span>{filteredPapers.length} 篇论文</span>
        </header>

        {!hasRealWorkspaceContent && hasLoadedWorkspaceData ? (
          <EmptyWorkspace workspace={liveData.workspace} error={loadError} />
        ) : activeCategory === "创新挖掘" && activeInnovation ? (
          <InnovationReaderView
            idea={activeInnovation}
            papersById={papersById}
            onBack={() => setActiveInnovationId("")}
            onSelectPaper={(paper, kind) => {
              setActiveInnovationId("");
              selectPaper(paper, kind);
            }}
          />
        ) : activeCategory === "创新挖掘" ? (
          <InnovationBoard
            ideas={innovations}
            papersById={papersById}
            onSelectPaper={(paper, kind) => {
              setActiveInnovationId("");
              selectPaper(paper, kind);
            }}
            onOpenIdea={(idea) => setActiveInnovationId(idea.id)}
          />
        ) : selectedPaper && activeReaderKind ? (
          <DocumentReaderView
            paper={selectedPaper}
            card={selectedPaper.cards[activeReaderKind]}
            onBack={() => setActiveReaderKind(null)}
          />
        ) : (
          <>
            <div className="paper-strip" aria-label="分类论文">
              {filteredPapers.map((paper) => (
                <button
                  key={paper.id}
                  type="button"
                  className={paper.id === selectedPaper.id ? "selected" : ""}
                  onClick={() => {
                    setSelectedPaperId(paper.id);
                    setActiveReaderKind(null);
                    setActiveInnovationId("");
                  }}
                >
                  <strong>{paper.title}</strong>
                  <span>{paper.year} · {paper.tags.join(" / ")}</span>
                </button>
              ))}
            </div>

            {selectedPaper && <ReadingEntryBoard paper={selectedPaper} onOpen={setActiveReaderKind} />}
          </>
        )}
      </section>
    </main>
  );
}
