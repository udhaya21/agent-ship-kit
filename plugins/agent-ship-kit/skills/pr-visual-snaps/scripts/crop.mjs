import { PNG } from 'pngjs';
import fs from 'fs';

// Crop a region given in CSS pixels from a screenshot taken at devicePixelRatio `dpr`.
// usage: node crop.mjs <src.png> <xCss> <yCss> <wCss> <hCss> <out.png> [dpr=2]
const [, , src, xs, ys, ws, hs, out, dprs] = process.argv;
if (!out) {
  console.error('usage: node crop.mjs <src.png> <xCss> <yCss> <wCss> <hCss> <out.png> [dpr=2]');
  process.exit(1);
}
const dpr = +(dprs || 2);
const img = PNG.sync.read(fs.readFileSync(src));

let x = Math.round(+xs * dpr);
let y = Math.round(+ys * dpr);
let w = Math.round(+ws * dpr);
let h = Math.round(+hs * dpr);

// clamp to image bounds so an over-long rect never throws
x = Math.max(0, Math.min(x, img.width));
y = Math.max(0, Math.min(y, img.height));
w = Math.min(w, img.width - x);
h = Math.min(h, img.height - y);

const o = new PNG({ width: w, height: h });
for (let row = 0; row < h; row++) {
  const from = ((y + row) * img.width + x) * 4;
  img.data.copy(o.data, row * w * 4, from, from + w * 4);
}
fs.writeFileSync(out, PNG.sync.write(o));
console.log(`${out} ${w}x${h}  (from ${src} @${dpr}x)`);
