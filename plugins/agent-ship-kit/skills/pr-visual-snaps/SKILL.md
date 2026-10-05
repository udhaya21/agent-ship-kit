---
name: pr-visual-snaps
description: Capture component-level before/after screenshots of two deployed URLs (base vs head), build side-by-side composites, and open or update a GitHub PR with a Before/After table. Use when comparing a branch against its base visually, generating before/after snaps for a PR, doing visual-regression review of UI changes, or when given two branches or two deployment URLs to compare via screenshots.
---

# PR Visual Snaps

Compare two deployments, **base = before** and **head = after**, at the component level and produce a PR Before/After table. Capture with whatever browser automation your tool has (in Claude Code: the chrome-devtools MCP or Claude in Chrome; Playwright works in any tool). Crop and compose with Node (`pngjs`), open the PR with `gh`.

## Inputs (ask if not given)

- head branch and its deployed URL (after)
- base branch and its deployed URL (before)
- the page or route to compare (same path on both)
- which components to capture: derive them from the diff (REFERENCE → Coverage)

## Quick start

1. Scratch dir: `npm i pngjs pixelmatch` once, copy `scripts/*.mjs` in, make `raw comp/before comp/after`.
2. `git diff <base>...HEAD --stat`, read the source diff, map every visual change to a component. List what you will and won't snap.
3. For EACH deployment, at a FIXED viewport: navigate, settle, then per component: rect, scroll, capture, crop.
4. `node sxs.mjs` → per-component `before|after` composites in `comp/sxs/`.
5. `gh pr create --base <base> --head <head> -t "..." -F body.md`, then embed images (see Images).

## Capture loop, per component, per deployment

- Fix the viewport (for example 1440×900) and keep it identical on both sides.
- Wait for text that only appears after async data loads, and settle BOTH sides to the **same data** (same account, same records, same counts) or the diff is noise.
- Get the component's CSS rect with a page script (walk the DOM up to its card or container).
- `el.scrollIntoView({block:'center'})`, then **screenshot twice and keep the second**: the capture can lag one frame behind the scroll.
- `node crop.mjs <shot.png> <xCss> <yCss> <wCss> <hCss> <out.png> [dpr]` (CSS px; dpr default 2).
- Read the crop back to confirm the region. Crop from the measured rect, never from eyeballed offsets.

## Images (the part that bites)

`gh` **cannot** upload to GitHub's attachment CDN, and on **private** repos `raw.githubusercontent`, blob and release URLs render broken (the image proxy cannot authenticate). The attachment CDN is the only source that renders inline there. Two ways to populate it:

- **Automate the browser (preferred):** in a logged-in browser session, open the PR, upload each PNG into the comment editor's hidden `<input type="file">`, let GitHub insert `![](.../user-attachments/...)`, read the URLs back, then build the table. See REFERENCE → Uploading images.
- **Manual fallback:** open the `comp/sxs` folder; the user drag-drops into the PR editor; `gh pr view --json body` reads the uploaded URLs back to wire into the table.

Public repos can skip all of this: commit the PNGs to a branch and use raw URLs.

## Then

Build the table (1 column of `sxs/*` = fewer uploads, or 2 columns of `before/*` + `after/*`). Re-apply with `gh pr edit <n> -F body.md`, then verify 0 placeholders and the expected image count remain.

Full recipe, gotchas and a worked example: [REFERENCE.md](REFERENCE.md).
