#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MANIFEST_FILE = path.join(ROOT, 'data', 'flashcards.json');
const ZERO_SHA = /^0+$/;

const previousRef = process.env.PREVIOUS_REF?.trim();
const refs = [
  previousRef && !ZERO_SHA.test(previousRef) ? previousRef : null,
  'HEAD^',
].filter(Boolean);

const manifest = JSON.parse(await readFile(MANIFEST_FILE, 'utf8'));
const previousManifest = readPreviousManifest(refs);

if (!previousManifest) {
  manifest.newCardCount = 0;
  manifest.cards = manifest.cards.map(({ isNew, ...card }) => card);
  await writeManifest(manifest);
  console.log('No previous manifest found; no cards marked as new.');
  process.exit(0);
}

const previousIds = new Set((previousManifest.cards || []).map((card) => card.id));
let newCardCount = 0;

manifest.cards = manifest.cards.map(({ isNew, ...card }) => {
  const cardIsNew = !previousIds.has(card.id);
  if (cardIsNew) newCardCount += 1;
  return cardIsNew ? { ...card, isNew: true } : card;
});

manifest.newCardCount = newCardCount;
await writeManifest(manifest);

console.log(`Marked ${newCardCount} new card${newCardCount === 1 ? '' : 's'}.`);

function readPreviousManifest(refsToTry) {
  for (const ref of refsToTry) {
    try {
      const source = execFileSync('git', ['show', `${ref}:data/flashcards.json`], {
        cwd: ROOT,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'ignore'],
      });
      return JSON.parse(source);
    } catch {
      // Try the next candidate ref.
    }
  }

  return null;
}

async function writeManifest(value) {
  await writeFile(MANIFEST_FILE, `${JSON.stringify(value, null, 2)}\n`);
}
