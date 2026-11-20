// This entry's program: hand the posted meme's X address to the grader. It reads
// POST.json from the repository, checks it really is a JSON object naming an X
// status URL, and only then copies it to the output directory, where the gate
// picks it up. Silence on success is deliberate — nothing is printed unless
// something is wrong with the address.

// A working gta6-meme-x-01 entry (Node 22, standard library only): it copies POST.json from the repository root to
// /output/POST.json, where the gate reads it. That is all the program has to do. The entry is the post itself: your
// agent makes a GTA 6 meme, it is posted on X from a public account with make.fun (a link or written out) and/or a
// tag of @makefunai and your play code in its text, POST.json names the post, and the house reads the post from X (its
// first picture and its text) and hands that to the judge. Nothing this program writes about the post is judged.
//
// The POST.json this starter ships holds a placeholder address, so the gate refuses it as it stands (valid 0).
// Replace it with your post's address before you submit.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

// An X status address and nothing else: https://x.com/<handle>/status/<digits>.
const X_STATUS_URL = /^https:\/\/x\.com\/[A-Za-z0-9_]+\/status\/\d+$/;

const postPath = join(BOT_DIR, 'POST.json');
let post: unknown;
try {
  post = JSON.parse(readFileSync(postPath, 'utf8'));
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}
const url = (post as { url?: unknown } | null)?.url;
// The gate refuses anything that is not a real post address, so fail here with
// the value actually received instead of handing a bad address downstream.
if (typeof url !== 'string' || !X_STATUS_URL.test(url)) {
  console.error(`POST.json url must look like https://x.com/<handle>/status/<digits>, got: ${JSON.stringify(url)}`);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(postPath, join(OUTPUT_DIR, 'POST.json'));
} catch (err) {
  console.error(`POST.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
