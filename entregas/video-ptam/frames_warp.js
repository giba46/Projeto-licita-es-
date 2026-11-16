// Renderiza com "time warp": tempo real -> tempo da animação, por trechos lineares.
const { chromium } = require('playwright');
const [,, html, outDir, fps, knotsJson, onlyTimes] = process.argv;
const knots = JSON.parse(knotsJson); // [[real, anim], ...]
const warp = r => { for (let i = 1; i < knots.length; i++) { const [r0,a0]=knots[i-1],[r1,a1]=knots[i]; if (r <= r1) return a0 + (a1-a0)*(r-r0)/(r1-r0); } return knots[knots.length-1][1]; };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready);
  const dur = knots[knots.length-1][0];
  const times = onlyTimes ? onlyTimes.split(',').map(Number) : [...Array(Math.round(fps*dur)).keys()].map(i => i / fps);
  let i = 0;
  for (const t of times) {
    await p.evaluate(a => window.seek(a), warp(t));
    await p.screenshot({ path: `${outDir}/f${String(i++).padStart(4,'0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
