// SFX from zero: toggle + precise beep aligned to visuals
(function () {
  var KEY = 'sound_enabled';
  var enabled = true; // default to ON
  var toggleEl = null;

  var ctx = null;
  var master = null;
  var comp = null;
  var lastBeepAt = 0;
  var lastClickAt = 0;
  var fan = { el: null, mediaSource: null, volume: 0.06 };
  var reverb = { convolver: null, gain: null };
  var sfxBus = null; // global SFX gain (hard cap)
  // Keyboard SFX state
  var noiseBuffer = null;
  var keyLastTimes = Object.create(null);
  var activeKeyVoices = 0;
  var maxKeyVoices = 12;

  function setToggleLabel() {
    if (!toggleEl) return;
    toggleEl.textContent = 'SFX: ' + (enabled ? 'On' : 'Off');
    toggleEl.setAttribute('aria-pressed', String(enabled));
  }

  function ensureContext() {
    if (ctx) return;
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain();
      master.gain.value = 1.0;
      comp = ctx.createDynamicsCompressor();
      comp.threshold.setValueAtTime(-18, ctx.currentTime);
      comp.knee.setValueAtTime(20, ctx.currentTime);
      comp.ratio.setValueAtTime(8, ctx.currentTime);
      comp.attack.setValueAtTime(0.003, ctx.currentTime);
      comp.release.setValueAtTime(0.15, ctx.currentTime);
      master.connect(comp);
      comp.connect(ctx.destination);
    } catch (_) { ctx = null; }
  }

  function ensureSfxBus() {
    if (!ctx) return false;
    if (sfxBus) return true;
    try {
      sfxBus = ctx.createGain();
      // Low overall SFX level (audible but subtle)
      sfxBus.gain.value = 0.01;
      sfxBus.connect(master);
      return true;
    } catch (_) { sfxBus = null; return false; }
  }

  function ensureReverb() {
    if (!ctx) return false;
    if (reverb.convolver && reverb.gain) return true;
    try {
      var sr = ctx.sampleRate || 44100;
      // Longer IR for more room, still lightweight
      var len = Math.floor(sr * 0.40);
      var ir = ctx.createBuffer(2, len, sr);
      for (var ch = 0; ch < 2; ch++) {
        var data = ir.getChannelData(ch);
        for (var i = 0; i < len; i++) {
          var t = i / len;
          // white noise * decay; a bit smoother tail
          data[i] = (Math.random() * 2 - 1) * Math.pow(1 - t, 1.8);
        }
      }
      var conv = ctx.createConvolver();
      conv.buffer = ir;
      var g = ctx.createGain();
      // Minimal overall reverb return for near-inaudible tail
      g.gain.value = 0.04;
      conv.connect(g);
      // Prefer sfxBus if available; fall back to master
      if (!sfxBus) ensureSfxBus();
      if (sfxBus) { g.connect(sfxBus); } else { g.connect(master); }
      reverb.convolver = conv;
      reverb.gain = g;
      return true;
    } catch (_) {
      reverb.convolver = null;
      reverb.gain = null;
      return false;
    }
  }

  function setEnabled(next) {
    enabled = !!next;
    try { localStorage.setItem(KEY, enabled ? '1' : '0'); } catch (_) {}
    setToggleLabel();
    if (enabled) {
      ensureContext();
      ensureSfxBus();
      if (ctx && ctx.state === 'suspended') { try { ctx.resume(); } catch (_) {} }
      startFan();
    } else {
      stopFan();
    }
  }

  function bindToggle() {
    var el = document.getElementById('sound-toggle');
    if (!el) return;
    toggleEl = el;
    setToggleLabel();
    toggleEl.onclick = function (e) { e.preventDefault(); setEnabled(!enabled); };
  }

  // Core scheduler with explicit frequency
  function scheduleBeepSyncEx(freqHz, offsetMs) {
    if (!enabled) return null;
    ensureContext();
    if (!ctx) return null;
    if (ctx.state === 'suspended') { try { ctx.resume(); } catch (_) {} }
    var nowMS = (performance && performance.now) ? performance.now() : Date.now();
    if (nowMS - lastBeepAt < 35) return null; // rate limit
    lastBeepAt = nowMS;

    var offset = Math.max(30, (typeof offsetMs === 'number' ? offsetMs : 70)) / 1000;
    var t0 = ctx.currentTime + offset;
    // Beep source (triangle for softer tone)
    var osc = ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime((typeof freqHz === 'number' && freqHz > 0) ? freqHz : 783.99, t0);
    // Tame highs more for smoothness
    var lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(1200, t0); // even softer top end
    lp.Q.setValueAtTime(0.6, t0);
    var g = ctx.createGain();
    // Quieter with tiny attack to avoid clicks
    g.gain.setValueAtTime(0.0, t0);
    g.gain.linearRampToValueAtTime(0.0005, t0 + 0.002); // extremely quiet
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.035);
    var dry = ctx.createGain(); dry.gain.value = 1.0;
    var send = ctx.createGain();
    // Minimal send for near-silent tail
    send.gain.value = 0.01;
    if (!sfxBus) ensureSfxBus();
    osc.connect(lp);
    lp.connect(dry);
    if (sfxBus) { dry.connect(sfxBus); } else { dry.connect(master); }
    if (ensureReverb()) { lp.connect(send); send.connect(reverb.convolver); }
    try { osc.start(t0); osc.stop(t0 + 0.045); } catch (_) {}

    var targetPerf = null;
    try {
      if (typeof ctx.getOutputTimestamp === 'function') {
        var ts = ctx.getOutputTimestamp();
        if (ts && typeof ts.performanceTime === 'number' && typeof ts.contextTime === 'number') {
          targetPerf = ts.performanceTime + (t0 - ts.contextTime) * 1000;
        }
      }
    } catch (_) {}
    if (targetPerf === null) {
      var delta = (nowMS / 1000) - ctx.currentTime;
      targetPerf = (t0 + delta) * 1000;
    }
    return targetPerf;
  }

  // Backward-compatible wrapper: default G5
  function scheduleBeepSync(offsetMs) {
    return scheduleBeepSyncEx(783.99, offsetMs);
  }

  function beepImmediateEx(freqHz) {
    if (!enabled) return;
    ensureContext();
    if (!ctx) return;
    if (ctx.state === 'suspended') { try { ctx.resume(); } catch (_) {} }
    var nowMS = (performance && performance.now) ? performance.now() : Date.now();
    if (nowMS - lastBeepAt < 35) return;
    lastBeepAt = nowMS;
    var t = ctx.currentTime;
    var osc = ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime((typeof freqHz === 'number' && freqHz > 0) ? freqHz : 783.99, t);
    var lp = ctx.createBiquadFilter();
    lp.type = 'lowpass';
    lp.frequency.setValueAtTime(1200, t);
    lp.Q.setValueAtTime(0.6, t);
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0, t);
    g.gain.linearRampToValueAtTime(0.0005, t + 0.002);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.035);
    var dry = ctx.createGain(); dry.gain.value = 1.0;
    var send = ctx.createGain(); send.gain.value = 0.01;
    if (!sfxBus) ensureSfxBus();
    osc.connect(lp);
    lp.connect(dry);
    if (sfxBus) { dry.connect(sfxBus); } else { dry.connect(master); }
    if (ensureReverb()) { lp.connect(send); send.connect(reverb.convolver); }
    try { osc.start(t); osc.stop(t + 0.055); } catch (_) {}
  }

  function beepImmediate() { beepImmediateEx(783.99); }

  function init() {
    bindToggle();
    // Default to ON when no preference stored
    try {
      var stored = localStorage.getItem(KEY);
      if (stored === null) {
        enabled = true;
      } else {
        enabled = (stored === '1');
      }
    } catch (_) { enabled = true; }
    setToggleLabel();
    if (enabled) {
      ensureContext();
      var onFirstGesture = function () {
        if (!ctx) ensureContext();
        if (ctx && ctx.state === 'suspended') { try { ctx.resume(); } catch (_) {} }
        startFan();
        document.removeEventListener('pointerdown', onFirstGesture, true);
        document.removeEventListener('keydown', onFirstGesture, true);
      };
      document.addEventListener('pointerdown', onFirstGesture, true);
      document.addEventListener('keydown', onFirstGesture, true);
    }
    // Keyboard listeners
    document.addEventListener('keydown', function (e) {
      if (!enabled) return;
      playKeySound(e, false);
    }, true);
    document.addEventListener('keyup', function (e) {
      if (!enabled) return;
      playKeySound(e, true);
    }, true);
    // Click listeners for interactive elements
    document.addEventListener('click', function (e) {
      if (!enabled) return;
      var t = e.target;
      if (!t) return;
      if (t.closest && (t.closest('a') || t.closest('button') || t.closest('input[type="button"]') || t.closest('input[type="submit"]'))) {
        playClick(e);
      }
    }, true);
  }

  function ensureFanMedia() {
    if (fan.el) return;
    try {
      var audio = new Audio('/static/audio/fan.mp3');
      audio.loop = true;
      audio.preload = 'auto';
      audio.volume = fan.volume;
      fan.el = audio;
      if (ctx && typeof ctx.createMediaElementSource === 'function') {
        fan.mediaSource = ctx.createMediaElementSource(audio);
        fan.mediaSource.connect(master);
      }
    } catch (_) {
      fan.el = null;
      fan.mediaSource = null;
    }
  }

  function startFan() {
    if (!enabled) return;
    ensureFanMedia();
    if (!fan.el) return;
    try { fan.el.play().catch(function () {}); } catch (_) {}
  }

  function stopFan() {
    if (!fan.el) return;
    try { fan.el.pause(); } catch (_) {}
  }

  // Expose minimal API for PJAX
  window.__mpd_initSoundToggle = bindToggle;
  window.__mpd_scheduleBeepSync = scheduleBeepSync;
  window.__mpd_scheduleBeepSyncEx = scheduleBeepSyncEx;
  window.__mpd_chunkBeepImmediate = beepImmediate;
  window.__mpd_chunkBeepImmediateEx = beepImmediateEx;
  window.__mpd_isSfxEnabled = function () { return !!enabled; };

  // ---------- Keyboard synthesis ----------
  function ensureNoiseBuffer() {
    if (noiseBuffer || !ctx) return;
    var sr = ctx.sampleRate || 44100;
    var len = Math.floor(sr * 0.12); // 120 ms
    var buf = ctx.createBuffer(1, len, sr);
    var d = buf.getChannelData(0);
    for (var i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    noiseBuffer = buf;
  }

  function keyRowAndPos(code) {
    var rows = {
      digits: ['Digit1','Digit2','Digit3','Digit4','Digit5','Digit6','Digit7','Digit8','Digit9','Digit0','Minus','Equal'],
      top:    ['KeyQ','KeyW','KeyE','KeyR','KeyT','KeyY','KeyU','KeyI','KeyO','KeyP','BracketLeft','BracketRight'],
      home:   ['KeyA','KeyS','KeyD','KeyF','KeyG','KeyH','KeyJ','KeyK','KeyL','Semicolon','Quote'],
      bottom: ['KeyZ','KeyX','KeyC','KeyV','KeyB','KeyN','KeyM','Comma','Period','Slash']
    };
    var row = 'home';
    var arr = rows.home;
    if (rows.digits.includes(code)) { row = 'digits'; arr = rows.digits; }
    else if (rows.top.includes(code)) { row = 'top'; arr = rows.top; }
    else if (rows.bottom.includes(code)) { row = 'bottom'; arr = rows.bottom; }
    else if (code === 'Space') { return { row: 'bottom', pos: 0.5 }; }
    var idx = arr.indexOf(code);
    var pos = idx >= 0 && arr.length > 1 ? idx / (arr.length - 1) : 0.5;
    return { row: row, pos: pos };
  }

  function rowCenterHz(row) {
    // Slightly lower centers for deeper tone
    if (row === 'digits') return 2400;
    if (row === 'top') return 2200;
    if (row === 'bottom') return 1700;
    return 1900; // home
  }

  function playKeySound(e, isRelease) {
    if (!enabled) return;
    ensureContext();
    if (!ctx) return;
    if (activeKeyVoices >= maxKeyVoices) return;
    var nowMs = (window.performance && performance.now) ? performance.now() : Date.now();
    var code = (e && e.code) || 'Unknown';
    var last = keyLastTimes[code] || 0;
    if (nowMs - last < 25) return; // per-key debounce
    keyLastTimes[code] = nowMs;
    ensureNoiseBuffer();

    var t = ctx.currentTime;
    var rp = keyRowAndPos(code);
    var baseCenter = rowCenterHz(rp.row);
    var dbVar = (Math.random() * 6 - 3);
    var gainMul = Math.pow(10, dbVar / 20);
    var freqVarPct = 1 + (Math.random() * 0.24 - 0.12);
    var decayVar = 0.002 * (Math.random() * 2 - 1);

    var outGain = ctx.createGain();
    outGain.gain.value = gainMul;
    var panNode = (ctx.createStereoPanner ? ctx.createStereoPanner() : null);
    var out = outGain;
    if (panNode) {
      var pan = (rp.pos - 0.5) * 0.5;
      panNode.pan.value = pan;
      outGain.connect(panNode);
      panNode.connect(master);
    } else {
      outGain.connect(master);
    }

    function noiseBurst(startTime, amp, hpHz, bpHz, q, decayMs) {
      var src = ctx.createBufferSource();
      src.buffer = noiseBuffer;
      var hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = hpHz;
      var bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = bpHz; bp.Q.value = q;
      var g = ctx.createGain(); g.gain.setValueAtTime(amp, startTime);
      g.gain.exponentialRampToValueAtTime(0.0001, startTime + decayMs);
      src.connect(hp); hp.connect(bp); bp.connect(g); g.connect(out);
      src.start(startTime);
      src.stop(startTime + Math.max(0.06, decayMs + 0.02));
    }

    function sineThock(startTime, freq, amp, decayMs) {
      var osc = ctx.createOscillator(); osc.type = 'sine'; osc.frequency.setValueAtTime(freq, startTime);
      var g = ctx.createGain(); g.gain.setValueAtTime(amp, startTime);
      g.gain.exponentialRampToValueAtTime(0.0001, startTime + decayMs);
      osc.connect(g); g.connect(out);
      osc.start(startTime); osc.stop(startTime + Math.max(0.05, decayMs + 0.01));
    }

    // Main transient
    var centerMain = baseCenter * freqVarPct * 0.75; // lower
    var hpMain = 400 + Math.random() * 250; // 400-650 Hz
    var bpQ = 1.0 + Math.random() * 0.4;
    var decayMain = 0.015 + Math.random() * 0.020 + decayVar; // 15-35 ms
    noiseBurst(t, isRelease ? 0.09 : 0.20, hpMain, centerMain, bpQ, Math.max(0.01, decayMain));

    // Body thock
    var thFreq = 100 + Math.random() * 80; // 100-180 Hz
    var thDecay = 0.012 + Math.random() * 0.012 + decayVar; // 12-24 ms
    sineThock(t, thFreq, isRelease ? 0.015 : 0.035, Math.max(0.006, thDecay));

    // Cap resonance
    var capCenter = 1000 + Math.random() * 1000; // 1.0-2.0 kHz
    var capQ = 2 + Math.random() * 2; // 2-4
    var capDecay = 0.040 + Math.random() * 0.050 + decayVar; // 40-90 ms
    noiseBurst(t, isRelease ? 0.030 : 0.060, 500, capCenter, capQ, Math.max(0.02, capDecay));

    // Optional reflection
    if (!isRelease && Math.random() < 0.7) {
      var dly = 0.008 + Math.random() * 0.008; // 8-16 ms
      noiseBurst(t + dly, 0.06, hpMain, centerMain * 1.05, 1.0, 0.012 + Math.random() * 0.012);
    }

    activeKeyVoices++;
    setTimeout(function () { activeKeyVoices = Math.max(0, activeKeyVoices - 1); }, 120);
  }

  // ---------- Click synthesis on interactive elements ----------
  function playClick(e) {
    if (!enabled) return;
    // do not click on the SFX toggle itself
    if (e && e.target && (e.target.id === 'sound-toggle' || (e.target.closest && e.target.closest('#sound-toggle')))) return;
    ensureContext();
    if (!ctx) return;
    var nowMS = (performance && performance.now) ? performance.now() : Date.now();
    if (nowMS - lastClickAt < 30) return; // debounce
    lastClickAt = nowMS;
    ensureNoiseBuffer();

    var t = ctx.currentTime;

    // Micro-variations
    var dbVar = (Math.random() * 6 - 3); // +/-3 dB
    var gainMul = Math.pow(10, dbVar / 20);
    var freqVarPct = 1 + (Math.random() * 0.3 - 0.15); // +/-15%
    var relDelay = 0.02 + Math.random() * 0.04; // 20-60 ms

    var outGain = ctx.createGain();
    outGain.gain.value = gainMul;
    outGain.connect(master);

    function noiseTransient(startTime, ampScale, centerHz) {
      var src = ctx.createBufferSource();
      src.buffer = noiseBuffer;
      var hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 800;
      var bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = centerHz; bp.Q.value = 1.0;
      var g = ctx.createGain(); g.gain.setValueAtTime(ampScale, startTime);
      var decayMs = 0.02 + Math.random() * 0.02; // 20-40 ms
      g.gain.exponentialRampToValueAtTime(0.0001, startTime + decayMs);
      src.connect(hp); hp.connect(bp); bp.connect(g); g.connect(outGain);
      src.start(startTime);
      src.stop(startTime + 0.12);
    }

    function thump(startTime, freq, amp) {
      var osc = ctx.createOscillator(); osc.type = 'sine'; osc.frequency.setValueAtTime(freq, startTime);
      var g = ctx.createGain(); g.gain.setValueAtTime(amp, startTime);
      var d = 0.005 + Math.random() * 0.01; // 5-15 ms
      g.gain.exponentialRampToValueAtTime(0.0001, startTime + d);
      osc.connect(g); g.connect(outGain);
      osc.start(startTime); osc.stop(startTime + 0.05);
    }

    // Layer 1: main transient
    var center = 3300 * freqVarPct; // 2-6 kHz
    noiseTransient(t, 0.22, center);
    // Layer 2: mechanical thump
    var thumpFreq = 120 + Math.random() * 130; // 120-250 Hz
    thump(t, thumpFreq, 0.03);
    // Layer 3: optional release
    noiseTransient(t + relDelay, 0.12, center * 1.1);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
