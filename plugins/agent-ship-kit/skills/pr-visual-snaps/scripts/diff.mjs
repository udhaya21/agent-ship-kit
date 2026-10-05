import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import fs from 'fs';

// Optional whole-frame pixel-regression: how much (and where) two same-size
// screenshots differ. Good for a quick "type/contrast only, no layout shift"
// signal before you bother cropping components.
// usage: node diff.mjs <before.png> <after.png> [outDiff.png=diff.png] [dpr=2]
const [, , bPath, aPath, outPath = 'diff.png', dprs = '2'] = process.argv;
const dpr = +dprs;
const before = PNG.sync.read(fs.readFileSync(bPath));
const after = PNG.sync.read(fs.readFileSync(aPath));

const w = Math.min(before.width, after.width);
const h = Math.min(before.height, after.height);
const crop = (src) => {
  const o = new PNG({ width: w, height: h });
  for (let y = 0; y < h; y++) src.data.copy(o.data, y * w * 4, y * src.width * 4, y * src.width * 4 + w * 4);
  return o;
};
const b = crop(before);
const a = crop(after);
const diff = new PNG({ width: w, height: h });
const changed = pixelmatch(b.data, a.data, diff.data, w, h, { threshold: 0.1, includeAA: false, alpha: 0.25, diffColor: [255, 0, 0] });
fs.writeFileSync(outPath, PNG.sync.write(diff));

// per-50px-CSS-band tally so you can see which rows moved
const bands = {};
for (let y = 0; y < h; y++)
  for (let x = 0; x < w; x++) {
    const i = (y * w + x) * 4;
    if (diff.data[i] === 255 && diff.data[i + 1] === 0 && diff.data[i + 2] === 0) {
      const band = Math.floor((y / dpr) / 50) * 50;
      bands[band] = (bands[band] || 0) + 1;
    }
  }
console.log(JSON.stringify({
  dims: { w, h, cssW: w / dpr, cssH: h / dpr },
  changedPixels: changed,
  pctChanged: +((changed / (w * h)) * 100).toFixed(4),
  topBandsCssY: Object.entries(bands).sort((p, q) => q[1] - p[1]).slice(0, 10).map(([y, c]) => ({ y: +y, px: c })),
  out: outPath,
}, null, 2));
