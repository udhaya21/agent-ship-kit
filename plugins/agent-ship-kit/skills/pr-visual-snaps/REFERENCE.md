# PR Visual Snaps: Reference

Detailed recipe, gotchas and a worked example. Pairs with `SKILL.md` and `scripts/`.

## 0. Setup

```bash
SNAPS=$(mktemp -d) && cd "$SNAPS"
npm i pngjs pixelmatch            # crop/compose/diff deps (Node 18+)
cp <skill-dir>/scripts/*.mjs .
mkdir -p raw comp/before comp/after
```

The browser steps below are named by action (navigate, resize, wait for text, run a page script, screenshot, upload a file). Map each to your automation tool: chrome-devtools MCP (`navigate_page`, `resize_page`, `wait_for`, `evaluate_script`, `take_screenshot`, `upload_file`), Claude in Chrome, or Playwright (`page.goto`, `page.setViewportSize`, `page.getByText().waitFor()`, `page.evaluate`, `page.screenshot`, `setInputFiles`).

## 1. Coverage: decide what to snap

```bash
git fetch origin <base>
git diff <base>...HEAD --stat                 # the files the PR touches
git --no-pager diff <base>...HEAD -- '**/*.tsx' '**/*.ts' ':(exclude)*.test.*' > "$SNAPS/srcdiff.txt"
```

Read the source diff and **map every visual change to a component**. Then split into:

- **Will snap**: components with a visible delta given the page's current data.
- **Won't snap (with reason)**: interaction-only popovers and modals, empty states absent for this data, and non-visual changes (accessibility tree, keyboard focus, reduced motion, refactors). List these in the PR so reviewers know they were considered.

This step is the difference between "screenshotted the obvious bits" and "covered the diff".

## 2. Settle both deployments to identical state

Per deployment: navigate, resize to a fixed size, wait for text that only exists once async data has loaded. Pick text from the **slowest** region, not just the page title. Confirm BOTH sides show the **same** account, records and counts: if the head environment has different data, the diff is noise.

## 3. Capture a component

```js
// page script: find a region's CSS rect (walk up to its card/container)
() => {
  const el = /* anchor by heading text, role, or container class */;
  el.scrollIntoView({ block: 'center' });
  const r = el.getBoundingClientRect();
  return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
}
```

Then **screenshot to a discard file, screenshot again to the real file**, and `node crop.mjs raw/<page>.png <x> <y> <w> <h> comp/<side>/<name>.png`. Read the crop back to verify.

Reuse one crop rect for both sides only when both report the same rect. Otherwise read the rect on each side: spacing and type changes shift Y by a few px, which is expected.

## 4. Compose and PR

```bash
node sxs.mjs                                         # comp/sxs/<name>.png  (before|after)
node diff.mjs raw/before_top.png raw/after_top.png   # optional: % changed and which bands moved
gh pr create --base <base> --head <head> -t "<title>" -F body.md
```

Table options in the body:

- **1 column** "Before → After" using `comp/sxs/*`: half the uploads.
- **2 columns** "Before | After" using `comp/before/*` + `comp/after/*`: literal, more uploads.

Use `<img width="...">` in cells (for example 430 for full-width components, 300 for narrow cards) so columns stay tidy. After embedding, re-apply with `gh pr edit <n> -F body.md` and verify:

```bash
gh pr view <n> --json body --jq .body | grep -c "_drop"                      # → 0 placeholders
gh pr view <n> --json body --jq .body | grep -oc "user-attachments/assets"   # → expected image count
```

## Uploading images: why `gh` can't, and what to do

- **`gh` has no attachment-upload command.** Inline images in issues and PRs live on GitHub's attachment CDN (`github.com/user-attachments/assets/...`), populated by the web editor through a session-cookie and CSRF endpoint. Tokens and `gh api` cannot reach it.
- **Private repos:** `raw.githubusercontent.com`, blob `?raw=true` and release-asset URLs all require auth, so GitHub's image proxy fetches them unauthenticated and the images break. The attachment CDN is the only source that renders inline.
- **Automate a logged-in browser instead:**
  1. Navigate to the PR, click **Edit** on the description (or focus a new comment box).
  2. Find the editor's hidden file input (the markdown toolbar's "paste, drop, or click to add files" affordance is backed by an `<input type="file">`).
  3. Upload the local PNG into that input. GitHub uploads it and inserts `![](.../user-attachments/assets/...)` into the textarea.
  4. Repeat per image; read the textarea value with a page script to collect the URLs, or submit and `gh pr view --json body` to read them back.
  5. Build the final table with those URLs and `gh pr edit -F body.md`.
- **Manual fallback:** open `comp/sxs` (or `comp/before` + `comp/after`); the user drags files into the PR editor; `gh pr view <n> --json body` gives the uploaded URLs (often as a flat list). Match them by `alt` or order and wire them into the table cells.

## Gotchas

- **Frame lag on scroll.** A screenshot can capture the frame *before* a fresh `scrollIntoView` applies. Shoot twice and keep the second. A crop showing the wrong region means the rect and the frame were out of sync: re-shoot, don't re-measure.
- **Inner scroll container.** The page may not scroll the window (`document.scrollingElement` stays at 0) because content scrolls inside a nested element. `el.scrollIntoView()` finds the right scroller; `window.scrollTo` may silently no-op.
- **Stray tabs resize the window.** A redirect opening a second tab can resize the viewport mid-run (1440 → 2560), shifting every rect. After odd `innerWidth` reads, switch back to the target tab and re-apply the fixed size.
- **Downscaled read-backs.** A screenshot shown back to you is downscaled; its pixels are not CSS px. Crop from the measured `getBoundingClientRect`, then verify.
- **Hidden DOM collisions.** Text matching (`textContent === 'Activity'`) can hit `display:none` legacy markup. Filter to visible nodes (`getBoundingClientRect().width > 0`).
- **Transformed panels report odd rects.** A slide-in panel mid-animation can return `x = innerWidth`. Wait for it to settle, or crop by its on-screen position.
- **Uppercased labels.** With `text-transform: uppercase`, `textContent` is "Assignee", not "ASSIGNEE": match case-insensitively.
- **Live clocks re-render.** A per-minute timestamp can re-render and reset scroll; capture promptly after settling.
- **Stale `GITHUB_TOKEN`.** If `gh` returns 401, an invalid env token may be shadowing the keyring: `env -u GITHUB_TOKEN gh ...`.

## Worked example: a two-column detail page

- URLs: the same `/items/<id>` route on the base and head preview deployments. Viewport 1440×900.
- Layout anchor: the two-column grid container; `grid.children[0]` is the main column, `grid.children[1]` the sidebar.
- Components and anchors:
  - **header** = `mainCol.children[0]` (title, meta, chips).
  - **activity** = anchor the first day separator (a visible leaf matching the date) in the main column; scroll to `block:'start'`, crop down through the first entry.
  - **sidebar cards** = `sidebarCol.children` matched by leading text (`/^Assignee/i`, ...), walked up to the card container.
  - **side panel** = click its toggle button; the panel slides in, so crop by its visible on-screen position.
- Settle text: wait for a label from the slowest-loading sidebar card.
- Typical deltas: body text size, a secondary text colour raised for contrast, a shared label component converging letter-spacing, and heading levels. Non-visual changes (screen-reader-only headings, focus reveal, reduced motion) are verified through the accessibility tree, not pixels, and listed under Won't snap.
