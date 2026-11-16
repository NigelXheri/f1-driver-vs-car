/* THE SCIENCE OF SPEED — presentation layer.
   Scroll reveals, count-ups, tooltips, parallax and the hero animation.
   No research data lives here: numbers are only re-displayed from the page itself. */
(function () {
  'use strict';
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  if (window.__sosFallback) clearTimeout(window.__sosFallback);

  const root = document.documentElement;
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.prototype.slice.call((c || document).querySelectorAll(s));
  const mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  let reduce = mq.matches;
  let paused = false;
  const hasIO = 'IntersectionObserver' in window;

  /* ---------- count-up: animates the number already in the text, then restores it exactly ---------- */
  const NUM = /^(\s*)([−+-]?)(\d[\d,]*\.?\d*|\.\d+)([\s\S]*)$/;
  function numberNode(el) {
    for (const n of el.childNodes) if (n.nodeType === 3 && NUM.test(n.nodeValue)) return n;
    return null;
  }
  function countUp(el) {
    if (reduce || !el) return;
    const node = numberNode(el);
    if (!node) return;
    const full = node.nodeValue;
    const [, pre, sign, num, rest] = full.match(NUM);
    const dec = (num.split('.')[1] || '').length;
    const comma = num.indexOf(',') > -1;
    const target = parseFloat(num.replace(/,/g, ''));
    const fmt = v => {
      let [i, d] = v.toFixed(dec).split('.');
      if (comma) i = i.replace(/\B(?=(\d{3})+$)/g, ',');
      return d ? i + '.' + d : i;
    };
    if (el.__cu) cancelAnimationFrame(el.__cu);
    const t0 = performance.now(), dur = 1300;
    const step = now => {
      const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
      node.nodeValue = p < 1 ? pre + sign + fmt(target * e) + rest : full;
      if (p < 1) el.__cu = requestAnimationFrame(step);
    };
    el.__cu = requestAnimationFrame(step);
  }
  function replay(el) {
    if (!el || reduce || !el.classList.contains('is-in')) return;
    el.classList.remove('is-in');
    void el.offsetWidth;
    requestAnimationFrame(() => el.classList.add('is-in'));
  }
  window.SOS = { countUp, replay };

  /* ---------- p-value / correlation strips: re-draw numbers read from the saved table ---------- */
  function buildPStrip() {
    const host = $('#p-strip');
    const rows = $$('.permutation tbody tr');
    if (!host || !rows.length) return;
    const names = ['Approx. p', 'Permutation p', 'Holm p'];
    let i = 0;
    const groups = rows.map(tr => {
      const name = tr.querySelector('th').textContent;
      const v = $$('td', tr).map(td => td.textContent.trim());   // ρ, approx., permutation, Holm
      const rho = parseFloat(v[0]);
      const lanes = names.map((label, k) => {
        const p = parseFloat(v[k + 1]);
        const tip = `${name} · ${label} = ${v[k + 1]}`;
        return `<div class="p-lane ${k === 2 ? 'holm' : ''}" style="--i:${i++}" data-tip="${tip}"><span>${label}</span><div class="p-lane-track"><i class="p-alpha" style="left:5%"></i><i class="p-dot" style="--x:${(p * 100).toFixed(2)}%"></i></div><b>${v[k + 1]}</b></div>`;
      }).join('');
      return `<div class="p-group"><h4>${name}</h4>
        <div class="corr-row" data-tip="${name} · Spearman ρ = ${v[0]}"><span>ρ (SPEARMAN)</span><div class="corr-track"><i class="corr-zero"></i><i class="corr-fill" style="--r:${rho}"></i></div><b>${v[0]}</b></div>
        ${lanes}</div>`;
    }).join('');
    host.innerHTML = `<p class="eyebrow">THE SAVED TEST VALUES ON THEIR SCALES · p-VALUES 0–1, THRESHOLD α = 0.05 · ρ −1 TO +1</p>${groups}`;
  }

  /* ---------- reveal on scroll ---------- */
  const revealSel = ['.opening > *', '.section-heading', '.chart-panel', '.insight-row article', '.mini-panel',
    '.career-layout > *', '.stat-feature', '.permutation', '.glossary details', '.pipeline li',
    '.archive-links a', '.audit-note', '.telemetry > *'].join(',');
  const animSel = ['#pace-chart', '#career-chart', '#progress-chart', '#race-scrub', '.gap-meter', '.corr-gauges',
    '.mini-panel', '.track-panel', '.p-scale', '.ci-panel', '#p-strip', '.pipeline'].join(',');
  const countSel = '.telemetry strong, .metric, .big-number, .comparison b, .stat-numbers strong, .corr-row b';

  function setupReveals() {
    $$(revealSel).forEach(el => {
      el.classList.add('reveal');
      const i = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.style.setProperty('--rd', Math.min(i, 6));
    });
    const anim = $$(animSel);
    if (!hasIO) {
      $$('.reveal').concat(anim).forEach(el => el.classList.add('is-in'));
      return;
    }
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        io.unobserve(en.target);
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });
    $$('.reveal').concat(anim).forEach(el => io.observe(el));

    const co = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        countUp(en.target);
        co.unobserve(en.target);
      });
    }, { threshold: 0.6 });
    $$(countSel).forEach(el => co.observe(el));
  }

  /* ---------- tooltip ---------- */
  function setupTooltip() {
    const tip = document.createElement('div');
    tip.className = 'tooltip';
    tip.id = 'tooltip';
    tip.setAttribute('role', 'tooltip');
    document.body.appendChild(tip);
    const place = (px, py) => {
      const w = tip.offsetWidth, h = tip.offsetHeight;
      const left = Math.min(Math.max(px + 14, 8), window.innerWidth - w - 8);
      let top = py - h - 14;
      if (top < 8) top = py + 20;
      tip.style.transform = `translate(${left}px,${top}px)`;
    };
    const show = (el, px, py) => {
      const text = el.getAttribute('data-tip');
      if (!text) return;
      if (el.hasAttribute('title')) el.removeAttribute('title');   // avoid the native tooltip doubling up
      tip.textContent = text;
      tip.classList.add('on');
      place(px, py);
    };
    const hide = () => tip.classList.remove('on');
    document.addEventListener('mouseover', e => {
      const el = e.target.closest && e.target.closest('[data-tip]');
      if (el) show(el, e.clientX, e.clientY);
    });
    document.addEventListener('mousemove', e => { if (tip.classList.contains('on')) place(e.clientX, e.clientY); });
    document.addEventListener('mouseout', e => {
      const el = e.target.closest && e.target.closest('[data-tip]');
      if (el && !(e.relatedTarget && el.contains(e.relatedTarget))) hide();
    });
    document.addEventListener('focusin', e => {
      const el = e.target.closest && e.target.closest('[data-tip]');
      if (!el) return;
      const r = el.getBoundingClientRect();
      show(el, r.left + r.width / 2, r.top);
    });
    document.addEventListener('focusout', hide);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') hide(); });
    window.addEventListener('scroll', hide, { passive: true });
  }

  /* ---------- scroll progress, parallax, active navigation ---------- */
  function setupScroll() {
    const bar = $('#scroll-progress');
    const par = $$('[data-parallax]');
    const links = $$('header nav a[href^="#"]');
    const secs = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
    let ticking = false;
    const update = () => {
      ticking = false;
      const sy = window.pageYOffset, max = root.scrollHeight - window.innerHeight;
      if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(1, sy / max) : 0})`;
      if (!reduce && !paused) {
        const vh = window.innerHeight;
        par.forEach(el => {
          const r = el.parentElement.getBoundingClientRect();
          if (r.bottom < -300 || r.top > vh + 300) return;
          const f = parseFloat(el.getAttribute('data-parallax')) || 0;
          el.style.setProperty('--py', ((r.top + r.height / 2 - vh / 2) * f).toFixed(1) + 'px');
        });
      }
      let current = null;
      secs.forEach(s => { if (s.getBoundingClientRect().top <= 140) current = s; });
      links.forEach(a => {
        if (current && a.getAttribute('href') === '#' + current.id) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
    };
    const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
  }

  /* ---------- hero: speed streaks + a dot running an illustrative racing line ---------- */
  function setupHero() {
    const hero = $('.hero'), cv = $('#hero-canvas');
    if (!hero || !cv || !cv.getContext) return;
    const ctx = cv.getContext('2d');
    const path = $('#hero-racing-line'), dot = $('#hero-dot'), trail = $$('#hero-trail circle');
    let w = 0, h = 0, streaks = [], raf = 0, last = 0, visible = true, lineLen = 0;
    const flow = $('.line-flow');
    const make = init => ({
      x: init ? Math.random() * w : w + Math.random() * 240,
      y: Math.random() * h,
      l: 60 + Math.random() * 240,
      v: 0.18 + Math.random() * 0.62,
      a: 0.05 + Math.random() * 0.16,
      red: Math.random() < 0.18,
      t: Math.random() < 0.22 ? 2 : 1
    });
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = hero.clientWidth; h = hero.clientHeight;
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(Math.min(44, Math.max(16, w / 36)));
      streaks = Array.from({ length: n }, () => make(true));
      draw(0);
    };
    const draw = dt => {
      ctx.clearRect(0, 0, w, h);
      for (const s of streaks) {
        s.x -= s.v * dt * 0.5;
        if (s.x + s.l < 0) Object.assign(s, make(false));
        const g = ctx.createLinearGradient(s.x, 0, s.x + s.l, 0);
        const c = s.red ? '255,59,48' : '197,204,214';
        g.addColorStop(0, `rgba(${c},0)`);
        g.addColorStop(1, `rgba(${c},${s.a})`);
        ctx.fillStyle = g;
        ctx.fillRect(s.x, s.y, s.l, s.t);
      }
    };
    const moveDot = t => {
      if (!path || !dot) return;
      const lap = 15000, base = ((t % lap) / lap) * lineLen;
      let p = path.getPointAtLength(base);
      dot.setAttribute('cx', p.x); dot.setAttribute('cy', p.y);
      trail.forEach((c, i) => {
        p = path.getPointAtLength((base - (i + 1) * 15 + lineLen) % lineLen);
        c.setAttribute('cx', p.x); c.setAttribute('cy', p.y);
        c.style.opacity = (0.5 - i * 0.075).toFixed(2);
      });
    };
    const frame = t => {
      raf = requestAnimationFrame(frame);
      const dt = Math.min(50, t - last || 16); last = t;
      if (paused) return;
      draw(dt); moveDot(t);
    };
    const start = () => { if (!raf && !reduce && visible && !document.hidden) { last = 0; raf = requestAnimationFrame(frame); } };
    const stop = () => { if (raf) { cancelAnimationFrame(raf); raf = 0; } };

    if (path && path.getTotalLength) lineLen = path.getTotalLength();
    resize();
    let rt;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(resize, 150); });
    if (hasIO) new IntersectionObserver(es => { visible = es[0].isIntersecting; visible ? start() : stop(); }).observe(hero);
    document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));

    trail.forEach(c => (c.style.display = 'none'));
    if (!reduce) {
      if (flow) flow.style.opacity = '.5';
      setTimeout(() => { if (dot) dot.style.opacity = '1'; trail.forEach(c => (c.style.display = '')); }, 4300);
      start();
    } else if (path) {
      moveDot(0); if (dot) dot.style.opacity = '0';
    }
    if (mq.addEventListener) mq.addEventListener('change', e => { reduce = e.matches; reduce ? stop() : start(); });

    const btn = $('.motion-toggle');
    if (btn) btn.addEventListener('click', () => {
      paused = !paused;
      root.classList.toggle('motion-paused', paused);
      btn.setAttribute('aria-pressed', String(paused));
      btn.textContent = paused ? 'RESUME MOTION' : 'PAUSE MOTION';
    });
  }

  function init() {
    buildPStrip();
    setupReveals();
    setupTooltip();
    setupScroll();
    setupHero();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
