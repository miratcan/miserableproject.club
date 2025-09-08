// Minimal DOS-style block caret for inputs and textareas
// Hides native caret and overlays a blinking block at the caret position
// Works with monospace DOS font used in this app

(function () {
  const selector = '.screen input[type="text"], .screen input:not([type]), .screen textarea';
  const screen = document.querySelector('.screen');
  if (!screen) return;

  const caretEl = document.createElement('div');
  caretEl.className = 'dos-caret';
  caretEl.style.display = 'none';
  screen.appendChild(caretEl);

  // mirror element for measuring caret coordinates
  const mirror = document.createElement('div');
  mirror.style.position = 'absolute';
  mirror.style.visibility = 'hidden';
  mirror.style.whiteSpace = 'pre-wrap';
  mirror.style.wordWrap = 'break-word';
  mirror.style.pointerEvents = 'none';
  mirror.style.left = '-9999px';
  mirror.style.top = '0';
  screen.appendChild(mirror);

  function copyStyles(src, dest) {
    const cs = window.getComputedStyle(src);
    const props = [
      'fontSize','fontFamily','fontWeight','lineHeight','letterSpacing','textTransform',
      'paddingTop','paddingRight','paddingBottom','paddingLeft','borderTopWidth','borderRightWidth','borderBottomWidth','borderLeftWidth',
      'boxSizing','width'
    ];
    props.forEach(p => dest.style[p] = cs[p]);
  }

  function getCaretPos(el) {
    const isTextarea = el.nodeName === 'TEXTAREA';
    copyStyles(el, mirror);
    mirror.style.width = el.clientWidth + 'px';
    // normalize value up to caret
    const val = el.value || '';
    const start = el.selectionStart || 0;
    const before = val.substring(0, start);
    const afterChar = val.substring(start, start + 1) || ' ';
    mirror.textContent = before;
    // add a span at caret
    const span = document.createElement('span');
    span.textContent = afterChar;
    mirror.appendChild(span);

    const mRect = mirror.getBoundingClientRect();
    const sRect = screen.getBoundingClientRect();
    const elRect = el.getBoundingClientRect();

    // caret position relative to mirror
    const spanRect = span.getBoundingClientRect();

    // account for input scroll
    const scrollLeft = el.scrollLeft || 0;
    const scrollTop = el.scrollTop || 0;

    const left = elRect.left - sRect.left + (spanRect.left - mRect.left) - scrollLeft;
    const top = elRect.top - sRect.top + (spanRect.top - mRect.top) - scrollTop;

    // approximate block size from line-height and char width
    const cs = window.getComputedStyle(el);
    const lh = parseFloat(cs.lineHeight) || el.clientHeight;
    const ch = 16;
    let cw = spanRect.width;
    if (!cw || cw < 2) cw = parseFloat(cs.fontSize) * 0.6;

    return { left, top, width: cw, height: ch };
  }

  function showCaret(el) {
    try {
      const p = getCaretPos(el);
      caretEl.style.display = 'block';
      caretEl.style.left = Math.round(p.left) + 'px';
      caretEl.style.top = Math.round(p.top) + 'px';
      caretEl.style.width = Math.round(p.width) + 'px';
      caretEl.style.height = Math.round(p.height) + 'px';
    } catch (e) {
      // ignore
    }
  }

  function hideCaret() {
    caretEl.style.display = 'none';
  }

  function attach(el) {
    function update() { showCaret(el); }
    el.addEventListener('focus', update);
    el.addEventListener('keyup', update);
    el.addEventListener('click', update);
    el.addEventListener('input', update);
    el.addEventListener('scroll', update);
    el.addEventListener('blur', hideCaret);
  }

  function init() {
    document.querySelectorAll(selector).forEach(attach);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

