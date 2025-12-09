import { describe, it, expect } from "vitest";
import { renderMarkdown } from "./markdown";

describe("renderMarkdown", () => {
  it("renders bold text", () => {
    const input = "**bold text**";
    const output = renderMarkdown(input);
    expect(output).toContain("<strong>bold text</strong>");
  });

  it("renders italic text", () => {
    const input = "*italic text*";
    const output = renderMarkdown(input);
    expect(output).toContain("<em>italic text</em>");
  });

  it("renders inline code", () => {
    const input = "`code snippet`";
    const output = renderMarkdown(input);
    expect(output).toContain("<code>code snippet</code>");
  });

  it("converts line breaks to <br> tags", () => {
    const input = "Line 1\nLine 2";
    const output = renderMarkdown(input);
    expect(output).toContain("<br>");
  });

  it("handles mixed formatting", () => {
    const input = "Mix **bold** and *italic* with `code`";
    const output = renderMarkdown(input);
    expect(output).toContain("<strong>bold</strong>");
    expect(output).toContain("<em>italic</em>");
    expect(output).toContain("<code>code</code>");
  });

  it("escapes HTML tags for security", () => {
    const input = '<script>alert("xss")</script>';
    const output = renderMarkdown(input);
    // HTML should be escaped, not rendered
    expect(output).not.toContain("<script>");
    expect(output).toContain("&lt;script&gt;");
  });
});
