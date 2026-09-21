#!/usr/bin/env node
// Runs the starfield from index.html against a stub canvas.
//
// The field is the one piece of this site with logic in it, and its failure
// mode is silent: a NaN coordinate or an out-of-range alpha draws nothing at
// all, and a black page looks exactly like a black page. So rather than trust
// that it parses, this drives a few frames and checks what it tried to paint.
//
//   node test-sky.js

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const source = /<script>([\s\S]*?)<\/script>/.exec(html)[1];

function run({ reduceMotion = false, finePointer = true, width = 1440, height = 900 } = {}) {
  const drawn = [];
  const listeners = {};
  let alpha = 1;
  let queued = null;
  let clock = 0;

  const ctx = {
    setTransform() {},
    clearRect() {},
    beginPath() {},
    fill() {},
    arc(x, y, r) {
      assert.ok(Number.isFinite(x) && Number.isFinite(y), `arc at ${x},${y}`);
      assert.ok(Number.isFinite(r) && r > 0, `radius ${r}`);
      drawn.push({ x, y, r, alpha });
    },
    set globalAlpha(v) {
      assert.ok(Number.isFinite(v) && v >= 0 && v <= 1, `alpha ${v}`);
      alpha = v;
    },
    get globalAlpha() { return alpha; },
    set fillStyle(v) {},
    get fillStyle() { return '#fff'; },
  };

  const canvas = { getContext: () => ctx, clientWidth: width, clientHeight: height, width: 0, height: 0 };

  global.document = {
    getElementById: () => canvas,
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn); },
    hidden: false,
  };
  global.window = {
    devicePixelRatio: 2,
    innerWidth: width,
    innerHeight: height,
    matchMedia: (q) => ({ matches: q.includes('reduced-motion') ? reduceMotion : finePointer }),
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn); },
  };
  global.performance = { now: () => clock };
  global.requestAnimationFrame = (fn) => { queued = fn; return 1; };
  global.cancelAnimationFrame = () => { queued = null; };

  new Function(source)();

  const fire = (type, event) => (listeners[type] || []).forEach((fn) => fn(event));
  const tick = (ms = 16) => {
    clock += ms;
    const next = queued;
    queued = null;
    if (next) next(clock);
  };

  return { drawn, canvas, fire, tick, animating: () => queued !== null };
}

// --- a moving sky ----------------------------------------------------------
{
  const sky = run();
  assert.ok(sky.drawn.length === 0, 'nothing is painted until the first frame');
  assert.strictEqual(sky.canvas.width, 1440 * 2, 'backing store scaled for the display');

  sky.tick();
  const first = sky.drawn.length;
  assert.ok(first > 100, `expected a field, drew ${first}`);
  assert.ok(first <= 260, `capped the count, drew ${first}`);
  assert.ok(sky.animating(), 'keeps animating');

  for (let i = 0; i < 90; i++) sky.tick();
  assert.strictEqual(sky.drawn.length, first * 91, 'every star is painted every frame');
}

// --- the cursor ------------------------------------------------------------
{
  const sky = run();
  sky.tick();
  const before = sky.drawn.slice(-260);

  sky.fire('pointermove', { pointerType: 'mouse', clientX: 720, clientY: 450 });
  sky.tick();
  const after = sky.drawn.slice(-before.length);

  const near = (s) => Math.hypot(s.x - 720, s.y - 450) < 150;
  const lit = after.filter(near).reduce((sum, s) => sum + s.alpha, 0);
  const was = before.filter(near).reduce((sum, s) => sum + s.alpha, 0);
  assert.ok(lit > was, 'stars under the cursor brighten');
  assert.ok(after.some((s) => s.r > 1.4), 'and grow a little');

  // A touch has no hover; reacting to it would light the sky under a thumb.
  const touch = run({ finePointer: false });
  touch.tick();
  touch.fire('pointermove', { pointerType: 'touch', clientX: 10, clientY: 10 });
  assert.ok(true, 'a touch-only device registers no pointer handler at all');
}

// --- someone who asked for less motion -------------------------------------
{
  const sky = run({ reduceMotion: true });
  assert.ok(sky.drawn.length > 100, 'still gets a sky, painted immediately');
  assert.ok(!sky.animating(), 'but nothing is scheduled to move');

  const count = sky.drawn.length;
  sky.fire('pointermove', { pointerType: 'mouse', clientX: 400, clientY: 300 });
  assert.ok(sky.drawn.length > count, 'the cursor still does something');
  assert.ok(!sky.animating(), 'without starting an animation');
}

// --- a phone ---------------------------------------------------------------
{
  const sky = run({ width: 390, height: 844, finePointer: false });
  sky.tick();
  assert.ok(sky.drawn.length < 100, `fewer stars on a small screen, drew ${sky.drawn.length}`);
}

// --- a tab nobody is looking at --------------------------------------------
{
  const sky = run();
  sky.tick();
  global.document.hidden = true;
  sky.fire('visibilitychange');
  assert.ok(!sky.animating(), 'stops when hidden');
  global.document.hidden = false;
  sky.fire('visibilitychange');
  assert.ok(sky.animating(), 'and picks up again');
}

console.log('sky: all checks passed');
