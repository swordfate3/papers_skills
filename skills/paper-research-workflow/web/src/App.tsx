import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { BookOpen, Brain, Code2, Lightbulb, MessageSquare, Network, Search } from "lucide-react";
import { InnovationIdea, Paper, Platform, ReadingCard, ReadingKind, WorkbenchData, readingKindLabels } from "./domain";
import { sampleWorkbenchData } from "./sampleData";
import { buildPlatformPrompt } from "./promptBuilder";
import { WORKBENCH_POLL_INTERVAL_MS, dataOrSample, loadWorkbenchData } from "./workbenchData";

const cardIcons: Record<ReadingKind, ReactNode> = {
  plain: <BookOpen aria-hidden="true" />,
  expert: <Brain aria-hidden="true" />,
  reproduction: <Code2 aria-hidden="true" />
};

const platforms: Platform[] = ["Codex", "Claude Code", "OpenClaw"];

function categoriesFor(items: Paper[]) {
  return ["全部论文", ...Array.from(new Set(items.map((paper) => paper.category))), "创新挖掘"];
}

function EmptyWorkspace({ workspace }: { workspace: string }) {
  return (
    <section className="empty-workspace" aria-label="空工作区">
      <h2>还没有可视化论文数据</h2>
      <p>{workspace ? `当前工作区：${workspace}` : "请先在论文工作区导入论文或刷新 Web 数据。"}</p>
    </section>
  );
}

function ReadingPanel({
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
    <article className="reading-card" aria-label={readingKindLabels[card.kind]}>
      <header className="card-header">
        <span className="card-icon">{cardIcons[card.kind]}</span>
        <div>
          <p className="card-kicker">{readingKindLabels[card.kind]}</p>
          <h3>{card.title}</h3>
        </div>
      </header>

      <p className="card-summary">{card.summary}</p>

      <ul className="insight-list">
        {card.bullets.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>

      <div className="artifact-line">
        <span>{card.version}</span>
        <span>{card.updatedAt}</span>
      </div>
      <code>{card.artifactPath}</code>

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
    </article>
  );
}

function InnovationBoard({
  ideas,
  papersById,
  onSelectPaper
}: {
  ideas: InnovationIdea[];
  papersById: Map<string, Paper>;
  onSelectPaper: (paper: Paper) => void;
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
            <div className="source-list">
              {idea.sources.map((source) => {
                const paper = papersById.get(source.paperId);
                return (
                  <button
                    key={`${source.paperId}-${source.cardKind}`}
                    type="button"
                    onClick={() => paper && onSelectPaper(paper)}
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
  const [liveData, setLiveData] = useState<WorkbenchData>(sampleWorkbenchData);
  const [hasLoadedWorkspaceData, setHasLoadedWorkspaceData] = useState(false);
  const [activeCategory, setActiveCategory] = useState("全部论文");
  const [selectedPaperId, setSelectedPaperId] = useState(sampleWorkbenchData.papers[0].id);
  const displayData = useMemo(
    () => (hasLoadedWorkspaceData ? liveData : dataOrSample(liveData)),
    [hasLoadedWorkspaceData, liveData]
  );
  const papers = displayData.papers;
  const innovations = displayData.innovations;
  const hasRealWorkspaceContent = hasLoadedWorkspaceData && (liveData.papers.length > 0 || liveData.innovations.length > 0);
  const categories = useMemo(() => categoriesFor(papers), [papers]);
  const papersById = useMemo(() => new Map(papers.map((paper) => [paper.id, paper])), [papers]);
  const filteredPapers = activeCategory === "全部论文" || activeCategory === "创新挖掘"
    ? papers
    : papers.filter((paper) => paper.category === activeCategory);
  const currentPaper = papersById.get(selectedPaperId);
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
        }
      } catch {
        if (!cancelled) {
          setHasLoadedWorkspaceData(false);
        }
      }
    }

    void refresh();
    const timer = window.setInterval(refresh, WORKBENCH_POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!papersById.has(selectedPaperId) && papers[0]) {
      setSelectedPaperId(papers[0].id);
    }
  }, [papers, papersById, selectedPaperId]);

  useEffect(() => {
    if (!categories.includes(activeCategory)) {
      setActiveCategory("全部论文");
    }
  }, [activeCategory, categories]);

  function selectPaper(paper: Paper) {
    setSelectedPaperId(paper.id);
    setActiveCategory(paper.category);
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
              onClick={() => setActiveCategory(category)}
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
          <EmptyWorkspace workspace={liveData.workspace} />
        ) : activeCategory === "创新挖掘" ? (
          <InnovationBoard ideas={innovations} papersById={papersById} onSelectPaper={selectPaper} />
        ) : (
          <>
            <div className="paper-strip" aria-label="分类论文">
              {filteredPapers.map((paper) => (
                <button
                  key={paper.id}
                  type="button"
                  className={paper.id === selectedPaper.id ? "selected" : ""}
                  onClick={() => setSelectedPaperId(paper.id)}
                >
                  <strong>{paper.title}</strong>
                  <span>{paper.year} · {paper.tags.join(" / ")}</span>
                </button>
              ))}
            </div>

            <section className="reading-grid" aria-label="三列阅读卡">
              {selectedPaper && (["plain", "expert", "reproduction"] as ReadingKind[]).map((kind) => (
                <ReadingPanel key={kind} paper={selectedPaper} card={selectedPaper.cards[kind]} />
              ))}
            </section>
          </>
        )}
      </section>
    </main>
  );
}
