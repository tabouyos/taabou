// usage: node render_bgm.js <bgm_engine.js> <theme> <durationSec> <out.wav>
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
(async () => {
  const [engine, theme, dur, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent('<html><body></body></html>');
  await page.addScriptTag({ content: fs.readFileSync(engine, 'utf8') });
  const b64 = await page.evaluate(async ([theme, dur]) => {
    const sr = 48000, buf = await window.__makeMusic(theme, dur, sr);
    const n = buf.length, ch = buf.numberOfChannels, ab = new ArrayBuffer(44 + n * ch * 2), v = new DataView(ab);
    const w = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
    w(0, 'RIFF'); v.setUint32(4, 36 + n * ch * 2, true); w(8, 'WAVEfmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true);
    v.setUint16(22, ch, true); v.setUint32(24, sr, true); v.setUint32(28, sr * ch * 2, true); v.setUint16(32, ch * 2, true); v.setUint16(34, 16, true);
    w(36, 'data'); v.setUint32(40, n * ch * 2, true);
    const data = [...Array(ch).keys()].map(c => buf.getChannelData(c)); let o = 44;
    for (let i = 0; i < n; i++) for (let c = 0; c < ch; c++) { const x = Math.max(-1, Math.min(1, data[c][i])); v.setInt16(o, x * 32767, true); o += 2; }
    let s = ''; const u = new Uint8Array(ab); for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode(...u.subarray(i, i + 0x8000));
    return btoa(s);
  }, [theme, parseFloat(dur)]);
  fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  await browser.close();
})();
