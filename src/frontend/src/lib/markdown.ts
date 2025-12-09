import MarkdownIt from "markdown-it";

// Initialize markdown-it with safe defaults
// XSS protection is built-in (no HTML tags allowed by default)
const md = new MarkdownIt({
  html: false, // Disable HTML tags for security
  breaks: true, // Convert line breaks to <br>
  linkify: false, // Don't auto-convert URLs to links (not needed for recipe instructions)
});

/**
 * Render markdown text to HTML.
 * Supports inline formatting: **bold**, *italics*, `code`
 * Line breaks are converted to <br> tags.
 */
export function renderMarkdown(text: string): string {
  return md.render(text);
}
