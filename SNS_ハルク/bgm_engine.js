// In-browser BGM synth + muxer (runs in the X tab)
window.__mf = (m) => 440 * Math.pow(2, (m - 69) / 12);

window.__makeMusic = async (theme, dur, sr) => {
  const ctx = new OfflineAudioContext(2, Math.ceil(dur * sr), sr);
  const mf = window.__mf;
  // master chain
  const master = ctx.createGain(); master.gain.value = 0.55;
  const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 4;
  const fade = ctx.createGain();
  fade.gain.setValueAtTime(0, 0); fade.gain.linearRampToValueAtTime(1, 0.25);
  fade.gain.setValueAtTime(1, dur - 0.45); fade.gain.linearRampToValueAtTime(0, dur - 0.02);
  master.connect(comp); comp.connect(fade); fade.connect(ctx.destination);
  // reverb
  const ir = ctx.createBuffer(2, Math.floor(sr * 2.2), sr);
  for (let ch = 0; ch < 2; ch++) { const d = ir.getChannelData(ch); for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 3); }
  const conv = ctx.createConvolver(); conv.buffer = ir;
  const wet = ctx.createGain(); wet.gain.value = 0.28; conv.connect(wet); wet.connect(master);
  const bus = ctx.createGain(); bus.connect(master); bus.connect(conv);
  // noise buffer
  const nb = ctx.createBuffer(1, sr * 2, sr); { const d = nb.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; }

  const env = (g, t, a, peak, decay) => { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + decay); };
  const osc = (type, f, t, len, out) => { const o = ctx.createOscillator(); o.type = type; o.frequency.value = f; o.connect(out); o.start(t); o.stop(t + len + 0.05); return o; };

  const box = (t, m, vol = 0.18) => { // music box tine
    const g = ctx.createGain(); env(g, t, 0.003, vol, 1.6); g.connect(bus);
    osc('sine', mf(m), t, 1.7, g);
    const g2 = ctx.createGain(); env(g2, t, 0.002, vol * 0.35, 0.25); g2.connect(bus);
    osc('sine', mf(m) * 3.01, t, 0.3, g2);
  };
  const koto = (t, m, vol = 0.16) => {
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.Q.value = 2;
    f.frequency.setValueAtTime(3800, t); f.frequency.exponentialRampToValueAtTime(700, t + 0.9);
    const g = ctx.createGain(); env(g, t, 0.004, vol, 1.4); f.connect(g); g.connect(bus);
    osc('sawtooth', mf(m), t, 1.5, f); osc('triangle', mf(m) * 2, t, 0.4, f);
  };
  const piano = (t, m, vol = 0.14) => {
    const g = ctx.createGain(); env(g, t, 0.005, vol, 1.8); g.connect(bus);
    osc('triangle', mf(m), t, 1.9, g);
    const g2 = ctx.createGain(); env(g2, t, 0.004, vol * 0.4, 0.6); g2.connect(bus);
    osc('sine', mf(m) * 2, t, 0.7, g2);
  };
  const pizz = (t, m, vol = 0.22) => {
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 1400;
    const g = ctx.createGain(); env(g, t, 0.004, vol, 0.28); f.connect(g); g.connect(bus);
    osc('triangle', mf(m), t, 0.35, f); osc('sawtooth', mf(m), t, 0.2, f);
  };
  const flute = (t, m, len, vol = 0.09) => {
    const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.06);
    g.gain.setValueAtTime(vol, t + len - 0.08); g.gain.linearRampToValueAtTime(0.0001, t + len); g.connect(bus);
    const o = osc('sine', mf(m), t, len, g);
    const lfo = ctx.createOscillator(); lfo.frequency.value = 5.5; const lg = ctx.createGain(); lg.gain.value = mf(m) * 0.008;
    lfo.connect(lg); lg.connect(o.frequency); lfo.start(t); lfo.stop(t + len);
    const o2 = osc('triangle', mf(m) * 2, t, len, g); o2.detune.value = 3;
  };
  const pad = (t, ms, len, vol = 0.05) => {
    ms.forEach(m => { const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(vol, t + 0.6);
      g.gain.setValueAtTime(vol, t + len - 0.4); g.gain.linearRampToValueAtTime(0.0001, t + len); g.connect(bus);
      osc('sine', mf(m), t, len, g); const o = osc('triangle', mf(m), t, len, g); o.detune.value = 6; });
  };
  const bell = (t, m, vol = 0.07) => {
    const g = ctx.createGain(); env(g, t, 0.002, vol, 2.4); g.connect(bus);
    osc('sine', mf(m), t, 2.5, g); osc('sine', mf(m) * 2.76, t, 1.2, g); osc('sine', mf(m) * 5.4, t, 0.6, g);
  };
  const noise = (t, len, ftype, freq, vol) => {
    const s = ctx.createBufferSource(); s.buffer = nb; s.loop = true;
    const f = ctx.createBiquadFilter(); f.type = ftype; f.frequency.value = freq; f.Q.value = 0.7;
    const g = ctx.createGain(); g.gain.value = vol; s.connect(f); f.connect(g); g.connect(master);
    s.start(t); s.stop(t + len); return g;
  };
  const drip = (t, vol = 0.05) => {
    const g = ctx.createGain(); env(g, t, 0.002, vol, 0.09); g.connect(bus);
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(900 + Math.random() * 400, t);
    o.frequency.exponentialRampToValueAtTime(2400, t + 0.06); o.connect(g); o.start(t); o.stop(t + 0.12);
  };
  const taiko = (t, vol = 0.5) => {
    const g = ctx.createGain(); env(g, t, 0.003, vol, 0.5); g.connect(master);
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(120, t); o.frequency.exponentialRampToValueAtTime(48, t + 0.35);
    o.connect(g); o.start(t); o.stop(t + 0.6);
    const ng = noise(t, 0.08, 'lowpass', 500, 0.0); ng.gain.setValueAtTime(0.25, t); ng.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
  };
  const block = (t, vol = 0.12) => {
    const g = ctx.createGain(); env(g, t, 0.001, vol, 0.05); g.connect(bus); osc('sine', 1250, t, 0.08, g); osc('square', 2500, t, 0.03, g);
  };

  const S = dur / 16; // 8th-note step (two bars)
  const seq = (arr, fn, stepLen = S, off = 0) => arr.forEach((m, i) => { if (m != null) fn(off + i * stepLen, m); });

  switch (theme) {
    case 'flower':
      pad(0, [48, 55, 64], dur / 2 + 0.3); pad(dur / 2, [53, 60, 69], dur / 2);
      seq([72, 76, 79, 84, 83, 79, 76, 79, 77, 81, 84, 88, 86, 84, 81, 77], (t, m) => box(t, m));
      seq([60, null, 67, null, 65, null, 72, null], (t, m) => box(t, m, 0.08), S * 2);
      break;
    case 'sento':
      pad(0, [50, 57, 62], dur, 0.04); bell(0.05, 86);
      seq([74, 71, 69, 67, 69, null, 62, null], (t, m) => koto(t, m), S * 2);
      for (let i = 0; i < 7; i++) drip(0.4 + Math.random() * (dur - 1), 0.04);
      noise(0, dur, 'lowpass', 600, 0.015);
      break;
    case 'bookstore':
      noise(0, dur, 'bandpass', 3200, 0.05); noise(0, dur, 'lowpass', 900, 0.03);
      seq([57, 60, 64, 69, 64, 60, 57, 60, 53, 57, 60, 65, 60, 57, 53, 57], (t, m) => piano(t, m, 0.08));
      seq([76, null, 74, null, 72, null, null, null], (t, m) => piano(t, m, 0.11), S * 2);
      for (let i = 0; i < 10; i++) drip(Math.random() * (dur - 0.3), 0.025);
      break;
    case 'dagashi':
      seq([43, 50, 43, 50, 47, 50, 43, 50], (t, m) => pizz(t, m, 0.16), S * 2);
      seq([67, 69, 71, 74, 76, 74, 71, 69, 67, 71, 74, 79, 76, 74, 71, null], (t, m) => box(t, m, 0.16));
      break;
    case 'onsen':
      pad(0, [40, 47, 52], dur, 0.045); bell(0.05, 88); bell(dur / 2, 83, 0.05);
      seq([76, 72, 71, 69, 71, 65, 64, null], (t, m) => koto(t, m, 0.15), S * 2);
      noise(0, dur, 'lowpass', 500, 0.02);
      break;
    case 'matsuri':
      [0, 4, 8, 10, 12].forEach(i => taiko(i * S, 0.45));
      [2, 6, 14].forEach(i => block(i * S)); [3, 7, 11, 15].forEach(i => block(i * S, 0.06));
      seq([74, 76, 79, 81, 79, 76, 74, null, 76, 79, 81, 84, 81, 79, 76, 74], (t, m) => flute(t, m, S * 0.95));
      pad(0, [50, 57], dur, 0.03);
      break;
    case 'halloween':
      pad(0, [38, 45, 50], dur, 0.035);
      seq([38, 45, 38, 45, 41, 45, 41, 46], (t, m) => pizz(t, m, 0.2), S * 2);
      seq([74, 73, 74, 77, 76, 74, 73, 70, 69, 70, 73, 74, 77, 76, 74, null], (t, m) => box(t, m, 0.15));
      break;
    case 'candy':
      pad(0, [41, 48, 53], dur, 0.035);
      seq([41, 48, 44, 48, 41, 48, 43, 47], (t, m) => pizz(t, m, 0.18), S * 2);
      seq([77, null, 80, 79, 77, null, 72, null, 73, null, 77, 76, 73, null, 68, null], (t, m) => box(t, m, 0.15));
      flute(S * 8, 84, S * 3, 0.04); flute(S * 12, 83, S * 3, 0.04);
      break;
    case 'parade':
      [0, 4, 8, 12].forEach(i => taiko(i * S, 0.35)); [2, 6, 10, 14].forEach(i => block(i * S, 0.1));
      seq([38, 45, 41, 45, 38, 45, 43, 45], (t, m) => pizz(t, m, 0.2), S * 2);
      seq([62, 65, 69, 74, 73, 69, 65, 69, 70, 74, 77, 74, 73, 76, 74, null], (t, m) => box(t, m, 0.16));
      break;
  }
  return await ctx.startRendering();
};

window.__mux = async (file, theme) => {
  const url = URL.createObjectURL(file);
  const v = document.createElement('video'); v.src = url; v.muted = true; v.playsInline = true; v.preload = 'auto';
  await new Promise((r, j) => { v.onloadeddata = r; v.onerror = j; });
  const k = Math.max(1, 720 / v.videoWidth); const c = document.createElement('canvas'); c.width = Math.round(v.videoWidth * k / 2) * 2; c.height = Math.round(v.videoHeight * k / 2) * 2;
  const g = c.getContext('2d'); g.imageSmoothingQuality = 'high'; g.drawImage(v, 0, 0, c.width, c.height);
  const ac = window.__ac; await ac.resume();
  const buf = await window.__makeMusic(theme, v.duration, ac.sampleRate);
  const dest = ac.createMediaStreamDestination();
  const src = ac.createBufferSource(); src.buffer = buf; src.connect(dest);
  const stream = new MediaStream([...c.captureStream(30).getVideoTracks(), ...dest.stream.getAudioTracks()]);
  const mime = 'video/mp4;codecs=avc1.640028,mp4a.40.2';
  const rec = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 10000000, audioBitsPerSecond: 192000 });
  const chunks = []; rec.ondataavailable = e => e.data.size && chunks.push(e.data);
  const stopped = new Promise(r => rec.onstop = r);
  rec.start(250);
  const draw = () => { g.drawImage(v, 0, 0, c.width, c.height); if (!v.ended) v.requestVideoFrameCallback(draw); };
  v.requestVideoFrameCallback(draw);
  src.start(); await v.play();
  await new Promise(r => v.onended = r);
  g.drawImage(v, 0, 0, c.width, c.height);
  await new Promise(r => setTimeout(r, 120));
  rec.stop(); try { src.stop(); } catch (e) {}
  await stopped; URL.revokeObjectURL(url);
  return new File(chunks, file.name.replace('.mp4', '_bgm.mp4'), { type: 'video/mp4' });
};

window.__themes = {
  day1_1016_flower: 'flower', day2_1017_sento: 'sento', day3_1018_bookstore: 'bookstore', day4_1019_dagashi: 'dagashi',
  day5_1020_onsen: 'onsen', day6_1021_matsuri: 'matsuri', day7_1022_halloween: 'halloween', day_1030_candy: 'candy', day_1031_parade: 'parade'
};
window.__out = {}; window.__log = [];
window.__ids = {
 day1_1016_flower:'77c33973-b770-4695-8b9e-1f3cf258e475', day2_1017_sento:'5953e116-8418-499f-ab55-1fa8dc261ecd',
 day3_1018_bookstore:'45f843b5-7fa5-40f9-928c-c8ef84f21b52', day4_1019_dagashi:'f5d6e57c-fef5-4192-9a75-f9cf90821e2f',
 day5_1020_onsen:'f435fccb-089e-4601-99e6-ef717da709d1', day6_1021_matsuri:'e61180ce-4303-4b19-acce-10dd80540edc',
 day7_1022_halloween:'ba909496-56bb-4542-a47b-fbbabf62e5e6', day_1030_candy:'14bc9861-a2b6-44d2-bf2c-958b82b83b09',
 day_1031_parade:'fd7b958f-3588-4659-85ca-01bc390a7017' };
window.__runAll = async () => {
  window.__ac = window.__ac || new AudioContext(); await window.__ac.resume();
  for (const [name, theme] of Object.entries(window.__themes)) {
    try {
      const r = await fetch('https://cdn.midjourney.com/video/' + window.__ids[name] + '/0.mp4');
      const src = new File([await r.blob()], 'tiktok_' + name + '.mp4', { type: 'video/mp4' });
      const f = await window.__mux(src, theme); window.__out[name] = f; window.__log.push(name + ' ' + f.size);
    } catch (e) { window.__log.push(name + ' ERR ' + e.message); }
  }
  window.__log.push('DONE');
};
window.__dlAll = async () => {
  for (const [name, f] of Object.entries(window.__out)) {
    const a = document.createElement('a'); a.href = URL.createObjectURL(f); a.download = f.name; document.body.appendChild(a); a.click(); a.remove();
    await new Promise(r => setTimeout(r, 700));
  }
  window.__log.push('DL DONE');
};
const b = document.createElement('button'); b.id='bgmrun'; b.textContent='BGM'; b.style.cssText='position:fixed;left:10px;top:10px;z-index:999999;width:80px;height:40px;background:#f60;color:#fff';
b.onclick = () => window.__runAll(); document.body.appendChild(b);
'bgm loaded';
