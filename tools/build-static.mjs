#!/usr/bin/env node

import { cp, mkdir, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT_DIR = path.join(ROOT, 'dist');

await rm(OUT_DIR, { recursive: true, force: true });
await mkdir(path.join(OUT_DIR, 'data'), { recursive: true });

await cp(path.join(ROOT, 'index.html'), path.join(OUT_DIR, 'index.html'));
await cp(path.join(ROOT, 'data', 'flashcards.json'), path.join(OUT_DIR, 'data', 'flashcards.json'));

console.log(`Built ${path.relative(ROOT, OUT_DIR)}/`);
