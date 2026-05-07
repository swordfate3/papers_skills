import { ReactElement } from "react";

function escapeHtml(text: string) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function inlineFormat(text: string) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function blockFor(lines: string[], index: number): { element: ReactElement; next: number } {
  const line = lines[index];
  const trimmed = line.trim();

  if (!trimmed) {
    return { element: <div className="md-space" key={index} />, next: index + 1 };
  }

  if (trimmed.startsWith("```")) {
    const codeLines: string[] = [];
    let cursor = index + 1;
    while (cursor < lines.length && !lines[cursor].trim().startsWith("```")) {
      codeLines.push(lines[cursor]);
      cursor += 1;
    }
    return {
      element: <pre className="md-code-block" key={index}><code>{codeLines.join("\n")}</code></pre>,
      next: Math.min(cursor + 1, lines.length)
    };
  }

  if (trimmed.startsWith("#")) {
    const level = Math.min(trimmed.match(/^#+/)?.[0].length ?? 1, 3);
    const text = trimmed.replace(/^#+\s*/, "");
    const Tag = `h${level}` as keyof JSX.IntrinsicElements;
    return {
      element: <Tag key={index} dangerouslySetInnerHTML={{ __html: inlineFormat(text) }} />,
      next: index + 1
    };
  }

  if (trimmed.startsWith(">")) {
    return {
      element: <blockquote key={index} dangerouslySetInnerHTML={{ __html: inlineFormat(trimmed.replace(/^>\s*/, "")) }} />,
      next: index + 1
    };
  }

  if (/^[-*]\s+/.test(trimmed)) {
    const items: string[] = [];
    let cursor = index;
    while (cursor < lines.length && /^[-*]\s+/.test(lines[cursor].trim())) {
      items.push(lines[cursor].trim().replace(/^[-*]\s+/, ""));
      cursor += 1;
    }
    return {
      element: (
        <ul key={index}>
          {items.map((item, itemIndex) => (
            <li key={`${index}-${itemIndex}`} dangerouslySetInnerHTML={{ __html: inlineFormat(item) }} />
          ))}
        </ul>
      ),
      next: cursor
    };
  }

  if (trimmed.includes("|") && index + 1 < lines.length && /^\s*\|?\s*:?-{3,}:?\s*\|/.test(lines[index + 1])) {
    const rows: string[] = [];
    let cursor = index;
    while (cursor < lines.length && lines[cursor].includes("|")) {
      rows.push(lines[cursor]);
      cursor += 1;
    }
    const [header, , ...body] = rows;
    const cellsFor = (row: string) => row.split("|").map((cell) => cell.trim()).filter(Boolean);
    return {
      element: (
        <table key={index}>
          <thead>
            <tr>{cellsFor(header).map((cell) => <th key={cell}>{cell}</th>)}</tr>
          </thead>
          <tbody>
            {body.map((row, rowIndex) => (
              <tr key={`${index}-${rowIndex}`}>{cellsFor(row).map((cell) => <td key={cell}>{cell}</td>)}</tr>
            ))}
          </tbody>
        </table>
      ),
      next: cursor
    };
  }

  const paragraph: string[] = [];
  let cursor = index;
  while (
    cursor < lines.length &&
    lines[cursor].trim() &&
    !lines[cursor].trim().startsWith("#") &&
    !lines[cursor].trim().startsWith(">") &&
    !lines[cursor].trim().startsWith("```") &&
    !/^[-*]\s+/.test(lines[cursor].trim())
  ) {
    paragraph.push(lines[cursor].trim());
    cursor += 1;
  }
  return {
    element: <p key={index} dangerouslySetInnerHTML={{ __html: inlineFormat(paragraph.join(" ")) }} />,
    next: cursor
  };
}

export function MarkdownReader({ markdown }: { markdown: string }) {
  const lines = markdown.split(/\r?\n/);
  const elements: ReactElement[] = [];
  let index = 0;
  while (index < lines.length) {
    const block = blockFor(lines, index);
    elements.push(block.element);
    index = block.next;
  }
  return <div className="markdown-reader" aria-label="Markdown 文档阅读器">{elements}</div>;
}
