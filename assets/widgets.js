/* Interactive figures for the book — dependency-free, offline, no CDN.
 *
 * Each `<figure class="widget" data-widget="NAME">` in a chapter is wired up on
 * load by the matching entry in WIDGETS below. A widget builds a responsive
 * hi-DPI canvas plus its controls inside the figure (before the <figcaption>),
 * and redraws on input and on resize. To add a widget: write a WIDGETS[name]
 * function and reference it from a chapter with the data attribute.
 *
 * Colors mirror assets/style.css. Keep them in sync with the :root palette.
 */
(function () {
  "use strict";

  var C = {
    ink: "#17181b",
    inkSoft: "#3b3d42",
    muted: "#6a6d73",
    rule: "#e4e3dd",
    ruleStrong: "#cfcdc4",
    accent: "#274b6d",
    accentSoft: "#eaf0f6",
    amber: "#9c6b12",
    grid: "#ededea",
  };

  function makeCanvas(parent, before, heightRatio) {
    var canvas = document.createElement("canvas");
    canvas.className = "widget-canvas";
    parent.insertBefore(canvas, before);
    var ctx = canvas.getContext("2d");
    function size() {
      var cssW = canvas.clientWidth || parent.clientWidth || 600;
      var cssH = Math.round(cssW * heightRatio);
      var dpr = window.devicePixelRatio || 1;
      canvas.style.height = cssH + "px";
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { w: cssW, h: cssH };
    }
    return { canvas: canvas, ctx: ctx, size: size };
  }

  function addSlider(parent, before, label, min, max, step, value) {
    var row = document.createElement("label");
    row.className = "widget-slider";
    var name = document.createElement("span");
    name.className = "widget-slider-label";
    name.innerHTML = label;
    var input = document.createElement("input");
    input.type = "range";
    input.min = min;
    input.max = max;
    input.step = step;
    input.value = value;
    row.appendChild(name);
    row.appendChild(input);
    parent.insertBefore(row, before);
    return input;
  }

  function readoutBox(parent, before) {
    var box = document.createElement("div");
    box.className = "widget-readout";
    parent.insertBefore(box, before);
    return box;
  }

  function controlsBox(parent, before) {
    var box = document.createElement("div");
    box.className = "widget-controls";
    parent.insertBefore(box, before);
    return box;
  }

  function drawAxes(ctx, dim, mx, my, xr, yr) {
    ctx.clearRect(0, 0, dim.w, dim.h);
    ctx.lineWidth = 1;
    ctx.strokeStyle = C.grid;
    var i;
    for (i = Math.ceil(xr[0]); i <= Math.floor(xr[1]); i++) {
      ctx.beginPath();
      ctx.moveTo(mx(i), 0);
      ctx.lineTo(mx(i), dim.h);
      ctx.stroke();
    }
    ctx.strokeStyle = C.ruleStrong;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(mx(xr[0]), my(yr[0]));
    ctx.lineTo(mx(xr[1]), my(yr[0]));
    ctx.moveTo(mx(xr[0]), my(yr[0]));
    ctx.lineTo(mx(xr[0]), my(yr[1]));
    ctx.stroke();
  }

  function plotFn(ctx, mx, my, xr, f, color, width) {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineJoin = "round";
    ctx.beginPath();
    var n = 240;
    for (var i = 0; i <= n; i++) {
      var x = xr[0] + ((xr[1] - xr[0]) * i) / n;
      var px = mx(x);
      var py = my(f(x));
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
  }

  function dot(ctx, x, y, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  var WIDGETS = {};

  // The bias-variance tradeoff for ridge shrinkage of one coordinate.
  // Observe z ~ Normal(beta, sigma^2); the ridge estimate is z / (1 + lambda).
  //   bias^2(lambda) = (lambda / (1 + lambda))^2 * beta^2
  //   variance(lambda) = sigma^2 / (1 + lambda)^2
  //   risk = bias^2 + variance,  minimized at lambda* = sigma^2 / beta^2.
  // With beta^2 = sigma^2 = 1 the minimum sits at lambda* = 1, and the risk
  // there (0.5) is half the unbiased risk at lambda = 0 (1.0): a little bias
  // beats none.
  WIDGETS["bias-variance"] = function (figure, cap) {
    var beta2 = 1;
    var sigma2 = 1;
    var xr = [0, 6];
    var yr = [0, 1.15];
    var lamStar = sigma2 / beta2;

    var bias2 = function (l) {
      return (l / (1 + l)) * (l / (1 + l)) * beta2;
    };
    var variance = function (l) {
      return sigma2 / ((1 + l) * (1 + l));
    };
    var risk = function (l) {
      return bias2(l) + variance(l);
    };

    var cv = makeCanvas(figure, cap, 0.6);
    var controls = controlsBox(figure, cap);
    var readout = readoutBox(figure, cap);
    var lamInput = addSlider(
      controls,
      null,
      "penalty&nbsp;<em>&lambda;</em>",
      0,
      6,
      0.05,
      0
    );

    function draw() {
      var dim = cv.size();
      var padL = 30;
      var pad = 10;
      var mx = function (x) {
        return padL + ((x - xr[0]) * (dim.w - padL - pad)) / (xr[1] - xr[0]);
      };
      var my = function (y) {
        return dim.h - 22 - ((y - yr[0]) * (dim.h - 22 - pad)) / (yr[1] - yr[0]);
      };
      var ctx = cv.ctx;
      var lam = parseFloat(lamInput.value);

      drawAxes(ctx, dim, mx, my, xr, yr);

      // The unbiased baseline (risk at lambda = 0) as a faint reference.
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = C.ruleStrong;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(mx(xr[0]), my(risk(0)));
      ctx.lineTo(mx(xr[1]), my(risk(0)));
      ctx.stroke();
      ctx.restore();

      plotFn(ctx, mx, my, xr, bias2, C.amber, 2);
      plotFn(ctx, mx, my, xr, variance, C.accent, 2);
      plotFn(ctx, mx, my, xr, risk, C.ink, 2.6);

      // Current penalty: a vertical guide with a dot on each curve.
      ctx.strokeStyle = C.muted;
      ctx.lineWidth = 1.25;
      ctx.beginPath();
      ctx.moveTo(mx(lam), my(yr[0]));
      ctx.lineTo(mx(lam), my(yr[1]));
      ctx.stroke();
      dot(ctx, mx(lam), my(bias2(lam)), 4.5, C.amber);
      dot(ctx, mx(lam), my(variance(lam)), 4.5, C.accent);
      dot(ctx, mx(lam), my(risk(lam)), 5, C.ink);

      // x-axis label.
      ctx.fillStyle = C.muted;
      ctx.font = "11px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText("penalty λ →", dim.w - pad, dim.h - 6);

      readout.innerHTML =
        '<span class="widget-num bias">bias² = ' +
        bias2(lam).toFixed(3) +
        "</span>" +
        '<span class="widget-num var">variance = ' +
        variance(lam).toFixed(3) +
        "</span>" +
        '<span class="widget-num total">total risk = ' +
        risk(lam).toFixed(3) +
        (lam === 0 ? " (unbiased)" : "") +
        "</span>" +
        '<span class="widget-num opt">best λ* = ' +
        lamStar.toFixed(2) +
        " → risk " +
        risk(lamStar).toFixed(3) +
        "</span>";
    }

    lamInput.addEventListener("input", draw);
    window.addEventListener("resize", draw);
    draw();
  };

  // The central limit theorem by simulation. Draw n values from a skewed source
  // (Exponential with mean 1, variance 1), average them, repeat M times to build
  // the sampling distribution of the mean, and overlay Normal(1, 1/n). As n
  // grows, the skewed histogram pulls into the bell despite the skewed source.
  WIDGETS["clt"] = function (figure, cap) {
    var mu = 1;
    var sigma = 1;
    var xr = [0, 4];
    var M = 2400;
    var bins = 46;
    var bw = (xr[1] - xr[0]) / bins;

    var cv = makeCanvas(figure, cap, 0.62);
    var controls = controlsBox(figure, cap);
    var readout = readoutBox(figure, cap);
    var nInput = addSlider(
      controls,
      null,
      "sample size&nbsp;<em>n</em>",
      1,
      40,
      1,
      1
    );
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "widget-button";
    btn.textContent = "Resample";
    controls.appendChild(btn);

    var cache = null;

    function expSample() {
      return -Math.log(1 - Math.random()); // Exponential(1): skewed, mean 1.
    }

    function simulate(n) {
      var counts = new Array(bins);
      for (var b = 0; b < bins; b++) counts[b] = 0;
      for (var t = 0; t < M; t++) {
        var s = 0;
        for (var i = 0; i < n; i++) s += expSample();
        var m = s / n;
        var bin = Math.floor((m - xr[0]) / bw);
        if (bin >= 0 && bin < bins) counts[bin] += 1;
      }
      return counts.map(function (c) {
        return c / (M * bw); // Convert to a density so the normal overlays it.
      });
    }

    function normalPdf(x, m, sd) {
      var z = (x - m) / sd;
      return Math.exp(-0.5 * z * z) / (sd * Math.sqrt(2 * Math.PI));
    }

    function draw(resim) {
      var n = Math.round(parseFloat(nInput.value));
      if (resim || !cache || cache.n !== n) cache = { n: n, dens: simulate(n) };
      var dim = cv.size();
      var padL = 30;
      var pad = 10;
      var sd = sigma / Math.sqrt(n);
      var ymax = Math.max(normalPdf(mu, mu, sd), Math.max.apply(null, cache.dens));
      ymax = Math.max(ymax, 1.05) * 1.12;
      var yr = [0, ymax];
      var mx = function (x) {
        return padL + ((x - xr[0]) * (dim.w - padL - pad)) / (xr[1] - xr[0]);
      };
      var my = function (y) {
        return dim.h - 22 - ((y - yr[0]) * (dim.h - 22 - pad)) / (yr[1] - yr[0]);
      };
      var ctx = cv.ctx;
      drawAxes(ctx, dim, mx, my, xr, yr);

      // Histogram of the sample means.
      ctx.fillStyle = C.accentSoft;
      ctx.strokeStyle = C.accent;
      ctx.lineWidth = 1;
      for (var b = 0; b < bins; b++) {
        var x0 = mx(xr[0] + b * bw);
        var x1 = mx(xr[0] + (b + 1) * bw);
        var y0 = my(0);
        var y1 = my(cache.dens[b]);
        if (cache.dens[b] > 0) {
          ctx.fillRect(x0, y1, x1 - x0, y0 - y1);
          ctx.strokeRect(x0, y1, x1 - x0, y0 - y1);
        }
      }

      // The skewed source density (Exponential), a faint fixed reference.
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = C.amber;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      for (var i = 0; i <= 200; i++) {
        var xx = xr[0] + ((xr[1] - xr[0]) * i) / 200;
        var yy = xx >= 0 ? Math.exp(-xx) : 0;
        if (i === 0) ctx.moveTo(mx(xx), my(yy));
        else ctx.lineTo(mx(xx), my(yy));
      }
      ctx.stroke();
      ctx.restore();

      // The normal approximation the CLT promises.
      ctx.strokeStyle = C.ink;
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      for (var k = 0; k <= 200; k++) {
        var x = xr[0] + ((xr[1] - xr[0]) * k) / 200;
        var y = normalPdf(x, mu, sd);
        if (k === 0) ctx.moveTo(mx(x), my(y));
        else ctx.lineTo(mx(x), my(y));
      }
      ctx.stroke();

      ctx.fillStyle = C.muted;
      ctx.font = "11px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText("sample mean →", dim.w - pad, dim.h - 6);

      readout.innerHTML =
        '<span class="widget-num bias">skewed source: Exponential</span>' +
        '<span class="widget-num total">histogram: mean of n draws</span>' +
        '<span class="widget-num var">overlay: Normal(1, 1/n), n = ' +
        n +
        "</span>";
    }

    nInput.addEventListener("input", function () {
      draw(true);
    });
    btn.addEventListener("click", function () {
      draw(true);
    });
    window.addEventListener("resize", function () {
      draw(false);
    });
    draw(true);
  };

  function boot() {
    var figures = document.querySelectorAll("figure.widget[data-widget]");
    Array.prototype.forEach.call(figures, function (figure) {
      var name = figure.getAttribute("data-widget");
      var builder = WIDGETS[name];
      if (!builder) return;
      var cap = figure.querySelector("figcaption");
      builder(figure, cap);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
