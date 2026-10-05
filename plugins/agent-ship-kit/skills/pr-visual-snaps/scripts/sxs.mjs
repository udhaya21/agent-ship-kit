import { PNG } from 'pngjs';
import fs from 'fs';

// Pair every comp/before/<name>.png with comp/after/<name>.png into a
// side-by-side composite (before left | after right) in comp/sxs/<name>.png.
// Auto-discovers components from comp/before/. No args needed.
// Override dirs/gutter: node sxs.mjs [beforeDir] [afterDir] [outDir] [gutterPx]
const beforeDir = process.argv[2] || 'comp/before';
const afterDir = process.argv[3] || 'comp/after';
const outDir = process.argv[4] || 'comp/sxs';
const GUT = +(process.argv[5] || 32);

fs.mkdirSync(outDir, { recursive: true });
const names = fs
  .readdirSync(beforeDir)
  .filter((f) => f.endsWith('.png'))
  .map((f) => f.replace(/\.png$/, ''));

for (const name of names) {
  const bPath = `${beforeDir}/${name}.png`;
  const aPath = `${afterDir}/${name}.png`;
  if (!fs.existsSync(aPath)) {
    console.warn(`skip ${name}: no after/`);
    continue;
  }
  const b = PNG.sync.read(fs.readFileSync(bPath));
  const a = PNG.sync.read(fs.readFileSync(aPath));
  const h = Math.max(b.height, a.height);
  const w = b.width + GUT + a.width;
  const out = new PNG({ width: w, height: h });
  // light gray backdrop so the gutter + height padding reads as a divider
  for (let i = 0; i < out.data.length; i += 4) {
    out.data[i] = 247; out.data[i + 1] = 247; out.data[i + 2] = 248; out.data[i + 3] = 255;
  }
  const blit = (src, dx) => {
    for (let y = 0; y < src.height; y++)
      for (let x = 0; x < src.width; x++) {
        const si = (y * src.width + x) * 4;
        const di = (y * w + (x + dx)) * 4;
        out.data[di] = src.data[si];
        out.data[di + 1] = src.data[si + 1];
        out.data[di + 2] = src.data[si + 2];
        out.data[di + 3] = 255;
      }
  };
  blit(b, 0);
  blit(a, b.width + GUT);
  fs.writeFileSync(`${outDir}/${name}.png`, PNG.sync.write(out));
  console.log(`${outDir}/${name}.png ${w}x${h}`);
}
