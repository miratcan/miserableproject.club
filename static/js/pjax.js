// PJAX from zero: strict sequential chunks with flash + synced beep per chunk
(function () {
  var MAIN = 'main';

  function isModifiedClick(e) { return e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0; }
  function isInternal(href) {
    try { var u = new URL(href, location.href); return u.origin === location.origin; } catch (_) { return false; }
  }

  function swapHeader(doc) {
    var nh = doc.querySelector('header');
    var ch = document.querySelector('header');
    if (!nh || !ch) return;
    var clone = nh.cloneNode(true);
    ch.parentNode.replaceChild(clone, ch);
    if (window.__mpd_initSoundToggle) { try { window.__mpd_initSoundToggle(); } catch (_) {} }
  }

  function initMessages(container) {
    var root = container || document;
    document.addEventListener('click', function (e) {
      var btn = e.target && e.target.closest && e.target.closest('.messages .close');
      if (!btn) return;
      var li = btn.closest('li');
      if (li) li.remove();
    });
    var success = root.querySelectorAll('.messages li.success');
    success.forEach(function (li) { setTimeout(function () { if (li && li.parentNode) li.remove(); }, 4000); });
  }

  function buildChunks(srcMain, dstMain) {
    var srcWrap = srcMain.querySelector('.wrapper') || srcMain;
    var dstWrap = dstMain.querySelector('.wrapper');
    if (!dstWrap && srcWrap !== srcMain) {
      dstWrap = document.createElement('div');
      dstWrap.className = 'wrapper';
      dstMain.appendChild(dstWrap);
    }
    dstWrap = dstMain.querySelector('.wrapper') || dstMain;

    var nodes = Array.prototype.slice.call(srcWrap.childNodes);
    // Pre-clone chunks to avoid work in the timed path
    var chunks = [];
    nodes.forEach(function (n) {
      if (n.nodeType === 3) {
        if ((n.nodeValue || '').trim()) chunks.push({ parent: dstWrap, el: n.cloneNode(true) });
      } else if (n.nodeType === 1) {
        var tag = n.tagName.toLowerCase();
        if (tag === 'article') {
          // Article: append shell, then stream its children as individual chunks
          var shell = n.cloneNode(false);
          var kids = Array.prototype.slice.call(n.childNodes).filter(function (c) {
            return (c.nodeType === 1) || (c.nodeType === 3 && (c.nodeValue || '').trim());
          }).map(function (c) { return c.cloneNode(true); });
          chunks.push({ parent: dstWrap, el: shell, follow: kids });
        } else if (tag === 'section') {
          // Section: single chunk
          chunks.push({ parent: dstWrap, el: n.cloneNode(true) });
        } else if (tag === 'form') {
          // Form: append empty shell, then stream each top-level child as-is
          // to preserve row/field layout.
          var formShell = n.cloneNode(false);
          var childChunks = [];
          Array.prototype.slice.call(n.childNodes).forEach(function (c) {
            if (c.nodeType === 3) {
              if ((c.nodeValue || '').trim()) childChunks.push(c.cloneNode(true));
              return;
            }
            if (c.nodeType !== 1) return;
            childChunks.push(c.cloneNode(true));
          });
          chunks.push({ parent: dstWrap, el: formShell, follow: childChunks });
        } else if (tag === 'ul' || tag === 'ol') {
          var listShell = n.cloneNode(false);
          var items = Array.prototype.slice.call(n.children).map(function (li) { return li.cloneNode(true); });
          chunks.push({ parent: dstWrap, el: listShell, follow: items });
        } else {
          chunks.push({ parent: dstWrap, el: n.cloneNode(true) });
        }
      }
    });
    return chunks;
  }

  function flashAndBeep(el, major, isFinal) {
    try { el.classList.add('pjax-chunk'); } catch (_) {}
    var targetPerf = null;
    if (major) {
      var freq = isFinal ? 391.995 : 783.99; // G4 for final, G5 otherwise
      if (typeof window.__mpd_scheduleBeepSyncEx === 'function') {
        try { targetPerf = window.__mpd_scheduleBeepSyncEx(freq, 70); } catch (_) { targetPerf = null; }
      } else if (typeof window.__mpd_scheduleBeepSync === 'function' && !isFinal) {
        try { targetPerf = window.__mpd_scheduleBeepSync(70); } catch (_) { targetPerf = null; }
      }
    }
    function show() {
      el.classList.add('pjax-on');
      el.classList.add('pjax-flash');
      requestAnimationFrame(function () { el.classList.remove('pjax-flash'); });
      if (major && (!targetPerf) && typeof window.__mpd_chunkBeepImmediate === 'function') {
        try { window.__mpd_chunkBeepImmediate(); } catch (_) {}
      }
    }
    if (targetPerf && typeof targetPerf === 'number') {
      requestAnimationFrame(function step(ts) {
        if (ts >= targetPerf - 1) { show(); } else { requestAnimationFrame(step); }
      });
    } else {
      requestAnimationFrame(show);
    }
  }

  function progressiveReplace(doc) {
    var srcMain = doc.querySelector(MAIN);
    var dstMain = document.querySelector(MAIN);
    if (!srcMain || !dstMain) return false;
    dstMain.innerHTML = '';
    window.scrollTo(0, 0);

    var chunks = buildChunks(srcMain, dstMain);
    var i = 0;
    function next() {
      if (i >= chunks.length) { initMessages(document); return; }
      var c = chunks[i++];
      var parent = c.parent;
      var el = c.el;
      parent.appendChild(el);
      var isLastAfterThis = (i >= chunks.length) && !(c.follow && c.follow.length);
      flashAndBeep(el, true, isLastAfterThis);
      // If list shell with follow items: show items strictly after shell
      if (c.follow && c.follow.length) {
        var j = 0;
        function nextItem() {
          if (j >= c.follow.length) { setTimeout(next, 60); return; }
          var item = c.follow[j++];
          el.appendChild(item);
          var willBeLast = (j >= c.follow.length) && (i >= chunks.length);
          flashAndBeep(item, true, willBeLast);
          setTimeout(nextItem, 50);
        }
        setTimeout(nextItem, 60);
      } else {
        setTimeout(next, 70);
      }
    }
    next();
    return true;
  }

  function navigate(url, push) {
    return fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.text(); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        swapHeader(doc);
        var ok = progressiveReplace(doc);
        if (!ok) { window.location.href = url; return; }
        var title = doc.querySelector('title');
        if (title) document.title = title.textContent;
        if (push) history.pushState({ pjax: true }, '', url);
      })
      .catch(function () { window.location.href = url; });
  }

  function onClick(e) {
    if (isModifiedClick(e)) return;
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    if (a.hasAttribute('download') || a.getAttribute('target')) return;
    var href = a.getAttribute('href');
    if (!href || href.indexOf('#') === 0) return;
    if (!isInternal(href)) return;
    if (a.matches('[data-no-pjax]')) return;
    e.preventDefault();
    navigate(a.href, true);
  }

  function onPop() { navigate(location.href, false); }

  function init() {
    document.addEventListener('click', onClick);
    window.addEventListener('popstate', onPop);
    initMessages(document);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
