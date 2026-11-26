(function () {
  var canvas = document.getElementById('sky');
  var ctx = canvas.getContext('2d');
  var still = window.matchMedia('(prefers-reduced-motion: reduce)');
  var fine = window.matchMedia('(pointer: fine)');

  // Three depths. Having the near layer move and react more than the far one
  // is what reads as distance — a single flat field of dots reads as noise.
  var LAYERS = [
    { depth: 0.30, size: 0.65, alpha: 0.26, drift: 3,  twinkle: 0.7 },
    { depth: 0.62, size: 0.95, alpha: 0.38, drift: 6,  twinkle: 1.0 },
    { depth: 1.00, size: 1.40, alpha: 0.55, drift: 10, twinkle: 1.4 }
  ];
  var REACH = 150;   // px around the cursor that brightens
  var SHIFT = 26;    // px of parallax at the nearest layer

  var stars = [], w = 0, h = 0, raf = null, last = 0;
  var pointer = { nx: 0.5, ny: 0.5, x: -1e4, y: -1e4, live: false };
  var eased = { x: 0.5, y: 0.5 };

  function build() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = canvas.clientWidth;
    h = canvas.clientHeight;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Counted by area, so a phone doesn't draw a desktop's worth of stars.
    var count = Math.min(Math.round(w * h / 5200), 260);
    stars = [];
    for (var i = 0; i < count; i++) {
      var layer = LAYERS[i % LAYERS.length];
      stars.push({
        layer: layer,
        x: Math.random() * w,
        y: Math.random() * h,
        r: layer.size * (0.6 + Math.random() * 0.8),
        vx: (Math.random() - 0.5) * layer.drift,
        vy: layer.drift * (0.25 + Math.random() * 0.4),
        phase: Math.random() * Math.PI * 2,
        // A handful carry the brand colour. Any more and it stops being a
        // night sky and starts being a logo.
        warm: Math.random() < 0.07
      });
    }
  }

  function paint(now, moving) {
    ctx.clearRect(0, 0, w, h);
    var px = (eased.x - 0.5) * SHIFT;
    var py = (eased.y - 0.5) * SHIFT;

    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var x = s.x - px * s.layer.depth;
      var y = s.y - py * s.layer.depth;
      var a = s.layer.alpha;
      var r = s.r;

      if (moving) {
        a *= 0.64 + 0.36 * Math.sin(now * 0.0011 * s.layer.twinkle + s.phase);
      }
      if (pointer.live) {
        var dx = x - pointer.x, dy = y - pointer.y;
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < REACH) {
          var near = 1 - d / REACH;
          a = Math.min(1, a + near * near * 0.55);
          r += near * near * 1.1;
        }
      }

      ctx.globalAlpha = a;
      ctx.fillStyle = s.warm ? '#FF2D6F' : '#E9EBF0';
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function frame(now) {
    var dt = Math.min((now - last) / 1000, 0.05);
    last = now;
    eased.x += (pointer.nx - eased.x) * 0.05;
    eased.y += (pointer.ny - eased.y) * 0.05;

    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      if (s.y - 3 > h) { s.y = -3; s.x = Math.random() * w; }
      if (s.x < -3) s.x = w + 3; else if (s.x > w + 3) s.x = -3;
    }
    paint(now, true);
    raf = requestAnimationFrame(frame);
  }

  function start() {
    stop();
    if (still.matches) { paint(0, false); return; }   // one static sky, still a sky
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    if (raf !== null) { cancelAnimationFrame(raf); raf = null; }
  }

  build();
  start();

  // Mobile browsers fire resize when the URL bar slides away. Rebuilding on
  // that would reshuffle the whole sky mid-scroll, so only a real change counts.
  var lastW = window.innerWidth, lastH = window.innerHeight;
  window.addEventListener('resize', function () {
    if (window.innerWidth === lastW && Math.abs(window.innerHeight - lastH) < 120) return;
    lastW = window.innerWidth; lastH = window.innerHeight;
    build();
    start();
  });

  // Hover only where there is a real cursor; a touch screen has none, and the
  // drift is the whole effect there.
  if (fine.matches) {
    window.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse') return;
      pointer.live = true;
      pointer.x = e.clientX;
      pointer.y = e.clientY;
      pointer.nx = e.clientX / window.innerWidth;
      pointer.ny = e.clientY / window.innerHeight;
      if (still.matches) paint(0, false);
    }, { passive: true });

    // pointerleave doesn't fire on window. A mouseout with no relatedTarget
    // is the one event that reliably means "the cursor left the page".
    var release = function () {
      pointer.live = false;
      pointer.nx = 0.5;
      pointer.ny = 0.5;
      if (still.matches) paint(0, false);
    };
    document.addEventListener('mouseout', function (e) {
      if (!e.relatedTarget) release();
    });
    window.addEventListener('blur', release);
  }

  // Nothing to animate for a tab nobody is looking at.
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });
})();
