#!/usr/bin/env node

import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CARDS_DIR = path.join(ROOT, 'cards');
const OUT_FILE = path.join(ROOT, 'data', 'flashcards.json');

const REQUIRED_FIELDS = [
  'id',
  'title',
  'technologies',
  'areas',
  'tags',
  'difficulty',
  'question',
];

async function listMarkdownFiles(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = await Promise.all(entries.map(async (entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) return listMarkdownFiles(fullPath);
    if (entry.isFile() && entry.name.endsWith('.md')) return [fullPath];
    return [];
  }));

  return files.flat().sort();
}

function parseFrontmatter(source, filePath) {
  const match = source.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) {
    throw new Error(`${filePath}: missing YAML frontmatter block`);
  }

  const meta = {};
  for (const rawLine of match[1].split('\n')) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;

    const delimiter = line.indexOf(':');
    if (delimiter === -1) {
      throw new Error(`${filePath}: invalid frontmatter line "${rawLine}"`);
    }

    const key = line.slice(0, delimiter).trim();
    const rawValue = line.slice(delimiter + 1).trim();
    meta[key] = parseYamlValue(rawValue);
  }

  return { meta, body: match[2].trim() };
}

function parseYamlValue(rawValue) {
  if (rawValue.startsWith('[') && rawValue.endsWith(']')) {
    const inner = rawValue.slice(1, -1).trim();
    if (!inner) return [];
    return inner.split(',').map((item) => unquote(item.trim())).filter(Boolean);
  }

  return unquote(rawValue);
}

function unquote(value) {
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }

  return value;
}

function validateCard(card, filePath, seenIds) {
  const errors = [];

  for (const field of REQUIRED_FIELDS) {
    if (!(field in card) || card[field] === '' || card[field]?.length === 0) {
      errors.push(`missing ${field}`);
    }
  }

  for (const field of ['technologies', 'areas', 'tags']) {
    if (!Array.isArray(card[field])) {
      errors.push(`${field} must be an inline array`);
    } else {
      for (const value of card[field]) {
        if (!/^[a-z0-9][a-z0-9-]*$/.test(value)) {
          errors.push(`${field} contains invalid slug "${value}"`);
        }
      }
    }
  }

  if (card.difficulty && !/^[a-z0-9][a-z0-9-]*$/.test(card.difficulty)) {
    errors.push(`difficulty contains invalid slug "${card.difficulty}"`);
  }

  if (seenIds.has(card.id)) {
    errors.push(`duplicate id "${card.id}"`);
  }

  if (!card.answerHtml || !card.answerMarkdown.trim()) {
    errors.push('empty answer body');
  }

  if (!/^[a-z0-9][a-z0-9.-]*$/.test(card.id ?? '')) {
    errors.push('id must use lowercase letters, numbers, dots, or hyphens');
  }

  if (errors.length > 0) {
    throw new Error(`${filePath}: ${errors.join(', ')}`);
  }

  seenIds.add(card.id);
}

function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  const html = [];
  let paragraph = [];
  let listItems = [];
  let codeLines = [];
  let inCode = false;

  function flushParagraph() {
    if (paragraph.length === 0) return;
    html.push(`<p>${renderInline(paragraph.join(' '))}</p>`);
    paragraph = [];
  }

  function flushList() {
    if (listItems.length === 0) return;
    html.push(`<ul>${listItems.map((item) => `<li>${renderInline(item)}</li>`).join('')}</ul>`);
    listItems = [];
  }

  function flushCode() {
    if (codeLines.length === 0) return;
    html.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
    codeLines = [];
  }

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushParagraph();
        flushList();
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = line.match(/^(#{2,4})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
      continue;
    }

    const listItem = line.match(/^\s*[-*]\s+(.+)$/);
    if (listItem) {
      flushParagraph();
      listItems.push(listItem[1]);
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }

  flushParagraph();
  flushList();
  flushCode();

  return html.join('\n');
}

function renderInline(value) {
  return escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>');
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function titleize(value) {
  const acronyms = new Map([
    ['aws', 'AWS'],
    ['ci', 'CI'],
    ['cicd', 'CI/CD'],
    ['eks', 'EKS'],
    ['hcl', 'HCL'],
    ['hcp', 'HCP'],
    ['hpa', 'HPA'],
    ['iam', 'IAM'],
    ['id', 'ID'],
    ['oidc', 'OIDC'],
    ['s3', 'S3'],
    ['sts', 'STS'],
    ['vpc', 'VPC'],
  ]);

  if (acronyms.has(value)) return acronyms.get(value);

  return value
    .split(/[-_]/)
    .map((part) => acronyms.get(part) || part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

async function main() {
  const files = await listMarkdownFiles(CARDS_DIR);
  const seenIds = new Set();
  const cards = [];

  for (const file of files) {
    const source = await readFile(file, 'utf8');
    const { meta, body } = parseFrontmatter(source, path.relative(ROOT, file));
    const relPath = path.relative(ROOT, file);
    const card = {
      ...meta,
      source: relPath,
      answerMarkdown: body,
      answerHtml: renderMarkdown(body),
    };

    validateCard(card, relPath, seenIds);
    cards.push(card);
  }

  const technologyMap = new Map();
  const areaMap = new Map();
  const tagMap = new Map();
  const difficultyMap = new Map();

  for (const card of cards) {
    card.technologies.forEach((item) => technologyMap.set(item, titleize(item)));
    card.areas.forEach((item) => areaMap.set(item, titleize(item)));
    card.tags.forEach((item) => tagMap.set(item, titleize(item)));
    difficultyMap.set(card.difficulty, titleize(card.difficulty));
  }

  const manifest = {
    cardCount: cards.length,
    technologies: [...technologyMap.entries()].map(([id, label]) => ({ id, label })).sort(byId),
    areas: [...areaMap.entries()].map(([id, label]) => ({ id, label })).sort(byId),
    tags: [...tagMap.entries()].map(([id, label]) => ({ id, label })).sort(byId),
    difficulties: [...difficultyMap.entries()].map(([id, label]) => ({ id, label })).sort(byId),
    cards,
  };

  await mkdir(path.dirname(OUT_FILE), { recursive: true });
  await writeFile(OUT_FILE, `${JSON.stringify(manifest, null, 2)}\n`);

  console.log(`Generated ${path.relative(ROOT, OUT_FILE)} with ${cards.length} cards.`);
}

function byId(a, b) {
  return a.id.localeCompare(b.id);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
