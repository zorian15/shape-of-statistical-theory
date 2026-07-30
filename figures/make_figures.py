"""Generate every figure for *The Shape of Statistical Theory* as SVG.

Two kinds of figure live here. **Diagrams** (concepts) are hand-authored SVG
emitted from Python string templates. **Plots** (anything quantitative) are
matplotlib, saved transparent with `svg.fonttype: "none"` so their text inherits
the page fonts. Both draw from the palette constants below, which mirror
`assets/style.css` — keep them in sync.

Run with `python figures/make_figures.py`. Each `fig_*()` returns the path it
wrote and is listed in `FIGURES`; `main()` runs them all. The cover and icons
carry the book's visual identity (a normal bell curve over a shaded area) and
are written to the assets root.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "assets" / "figures"
ASSETS_DIR = ROOT / "assets"

# The book's palette, mirrored from assets/style.css. Keep these in sync.
PAPER = "#f4f3ee"
INK = "#17181b"
INK_SOFT = "#3b3d42"
MUTED = "#6a6d73"
RULE = "#e4e3dd"
RULE_STRONG = "#cfcdc4"
ACCENT = "#274b6d"
ACCENT_SOFT = "#eaf0f6"
AMBER = "#9c6b12"
VIOLET = "#6b4f9c"
BRICK = "#b04a3f"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
SERIF = "'Charter', 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"
MONO = "'SF Mono', 'SFMono-Regular', ui-monospace, Menlo, Consolas, monospace"


def write_svg(name: str, svg: str) -> Path:
    """Write a raw SVG string to the figures directory and return its path."""
    assert name.endswith(".svg"), f"Figure name must end in .svg, got '{name}'."
    assert svg.lstrip().startswith("<svg"), f"Figure '{name}' is not an SVG document."
    path = OUTPUT_DIR / name
    path.write_text(svg, encoding="utf-8")
    return path


def write_root_asset(name: str, svg: str) -> Path:
    """Write a raw SVG string to the assets root (cover, icon) and return its path."""
    assert name.endswith(".svg"), f"Asset name must end in .svg, got '{name}'."
    assert svg.lstrip().startswith("<svg"), f"Asset '{name}' is not an SVG document."
    path = ASSETS_DIR / name
    path.write_text(svg, encoding="utf-8")
    return path


def svg_doc(width: float, height: float, label: str, body: list[str]) -> str:
    """Wrap SVG body elements in a document with the book's default font.

    `label` becomes the accessible description; keep it plain ASCII so it needs
    no escaping. `body` is the list of element strings, in draw order.
    """
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="{SANS}" role="img" aria-label="{label}">'
    )
    return "\n".join([head, *body, "</svg>"])


def arrow_marker(color: str, name: str) -> str:
    """Return a `<defs>` block holding one triangular arrowhead marker."""
    return (
        f'<defs><marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker></defs>'
    )


def node_box(
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    fill: str = "#ffffff",
    stroke: str = RULE_STRONG,
    text_fill: str = INK,
    font_size: float = 12,
    weight: int = 400,
) -> list[str]:
    """Return a rounded rectangle with centered text: the book's labelled chip."""
    stroke_attr = "none" if stroke == "none" else stroke
    return [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" '
        f'fill="{fill}" stroke="{stroke_attr}"/>',
        f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + font_size * 0.35:.1f}" '
        f'font-size="{font_size}" font-weight="{weight}" text-anchor="middle" '
        f'fill="{text_fill}">{text}</text>',
    ]


def eyebrow(x: float, y: float, text: str, fill: str = MUTED) -> str:
    """Return a small uppercase section label, as used across the diagrams."""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="11" font-weight="700" '
        f'fill="{fill}" letter-spacing="1">{text}</text>'
    )


def style_plot() -> None:
    """Apply the book's typographic style to matplotlib's global state."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 9,
            "text.color": INK,
            "axes.edgecolor": RULE_STRONG,
            "axes.labelcolor": INK_SOFT,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "grid.color": RULE,
            "grid.linewidth": 0.8,
            "legend.frameon": False,
            "legend.fontsize": 8,
            "svg.fonttype": "none",  # Keep text as text so it inherits page fonts.
        }
    )


def save_plot(fig: plt.Figure, name: str) -> Path:
    """Save a matplotlib figure as a transparent SVG and close it."""
    assert name.endswith(".svg"), f"Figure name must end in .svg, got '{name}'."
    path = OUTPUT_DIR / name
    fig.savefig(path, format="svg", transparent=True, bbox_inches="tight")
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Chapter figures. Static SVG/matplotlib figures live here; interactive figures
# are separate (see assets/widgets.js). Add each new fig_*() to the FIGURES
# tuple at the bottom.
# ---------------------------------------------------------------------------

# A fixed scatter pattern (unit offsets), reused across the dartboard panels so
# the only thing that changes is the cluster's center (bias) and spread
# (variance). Hard-coded rather than random so the build is reproducible.
_DART_PATTERN = (
    (-0.62, -0.30),
    (0.40, -0.68),
    (0.78, 0.22),
    (-0.20, 0.60),
    (0.12, -0.08),
    (-0.80, 0.42),
    (0.52, 0.66),
    (-0.42, -0.58),
)


def fig_dartboard() -> Path:
    """Diagram: a 2x2 grid of dartboards for the bias-variance failure modes."""
    width, height = 700, 720
    body = [eyebrow(28, 40, "THE TWO WAYS TO BE WRONG")]

    # Columns are bias (left low, right high); rows are variance (top low,
    # bottom high). Each panel scatters _DART_PATTERN around its own center.
    col_x = (190, 510)
    row_y = (230, 560)
    bias = ((6, -4), (70, -46))  # Cluster-center offset per column.
    spread = (16, 46)  # Pixel spread per row.
    labels = (
        ("low bias · low variance", "high bias · low variance"),
        ("low bias · high variance", "high bias · high variance"),
    )
    rings = ((96, "#ffffff"), (64, ACCENT_SOFT), (32, "#ffffff"))

    for r, cy in enumerate(row_y):
        for c, cx in enumerate(col_x):
            for radius, fill in rings:
                body.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" '
                    f'stroke="{RULE_STRONG}" stroke-width="1.2"/>'
                )
            body.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{AMBER}"/>')
            bx, by = bias[c]
            for px, py in _DART_PATTERN:
                dx = cx + bx + px * spread[r]
                dy = cy + by + py * spread[r]
                body.append(
                    f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4.5" fill="{ACCENT}" '
                    f'opacity="0.85"/>'
                )
            body.append(
                f'<text x="{cx}" y="{cy + 126}" font-size="13" font-weight="600" '
                f'text-anchor="middle" fill="{INK_SOFT}">{labels[r][c]}</text>'
            )

    return write_svg(
        "dartboard.svg",
        svg_doc(
            width,
            height,
            "Four dartboards: bias moves the cluster off the bullseye, variance "
            "spreads it out.",
            body,
        ),
    )


def fig_cdf_pdf() -> Path:
    """Plot: one continuous distribution seen as its density (top) and CDF (bottom)."""
    import numpy as np

    style_plot()
    x = np.linspace(0.0, 1.0, 400)
    pdf = 6.0 * x * (1.0 - x)  # Beta(2, 2) density; peaks at 1.5, above height 1.
    cdf = 3.0 * x**2 - 2.0 * x**3  # Its cumulative distribution function.
    x0 = 0.4
    f0 = 3.0 * x0**2 - 2.0 * x0**3  # Equals the shaded area to the left of x0.

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(5.4, 5.4), sharex=True, gridspec_kw={"hspace": 0.34}
    )

    # Top: the density, with the area up to x0 shaded and the peak marked above 1.
    ax_top.plot(x, pdf, color=ACCENT, linewidth=2.2)
    mask = x <= x0
    ax_top.fill_between(x[mask], 0, pdf[mask], color=ACCENT_SOFT)
    ax_top.axhline(1.0, color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
    ax_top.text(0.02, 1.05, "height = 1", color=MUTED, fontsize=7.5, va="bottom")
    ax_top.plot([0.5], [1.5], marker="o", color=AMBER, markersize=6, zorder=5)
    ax_top.annotate(
        "peak 1.5 > 1", xy=(0.5, 1.5), xytext=(0.6, 1.34), color=AMBER, fontsize=7.5
    )
    ax_top.text(
        x0 / 2,
        0.30,
        "area\n≈ 0.35",
        ha="center",
        va="center",
        color=INK_SOFT,
        fontsize=8,
    )
    ax_top.set_ylim(0, 1.7)
    ax_top.set_ylabel("density  f(x)")
    ax_top.set_title("The density lays probability down", loc="left")

    # Bottom: the CDF, with a dot whose height equals the shaded area above.
    ax_bot.plot(x, cdf, color=ACCENT, linewidth=2.2)
    ax_bot.plot([x0, x0], [0, f0], color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
    ax_bot.plot([0, x0], [f0, f0], color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
    ax_bot.plot([x0], [f0], marker="o", color=AMBER, markersize=6, zorder=5)
    ax_bot.annotate(
        "F(x₀) ≈ 0.35",
        xy=(x0, f0),
        xytext=(x0 + 0.05, f0 - 0.15),
        color=INK_SOFT,
        fontsize=8,
    )
    ax_bot.set_ylim(0, 1.05)
    ax_bot.set_ylabel("CDF  F(x)")
    ax_bot.set_xlabel("x")
    ax_bot.set_title("The CDF accumulates it", loc="left")
    ax_bot.set_xticks([0, x0, 1])
    ax_bot.set_xticklabels(["0", "x₀", "1"])

    return save_plot(fig, "cdf-pdf.svg")


def fig_joint_marginals() -> Path:
    """Plot: a correlated joint density with its two marginal densities as shadows."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    style_plot()
    rho = 0.6  # Positive correlation, so the joint tilts lower-left to upper-right.
    lim = 3.0
    grid = np.linspace(-lim, lim, 200)
    xx, yy = np.meshgrid(grid, grid)
    det = 1.0 - rho**2
    quad = (xx**2 - 2 * rho * xx * yy + yy**2) / det
    joint = np.exp(-quad / 2.0) / (2.0 * np.pi * np.sqrt(det))
    marg = np.exp(-(grid**2) / 2.0) / np.sqrt(2.0 * np.pi)  # Standard-normal marginals.

    cmap = LinearSegmentedColormap.from_list("paper_accent", [PAPER, ACCENT])

    fig = plt.figure(figsize=(5.4, 5.4))
    gs = fig.add_gridspec(
        2, 2, width_ratios=(4, 1), height_ratios=(1, 4), wspace=0.06, hspace=0.06
    )
    ax_joint = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_joint)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_joint)

    ax_joint.imshow(
        joint, extent=(-lim, lim, -lim, lim), origin="lower", cmap=cmap, aspect="auto"
    )
    ax_joint.contour(xx, yy, joint, levels=5, colors=ACCENT, linewidths=0.5, alpha=0.35)
    ax_joint.set_xlabel("X")
    ax_joint.set_ylabel("Y")
    ax_joint.set_xticks([-2, 0, 2])
    ax_joint.set_yticks([-2, 0, 2])

    # Top marginal: density of X, projected onto the horizontal axis.
    ax_top.fill_between(grid, 0, marg, color=ACCENT_SOFT)
    ax_top.plot(grid, marg, color=ACCENT, linewidth=1.8)
    ax_top.set_ylim(0, marg.max() * 1.3)
    ax_top.axis("off")
    ax_top.text(
        -lim, marg.max() * 1.12, "marginal of X", color=MUTED, fontsize=8, va="top"
    )

    # Right marginal: density of Y, drawn sideways onto the vertical axis.
    ax_right.fill_betweenx(grid, 0, marg, color=ACCENT_SOFT)
    ax_right.plot(marg, grid, color=ACCENT, linewidth=1.8)
    ax_right.set_xlim(0, marg.max() * 1.3)
    ax_right.axis("off")
    ax_right.text(
        marg.max() * 1.12,
        -lim,
        "marginal\nof Y",
        color=MUTED,
        fontsize=8,
        ha="right",
        va="bottom",
    )

    return save_plot(fig, "joint-marginals.svg")


def fig_convergence_modes() -> Path:
    """Diagram: three nested boxes showing which mode of convergence implies which."""
    width, height = 700, 360
    inner_fill = "#d3e0ee"  # A shade deeper than ACCENT_SOFT for the innermost ring.
    body = [
        eyebrow(40, 42, "WHICH IMPLIES WHICH"),
        arrow_marker(ACCENT, "arrowmodes"),
    ]

    # Nested rectangles: strongest mode innermost, weakest outermost. Each label
    # sits in the top strip of its own ring so no two labels overlap.
    body += [
        f'<rect x="40" y="66" width="620" height="230" rx="10" fill="#ffffff" '
        f'stroke="{RULE_STRONG}" stroke-width="1.4"/>',
        f'<text x="350" y="94" font-size="14" font-weight="700" text-anchor="middle" '
        f'fill="{ACCENT}">Convergence in distribution</text>',
        f'<text x="350" y="112" font-size="11" text-anchor="middle" '
        f'fill="{MUTED}">weakest</text>',
    ]
    body += [
        f'<rect x="118" y="126" width="464" height="146" rx="9" fill="{ACCENT_SOFT}" '
        f'stroke="{RULE_STRONG}" stroke-width="1.2"/>',
        f'<text x="350" y="152" font-size="14" font-weight="700" text-anchor="middle" '
        f'fill="{ACCENT}">Convergence in probability</text>',
    ]
    body += [
        f'<rect x="205" y="170" width="290" height="82" rx="8" fill="{inner_fill}" '
        f'stroke="{RULE_STRONG}" stroke-width="1.2"/>',
        f'<text x="350" y="206" font-size="14" font-weight="700" text-anchor="middle" '
        f'fill="{ACCENT}">Almost sure</text>',
        f'<text x="350" y="226" font-size="11" text-anchor="middle" '
        f'fill="{MUTED}">strongest</text>',
    ]

    # A single arrow running outward: each inner mode implies every outer one.
    body += [
        f'<line x1="230" y1="326" x2="628" y2="326" stroke="{INK_SOFT}" '
        f'stroke-width="1.6" marker-end="url(#arrowmodes)"/>',
        f'<text x="424" y="318" font-size="12" font-style="italic" '
        f'text-anchor="middle" fill="{INK_SOFT}">each inner mode implies the outer</text>',
    ]

    return write_svg(
        "convergence-modes.svg",
        svg_doc(
            width,
            height,
            "Three nested boxes: almost sure convergence inside convergence in "
            "probability inside convergence in distribution.",
            body,
        ),
    )


def fig_lln_settling() -> Path:
    """Plot: running sample means of skewed draws funneling onto the true mean."""
    import numpy as np

    style_plot()
    rng = np.random.default_rng(7)
    n_max = 2000
    mu = 1.0  # Exponential(1) has mean 1 and standard deviation 1.
    sigma = 1.0
    ns = np.arange(1, n_max + 1)

    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    band = 2.0 * sigma / np.sqrt(ns)
    ax.fill_between(ns, mu - band, mu + band, color=ACCENT_SOFT, label="μ ± 2σ/√n")
    for color in (ACCENT, VIOLET, BRICK):
        draws = rng.exponential(scale=1.0, size=n_max)
        running = np.cumsum(draws) / ns
        ax.plot(ns, running, color=color, linewidth=1.0, alpha=0.9)
    ax.axhline(mu, color=INK_SOFT, linestyle="--", linewidth=1.2, label="true mean μ")

    ax.set_xscale("log")
    ax.set_xlim(1, n_max)
    ax.set_ylim(0, 2.3)
    ax.set_xlabel("number of observations  n")
    ax.set_ylabel("running sample mean")
    ax.legend(loc="upper right")
    return save_plot(fig, "lln-settling.svg")


def fig_center_of_mass() -> Path:
    """Diagram: a distribution's mass on a rod, balanced on a fulcrum at the mean."""
    width, height = 680, 380

    vals = [1, 2, 3, 4, 5, 7, 10]
    probs = [0.05, 0.20, 0.28, 0.20, 0.12, 0.10, 0.05]
    assert abs(sum(probs) - 1.0) < 1e-9, "Bar probabilities must sum to one."

    mean = sum(v * p for v, p in zip(vals, probs))
    # Median is the value where the cumulative mass first reaches one half.
    cum = 0.0
    median = vals[-1]
    for v, p in zip(vals, probs):
        cum += p
        if cum >= 0.5:
            median = v
            break

    x0, x1, vmax = 110.0, 590.0, 11.0
    sx = (x1 - x0) / vmax

    def xof(v: float) -> float:
        return x0 + v * sx

    y0 = 292.0  # Baseline: the top of the rod.
    hscale = 158.0 / max(probs)
    bar_w = 24.0

    body = [eyebrow(30, 42, "EXPECTATION IS THE BALANCE POINT")]
    body.append(
        f'<line x1="95" y1="{y0}" x2="605" y2="{y0}" stroke="{RULE_STRONG}" '
        f'stroke-width="3" stroke-linecap="round"/>'
    )
    for v in vals:
        xv = xof(v)
        body.append(
            f'<text x="{xv:.1f}" y="{y0 + 22:.1f}" font-size="11" '
            f'text-anchor="middle" fill="{MUTED}">{v}</text>'
        )
    for v, p in zip(vals, probs):
        xv = xof(v)
        h = p * hscale
        body.append(
            f'<rect x="{xv - bar_w / 2:.1f}" y="{y0 - h:.1f}" width="{bar_w:.1f}" '
            f'height="{h:.1f}" rx="3" fill="{ACCENT}" opacity="0.85"/>'
        )
        body.append(
            f'<text x="{xv:.1f}" y="{y0 - h - 8:.1f}" font-size="9.5" '
            f'text-anchor="middle" fill="{MUTED}">{p:.2f}</text>'
        )

    xmed = xof(median)
    body.append(
        f'<line x1="{xmed:.1f}" y1="{y0 - 6:.1f}" x2="{xmed:.1f}" y2="60" '
        f'stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="2 3"/>'
    )
    body.append(
        f'<text x="{xmed:.1f}" y="54" font-size="11" text-anchor="middle" '
        f'fill="{MUTED}">median</text>'
    )

    xmean = xof(mean)
    body.append(
        f'<line x1="{xmean:.1f}" y1="{y0:.1f}" x2="{xmean:.1f}" y2="82" '
        f'stroke="{AMBER}" stroke-width="1.8" stroke-dasharray="5 4"/>'
    )
    body.append(
        f'<polygon points="{xmean:.1f},{y0 + 2:.1f} {xmean - 15:.1f},{y0 + 30:.1f} '
        f'{xmean + 15:.1f},{y0 + 30:.1f}" fill="{AMBER}"/>'
    )
    body.append(
        f'<text x="{xmean:.1f}" y="76" font-size="12" font-weight="700" '
        f'text-anchor="middle" fill="{AMBER}">mean = {mean:.2f}</text>'
    )

    body.append(arrow_marker(INK_SOFT, "cmArrow"))
    body.append(
        f'<line x1="{xof(6.3):.1f}" y1="150" x2="{xof(9.4):.1f}" y2="150" '
        f'stroke="{INK_SOFT}" stroke-width="1.3" marker-end="url(#cmArrow)"/>'
    )
    body.append(
        f'<text x="{xof(7.9):.1f}" y="140" font-size="10.5" text-anchor="middle" '
        f'fill="{INK_SOFT}">long tail, heavy leverage</text>'
    )

    return write_svg(
        "center-of-mass.svg",
        svg_doc(
            width,
            height,
            "A distribution's mass drawn as bars on a rod, balanced on a fulcrum "
            "at the mean, which the long right tail pulls past the median.",
            body,
        ),
    )


def _normal_pdf(x, mu, sd):
    """Standard normal density, vectorized over a numpy array x."""
    import math

    return np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def _gamma_pdf(x, k, theta):
    """Gamma density with shape k and scale theta, zero for x <= 0."""
    import math

    out = np.zeros_like(x)
    pos = x > 0
    xp = x[pos]
    out[pos] = xp ** (k - 1) * np.exp(-xp / theta) / (theta**k * math.gamma(k))
    return out


def _t_pdf(x, df):
    """Student-t density with df degrees of freedom."""
    import math

    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    return c * (1 + x**2 / df) ** (-(df + 1) / 2)


def fig_moment_shapes() -> Path:
    """Plot: three distributions sharing a mean but differing in a higher moment."""
    import math

    style_plot()
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.5))

    # Variance: same mean, different spread.
    ax = axes[0]
    x = np.linspace(-6, 6, 400)
    ax.plot(x, _normal_pdf(x, 0, 1.0), color=ACCENT, lw=2, label="narrow")
    ax.plot(x, _normal_pdf(x, 0, 2.0), color=AMBER, lw=2, label="wide")
    ax.set_title("variance (spread)")

    # Skewness: same mean and variance, different lean.
    ax = axes[1]
    k, theta = 2.5, 1.0
    mean_g = k * theta
    sd_g = math.sqrt(k) * theta
    x = np.linspace(-3, 9, 500)
    ax.plot(x, _normal_pdf(x, mean_g, sd_g), color=ACCENT, lw=2, label="symmetric")
    ax.plot(x, _gamma_pdf(x, k, theta), color=AMBER, lw=2, label="right-skewed")
    ax.axvline(mean_g, color=MUTED, lw=1, ls=(0, (2, 3)))
    ax.set_title("skewness (lean)")

    # Kurtosis: same mean and variance, different tail weight.
    ax = axes[2]
    x = np.linspace(-5, 5, 500)
    ax.plot(x, _normal_pdf(x, 0, 1.0), color=ACCENT, lw=2, label="light tails")
    df = 3.0
    s = math.sqrt(df)  # Scale a t(3) to unit variance.
    ax.plot(x, s * _t_pdf(s * x, df), color=AMBER, lw=2, label="heavy tails")
    ax.set_title("kurtosis (tails)")

    for ax in axes:
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_ylim(bottom=0)
        ax.legend(loc="upper right", handlelength=1.0, borderaxespad=0.2)
        ax.tick_params(length=0)

    fig.tight_layout(pad=0.6)
    return save_plot(fig, "moment-shapes.svg")


def fig_mgf_convolution() -> Path:
    """Diagram: MGFs turn the convolution of a sum into a plain product."""
    width, height = 720, 380
    body = [arrow_marker(INK_SOFT, "mgfArrow")]

    bw, bh = 118.0, 50.0
    cols = (48.0, 250.0)  # Left edges of the X and Y boxes.
    res_x, res_w = 508.0, 168.0
    top_y, bot_y = 96.0, 250.0

    body.append(eyebrow(30, 46, "TWO LANES TO THE SAME LAW"))
    body.append(eyebrow(30, top_y - 18, "DENSITIES", ACCENT))
    body.append(eyebrow(30, bot_y - 18, "MGFs", AMBER))

    def op_symbol(x, y, sym, word):
        return [
            f'<text x="{x:.1f}" y="{y + 6:.1f}" font-size="26" text-anchor="middle" '
            f'font-weight="600" fill="{INK_SOFT}">{sym}</text>',
            f'<text x="{x:.1f}" y="{y + 26:.1f}" font-size="9.5" '
            f'text-anchor="middle" fill="{MUTED}">{word}</text>',
        ]

    def lane(y, labels, sym, word, tag, tag_fill):
        parts = []
        parts += node_box(cols[0], y, bw, bh, labels[0], font_size=12)
        parts += node_box(cols[1], y, bw, bh, labels[1], font_size=12)
        parts += op_symbol((cols[0] + bw + cols[1]) / 2, y + bh / 2, sym, word)
        parts.append(
            f'<line x1="{cols[1] + bw + 6:.1f}" y1="{y + bh / 2:.1f}" '
            f'x2="{res_x - 8:.1f}" y2="{y + bh / 2:.1f}" stroke="{INK_SOFT}" '
            f'stroke-width="1.4" marker-end="url(#mgfArrow)"/>'
        )
        parts.append(
            f'<text x="{(cols[1] + bw + res_x) / 2:.1f}" y="{y + bh / 2 - 8:.1f}" '
            f'font-size="9.5" text-anchor="middle" fill="{tag_fill}" '
            f'font-weight="600">{tag}</text>'
        )
        parts += node_box(
            res_x, y, res_w, bh, labels[2], font_size=12, fill=ACCENT_SOFT
        )
        return parts

    body += lane(
        top_y,
        ("law of X", "law of Y", "law of X + Y"),
        "&#8859;",  # Convolution (circled asterisk).
        "convolve",
        "needs an integral",
        BRICK,
    )
    body += lane(
        bot_y,
        ("MGF of X", "MGF of Y", "MGF of X + Y"),
        "&#215;",  # Multiplication sign.
        "multiply",
        "just a product",
        ACCENT,
    )

    for cx in (cols[0] + bw / 2, cols[1] + bw / 2, res_x + res_w / 2):
        body.append(
            f'<line x1="{cx:.1f}" y1="{top_y + bh + 4:.1f}" x2="{cx:.1f}" '
            f'y2="{bot_y - 4:.1f}" stroke="{MUTED}" stroke-width="1.1" '
            f'stroke-dasharray="3 3"/>'
        )
    body.append(
        f'<text x="{res_x + res_w / 2:.1f}" y="{(top_y + bh + bot_y) / 2 + 4:.1f}" '
        f'font-size="9.5" text-anchor="middle" fill="{MUTED}">same law</text>'
    )

    return write_svg(
        "mgf-convolution.svg",
        svg_doc(
            width,
            height,
            "Two lanes: convolving densities of X and Y to get the law of X + Y is "
            "hard, while multiplying their MGFs is easy; both reach the same law.",
            body,
        ),
    )


def fig_two_moves() -> Path:
    """Diagram: the forward inference chain plus the backward evaluation arc."""
    width, height = 760, 300
    body = [
        arrow_marker(ACCENT, "twm_fwd"),
        arrow_marker(AMBER, "twm_back"),
        eyebrow(28, 40, "TWO MOVES, ONE SUBJECT"),
    ]
    boxes = (
        (30, "Truth", "unknown parameter"),
        (218, "Data", "one sample"),
        (406, "Procedure", "your rule"),
        (594, "Estimate", "your guess"),
    )
    bw, bh, by = 120, 54, 86
    cy = by + bh / 2
    for bx, title, sub in boxes:
        body += node_box(bx, by, bw, bh, title, font_size=15, weight=600)
        body.append(
            f'<text x="{bx + bw / 2:.1f}" y="{by + bh + 20:.1f}" font-size="11.5" '
            f'text-anchor="middle" fill="{MUTED}">{sub}</text>'
        )
    arrow_labels = ("sample", "compute", "read off")
    for i in range(3):
        x0 = boxes[i][0] + bw
        x1 = boxes[i + 1][0]
        body.append(
            f'<line x1="{x0 + 4:.1f}" y1="{cy:.1f}" x2="{x1 - 4:.1f}" y2="{cy:.1f}" '
            f'stroke="{ACCENT}" stroke-width="2" marker-end="url(#twm_fwd)"/>'
        )
        body.append(
            f'<text x="{(x0 + x1) / 2:.1f}" y="{cy - 10:.1f}" font-size="10.5" '
            f'text-anchor="middle" fill="{INK_SOFT}">{arrow_labels[i]}</text>'
        )
    # Backward evaluation arc: from Estimate box down and back into Truth box.
    x_est = boxes[3][0] + bw / 2
    x_tru = boxes[0][0] + bw / 2
    y_bot = by + bh
    body.append(
        f'<path d="M {x_est:.1f} {y_bot:.1f} C {x_est:.1f} 252, {x_tru:.1f} 252, '
        f'{x_tru:.1f} {y_bot + 2:.1f}" fill="none" stroke="{AMBER}" '
        f'stroke-width="2" stroke-dasharray="6 5" marker-end="url(#twm_back)"/>'
    )
    body.append(
        f'<text x="{(x_est + x_tru) / 2:.1f}" y="264" font-size="12" '
        f'text-anchor="middle" fill="{AMBER}" font-weight="600">'
        f"risk: average error over every dataset the truth could produce</text>"
    )
    return write_svg(
        "two-moves.svg",
        svg_doc(
            width,
            height,
            "A forward chain from truth to data to procedure to estimate, with a "
            "dashed arc labeled risk looping the evaluation back to the truth.",
            body,
        ),
    )


def fig_field_map() -> Path:
    """Diagram: the six parts of the book as one vertical chain of links."""
    width, height = 700, 540
    body = [
        arrow_marker(ACCENT, "fm_arrow"),
        eyebrow(30, 36, "THE MAP OF THE FIELD"),
    ]
    rows = (
        ("I", "Distributions", "the language of randomness"),
        ("II", "Estimation", "guessing an unknown from data"),
        ("III", "Loss &amp; risk", "scoring a procedure before you see data"),
        ("IV", "Regularization", "trading a little bias for less variance"),
        ("V", "Testing", "deciding between explanations under doubt"),
        ("VI", "Asymptotics", "the promises that hold as data grows"),
    )
    bx, bw, bh = 74, 556, 52
    step = 78
    y0 = 60
    for i, (num, title, role) in enumerate(rows):
        top = y0 + i * step
        mid = top + bh / 2
        body.append(
            f'<circle cx="42" cy="{mid:.1f}" r="16" fill="{ACCENT_SOFT}" '
            f'stroke="{ACCENT}" stroke-width="1.3"/>'
        )
        body.append(
            f'<text x="42" y="{mid + 4:.1f}" font-size="12" font-weight="700" '
            f'text-anchor="middle" fill="{ACCENT}">{num}</text>'
        )
        body.append(
            f'<rect x="{bx}" y="{top:.1f}" width="{bw}" height="{bh}" rx="8" '
            f'fill="#ffffff" stroke="{RULE_STRONG}"/>'
        )
        body.append(
            f'<line x1="242" y1="{top + 12:.1f}" x2="242" y2="{top + bh - 12:.1f}" '
            f'stroke="{RULE}" stroke-width="1"/>'
        )
        body.append(
            f'<text x="94" y="{mid + 5:.1f}" font-size="14" font-weight="700" '
            f'fill="{ACCENT}">{title}</text>'
        )
        body.append(
            f'<text x="258" y="{mid + 5:.1f}" font-size="12.5" fill="{INK_SOFT}">'
            f"{role}</text>"
        )
        if i < len(rows) - 1:
            body.append(
                f'<line x1="{bx + bw / 2:.1f}" y1="{top + bh + 3:.1f}" '
                f'x2="{bx + bw / 2:.1f}" y2="{top + step - 3:.1f}" '
                f'stroke="{ACCENT}" stroke-width="1.8" marker-end="url(#fm_arrow)"/>'
            )
    return write_svg(
        "field-map.svg",
        svg_doc(
            width,
            height,
            "Six labeled rows, numbered I to VI, connected top to bottom by arrows: "
            "distributions, estimation, loss and risk, regularization, testing, "
            "asymptotics.",
            body,
        ),
    )


def fig_one_question() -> Path:
    """Diagram: one risk question on the left fanning out to named methods."""
    width, height = 760, 380
    body = [
        arrow_marker(MUTED, "oq_arrow"),
        eyebrow(28, 36, "ONE QUESTION, MANY METHODS"),
    ]
    hx, hy, hw, hh = 40, 148, 252, 96
    body.append(
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="10" '
        f'fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-width="1.4"/>'
    )
    hub_cx = hx + hw / 2
    body.append(
        f'<text x="{hub_cx:.1f}" y="{hy + 30:.1f}" font-size="13.5" '
        f'font-weight="700" text-anchor="middle" fill="{ACCENT}">One question</text>'
    )
    for j, line in enumerate(
        (
            "which procedure has the",
            "least risk under a given",
            "model and a given loss?",
        )
    ):
        body.append(
            f'<text x="{hub_cx:.1f}" y="{hy + 50 + j * 17:.1f}" font-size="11.5" '
            f'text-anchor="middle" fill="{INK}">{line}</text>'
        )
    chips = (
        "maximum likelihood",
        "ridge &amp; lasso",
        "the t-test",
        "confidence intervals",
        "the bootstrap",
        "Bayesian posteriors",
    )
    cx0, cw, ch = 516, 214, 40
    y0, gap = 28, 55
    origin_x, origin_y = hx + hw, hy + hh / 2
    for k in range(len(chips)):
        top = y0 + k * gap
        mid = top + ch / 2
        body.append(
            f'<line x1="{origin_x + 3:.1f}" y1="{origin_y:.1f}" '
            f'x2="{cx0 - 4:.1f}" y2="{mid:.1f}" stroke="{MUTED}" '
            f'stroke-width="1.3" marker-end="url(#oq_arrow)"/>'
        )
    # Draw chips after the lines so the boxes sit on top of the arrow tails.
    for k, label in enumerate(chips):
        top = y0 + k * gap
        body += node_box(cx0, top, cw, ch, label, font_size=12.5)
    return write_svg(
        "one-question.svg",
        svg_doc(
            width,
            height,
            "A single box on the left, one question about least risk under a model "
            "and loss, with arrows fanning to six named methods on the right.",
            body,
        ),
    )


def _chip(cx: float, top: float, w: float, h: float, name: str, sub: str) -> list[str]:
    """A two-line labelled chip: a distribution name over its sufficient statistic."""
    x = cx - w / 2
    return [
        f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" '
        f'fill="#ffffff" stroke="{RULE_STRONG}"/>',
        f'<text x="{cx:.1f}" y="{top + 23:.1f}" font-size="14" font-weight="700" '
        f'text-anchor="middle" fill="{INK}">{name}</text>',
        f'<text x="{cx:.1f}" y="{top + 42:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{MUTED}">{sub}</text>',
    ]


def fig_exponential_family_umbrella() -> Path:
    """Diagram: named distributions gathered under the exponential-family form."""
    width, height = 780, 470
    bus_y = 155
    centers = (150, 390, 630)
    row1_top, row2_top = 185, 265
    chip_w, chip_h = 210, 56

    body = [eyebrow(30, 40, "ONE FORM, MANY FACES")]

    # The header box carrying the exponential-family form.
    body += [
        f'<rect x="110" y="60" width="560" height="52" rx="10" '
        f'fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-width="1.3"/>',
        f'<text x="390" y="92" font-size="16" text-anchor="middle" fill="{INK}">'
        f"p(x&#160;|&#160;θ) = h(x)&#160;exp( η(θ)&#183;T(x) − A(θ) )</text>",
    ]

    # Ribs of the umbrella: spine from the header to a bus, then down to each chip.
    body.append(
        f'<line x1="390" y1="112" x2="390" y2="{bus_y}" '
        f'stroke="{RULE_STRONG}" stroke-width="1.4"/>'
    )
    body.append(
        f'<line x1="{centers[0]}" y1="{bus_y}" x2="{centers[2]}" y2="{bus_y}" '
        f'stroke="{RULE_STRONG}" stroke-width="1.4"/>'
    )
    for cx in centers:
        body.append(
            f'<line x1="{cx}" y1="{bus_y}" x2="{cx}" y2="{row1_top}" '
            f'stroke="{RULE_STRONG}" stroke-width="1.4"/>'
        )
        body.append(
            f'<line x1="{cx}" y1="{row1_top + chip_h}" x2="{cx}" y2="{row2_top}" '
            f'stroke="{RULE_STRONG}" stroke-width="1.4"/>'
        )

    row1 = (
        ("Bernoulli", "T(x) = x"),
        ("Poisson", "T(x) = x"),
        ("Exponential", "T(x) = x"),
    )
    row2 = (
        ("Normal", "T(x) = (x, x²)"),
        ("Gamma", "T(x) = (x, ln x)"),
        ("Beta", "T(x) = (ln x, ln(1−x))"),
    )
    for cx, (name, sub) in zip(centers, row1):
        body += _chip(cx, row1_top, chip_w, chip_h, name, sub)
    for cx, (name, sub) in zip(centers, row2):
        body += _chip(cx, row2_top, chip_w, chip_h, name, sub)

    # The outsiders: a dashed strip beneath, kept clearly out of the umbrella.
    body += [
        f'<rect x="110" y="360" width="560" height="70" rx="10" fill="none" '
        f'stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="5 4"/>',
        f'<text x="390" y="386" font-size="12.5" font-weight="700" '
        f'text-anchor="middle" fill="{INK_SOFT}" letter-spacing="0.5">'
        f"OUTSIDE THE FAMILY</text>",
        f'<text x="390" y="410" font-size="12.5" text-anchor="middle" '
        f'fill="{MUTED}">Uniform on [0, θ] — support moves&#160;&#160;•'
        f"&#160;&#160;Cauchy — tails too heavy</text>",
    ]

    return write_svg(
        "exponential-family-umbrella.svg",
        svg_doc(
            width,
            height,
            "Named distributions gathered under the exponential-family form, with "
            "the uniform and Cauchy marked as outside it.",
            body,
        ),
    )


def fig_sufficient_statistic() -> Path:
    """Diagram: an iid sample collapsing into a single sufficient statistic."""
    width, height = 720, 360
    body = [
        eyebrow(30, 40, "THE SAMPLE FUNNELS INTO ONE SUMMARY"),
        arrow_marker(RULE_STRONG, "suff-arrow"),
    ]

    chip_w, chip_h = 118, 40
    chip_x = 60
    rows = (
        (74, "x₁"),
        (122, "x₂"),
        (170, "x₃"),
        (218, None),  # Vertical dots for the rest of the sample.
        (262, "xₙ"),
    )
    target = (472, 200)  # Left-center of the T box; every arrow converges here.
    for top, label in rows:
        cy = top + chip_h / 2
        if label is None:
            body.append(
                f'<text x="{chip_x + chip_w / 2:.1f}" y="{cy + 4:.1f}" '
                f'font-size="18" text-anchor="middle" fill="{MUTED}">⋮</text>'
            )
            continue
        body += [
            f'<rect x="{chip_x}" y="{top}" width="{chip_w}" height="{chip_h}" rx="7" '
            f'fill="#ffffff" stroke="{RULE_STRONG}"/>',
            f'<text x="{chip_x + chip_w / 2:.1f}" y="{cy + 5:.1f}" font-size="15" '
            f'text-anchor="middle" fill="{INK}">{label}</text>',
        ]
        body.append(
            f'<path d="M {chip_x + chip_w + 6:.1f} {cy:.1f} '
            f"C {chip_x + chip_w + 90:.1f} {cy:.1f} "
            f"{target[0] - 90:.1f} {target[1]:.1f} "
            f'{target[0] - 4:.1f} {target[1]:.1f}" fill="none" '
            f'stroke="{RULE_STRONG}" stroke-width="1.4" marker-end="url(#suff-arrow)"/>'
        )

    # The single sufficient-statistic box the whole sample lands in.
    bx, by, bw, bh = 472, 150, 210, 100
    body += [
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
        f'fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-width="1.4"/>',
        f'<text x="{bx + bw / 2:.1f}" y="{by + 34:.1f}" font-size="16" '
        f'font-weight="700" text-anchor="middle" fill="{INK}">T = Σᵢ T(xᵢ)</text>',
        f'<text x="{bx + bw / 2:.1f}" y="{by + 58:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">carries all of θ’s information</text>',
        f'<text x="{bx + bw / 2:.1f}" y="{by + 78:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{MUTED}">its size never grows with n</text>',
    ]

    return write_svg(
        "sufficient-statistic.svg",
        svg_doc(
            width,
            height,
            "An independent sample x-one through x-n collapsing into a single "
            "sufficient statistic, the sum of T over the sample.",
            body,
        ),
    )


def fig_outside_the_family() -> Path:
    """Plot: the two classic non-exponential families, the uniform and the Cauchy."""
    style_plot()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.3))

    # Left: uniform on [0, theta], with its support edge sliding as theta grows.
    for theta, color in ((1.0, ACCENT), (1.6, AMBER), (2.6, VIOLET)):
        h = 1.0 / theta
        ax1.plot(
            [0, 0, theta, theta, theta + 0.35],
            [0, h, h, 0, 0],
            color=color,
            linewidth=2.0,
        )
        ax1.fill_between([0, theta], [h, h], color=color, alpha=0.10)
        ax1.text(theta, h + 0.05, f"θ={theta:g}", color=color, fontsize=8, ha="center")
    ax1.set_title("Uniform on [0, θ]: support moves")
    ax1.set_xlabel("x")
    ax1.set_ylabel("density")
    ax1.set_xlim(-0.15, 3.1)
    ax1.set_ylim(0, 1.28)
    ax1.annotate(
        "edge slides with θ",
        xy=(2.6, 0.06),
        xytext=(1.72, 0.98),
        color=INK_SOFT,
        fontsize=8,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    # Right: Cauchy against Normal, the heavy tails that leave it with no MGF.
    xx = np.linspace(-6, 6, 400)
    normal = np.exp(-(xx**2) / 2) / np.sqrt(2 * np.pi)
    cauchy = 1.0 / (np.pi * (1 + xx**2))
    ax2.plot(xx, normal, color=ACCENT, linewidth=2.0, label="Normal")
    ax2.plot(xx, cauchy, color=VIOLET, linewidth=2.0, label="Cauchy")
    ax2.fill_between(xx, cauchy, color=VIOLET, alpha=0.08)
    ax2.set_title("Cauchy vs Normal: heavy tails")
    ax2.set_xlabel("x")
    ax2.set_ylabel("density")
    ax2.set_xlim(-6, 6)
    ax2.set_ylim(0, 0.44)
    ax2.legend(loc="upper right")
    ax2.annotate(
        "no MGF",
        xy=(3.6, cauchy[np.argmin(np.abs(xx - 3.6))]),
        xytext=(1.9, 0.24),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    fig.tight_layout()
    return save_plot(fig, "outside-the-family.svg")


def fig_mle_asymptotics() -> Path:
    """Plot: the MLE's sampling distribution tightening to a Normal at the truth."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    theta = 1.0  # The true parameter.
    info = 1.0  # Fisher information per observation, I(theta).
    x = np.linspace(-0.4, 2.4, 700)
    for n, color, label in (
        (5, VIOLET, "n = 5"),
        (20, AMBER, "n = 20"),
        (80, ACCENT, "n = 80"),
    ):
        sd = 1.0 / np.sqrt(n * info)  # Cramér–Rao floor width: 1/(n I).
        dens = np.exp(-0.5 * ((x - theta) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
        ax.plot(x, dens, color=color, linewidth=2.0, label=label)
        ax.fill_between(x, dens, color=color, alpha=0.07)
    ax.axvline(theta, color=INK_SOFT, linestyle="--", linewidth=1.2)
    ax.set_ylim(0, 4.4)
    ax.set_xlim(x[0], x[-1])
    ax.text(theta + 0.04, 4.15, "truth θ", color=INK_SOFT, fontsize=8, va="top")
    ax.set_xlabel("maximum-likelihood estimate  θ̂")
    ax.set_ylabel("sampling density")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(length=0)
    ax.annotate(
        "width ∝ 1/√n",
        xy=(theta + 1.0 / np.sqrt(20), 0.9),
        xytext=(theta + 0.55, 2.4),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.legend(loc="upper left")
    fig.tight_layout()
    return save_plot(fig, "mle-asymptotics.svg")


def fig_mle_pitfalls() -> Path:
    """Plot: two failure modes — an irregular boundary peak and a small-sample bias."""
    style_plot()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.3))

    # Left: uniform on [0, theta] likelihood — the peak is a boundary corner.
    m = 1.4  # The sample maximum, max_i x_i.
    n = 6
    theta = np.linspace(0.0, 3.0, 700)
    like = np.where(theta >= m, (m / np.maximum(theta, m)) ** n, 0.0)
    ax1.plot(theta, like, color=ACCENT, linewidth=2.0)
    ax1.fill_between(theta, like, color=ACCENT, alpha=0.08)
    ax1.axvline(m, color=AMBER, linestyle="--", linewidth=1.2)
    ax1.plot([m], [1.0], marker="o", color=AMBER, markersize=6, zorder=5)
    ax1.set_title("Uniform on [0, θ]: peak at the edge")
    ax1.set_xlabel("candidate θ")
    ax1.set_ylabel("likelihood (scaled)")
    ax1.set_xlim(0, 3)
    ax1.set_ylim(0, 1.25)
    ax1.annotate(
        "MLE = max xᵢ,\nslope never zero",
        xy=(m, 1.0),
        xytext=(m + 0.18, 0.62),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    # Right: the MLE of a Normal variance divides by n, so it runs low.
    ns = np.arange(2, 41)
    ratio = (ns - 1) / ns
    ax2.plot(ns, ratio, color=ACCENT, linewidth=2.0, marker="o", markersize=3)
    ax2.axhline(1.0, color=INK_SOFT, linestyle="--", linewidth=1.2)
    ax2.text(40, 1.012, "unbiased target", color=INK_SOFT, fontsize=8, ha="right")
    ax2.set_title("MLE of σ² is biased low")
    ax2.set_xlabel("sample size  n")
    ax2.set_ylabel("E[σ̂²] / σ²  =  (n−1)/n")
    ax2.set_xlim(0, 41)
    ax2.set_ylim(0.3, 1.08)
    ax2.annotate(
        "divides by n, not n−1",
        xy=(6, 5 / 6),
        xytext=(13, 0.58),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    fig.tight_layout()
    return save_plot(fig, "mle-pitfalls.svg")


def fig_estimator_sampling_distributions() -> Path:
    """Plot: two estimators' sampling distributions over the same true value."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.4))

    theta = 0.0  # The true value both rules aim at, marked on the axis.
    x = np.linspace(-4.2, 4.2, 500)

    def normal(mu, sd):
        return np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))

    wide = normal(0.0, 1.5)  # Unbiased but high variance.
    tight_mu = 1.05
    tight = normal(tight_mu, 0.62)  # Biased but low variance.

    ax.axvline(theta, color=INK_SOFT, linestyle="--", linewidth=1.3, zorder=1)
    ax.fill_between(x, 0, wide, color=ACCENT, alpha=0.14)
    ax.plot(x, wide, color=ACCENT, linewidth=2.2, label="unbiased, high variance")
    ax.fill_between(x, 0, tight, color=AMBER, alpha=0.14)
    ax.plot(x, tight, color=AMBER, linewidth=2.2, label="biased, low variance")

    peak = tight.max()
    top = peak * 1.34
    ax.set_ylim(0, top)
    # "true theta" rides the top of the dashed line, to its left to clear the arrow.
    ax.text(
        theta - 0.12,
        top * 0.99,
        "true θ",
        color=INK_SOFT,
        fontsize=9,
        ha="right",
        va="top",
    )
    # Bias arrow: from the truth to the biased rule's center.
    ax.annotate(
        "",
        xy=(tight_mu, peak * 1.04),
        xytext=(theta, peak * 1.04),
        arrowprops=dict(arrowstyle="<->", color=INK_SOFT, lw=1.1),
    )
    ax.text(
        (theta + tight_mu) / 2,
        peak * 1.11,
        "bias",
        color=INK_SOFT,
        fontsize=8,
        ha="center",
        va="bottom",
    )

    ax.set_xlabel("value of the estimate")
    ax.set_ylabel("sampling density")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-4.2, 4.2)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return save_plot(fig, "estimator-sampling-distributions.svg")


def fig_consistency_concentration() -> Path:
    """Plot: an estimator's sampling distribution concentrating as n grows."""
    from matplotlib.colors import LinearSegmentedColormap

    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.4))

    theta = 0.0  # The estimand; every curve concentrates onto it.
    sigma = 3.0  # Population spread; the estimator's SE is sigma / sqrt(n).
    x = np.linspace(-3.0, 3.0, 600)

    cmap = LinearSegmentedColormap.from_list("shrink", ["#b7c6d6", ACCENT])
    ns = (5, 20, 80, 320)
    peak = 0.0
    for i, n in enumerate(ns):
        se = sigma / np.sqrt(n)
        dens = np.exp(-0.5 * ((x - theta) / se) ** 2) / (se * np.sqrt(2 * np.pi))
        peak = max(peak, dens.max())
        ax.plot(x, dens, color=cmap(i / (len(ns) - 1)), linewidth=2.2, label=f"n = {n}")

    top = peak * 1.1
    ax.set_ylim(0, top)
    ax.axvline(theta, color=INK_SOFT, linestyle="--", linewidth=1.3, zorder=1)
    ax.text(
        theta - 0.06,
        top * 0.99,
        "true θ",
        color=INK_SOFT,
        fontsize=9,
        ha="right",
        va="top",
    )

    ax.set_xlabel("value of the estimate")
    ax.set_ylabel("sampling density")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-3.0, 3.0)
    ax.legend(loc="upper right", title="more data")
    fig.tight_layout()
    return save_plot(fig, "consistency-concentration.svg")


def fig_factorization() -> Path:
    """Diagram: the Fisher-Neyman factorization splitting the likelihood in two."""
    width, height = 720, 400
    body = [eyebrow(30, 40, "THE FISHER-NEYMAN FACTORIZATION")]

    # Header: the likelihood, which the split below resolves into two factors.
    hx, hw, hy, hh = 270, 180, 66, 52
    body += [
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="10" '
        f'fill="#ffffff" stroke="{RULE_STRONG}" stroke-width="1.3"/>',
        f'<text x="{hx + hw / 2:.1f}" y="{hy + 25:.1f}" font-size="15" '
        f'font-weight="700" text-anchor="middle" fill="{INK}">likelihood</text>',
        f'<text x="{hx + hw / 2:.1f}" y="{hy + 43:.1f}" font-size="13" '
        f'text-anchor="middle" fill="{MUTED}">p(x | θ)</text>',
    ]
    body.append(
        f'<text x="{hx + hw / 2:.1f}" y="{hy + hh + 26:.1f}" font-size="20" '
        f'text-anchor="middle" fill="{INK_SOFT}">=</text>'
    )

    # The two factor boxes, fed by curved connectors from the "=".
    fy, fh = hy + hh + 44, 96
    lx, lw = 96, 250
    rx, rw = 386, 250
    mid = hx + hw / 2
    for tx in (lx + lw / 2, rx + rw / 2):
        body.append(
            f'<path d="M {mid:.1f} {hy + hh + 34:.1f} '
            f"C {mid:.1f} {fy - 14:.1f} {tx:.1f} {fy - 24:.1f} "
            f'{tx:.1f} {fy - 3:.1f}" fill="none" stroke="{RULE_STRONG}" '
            f'stroke-width="1.3"/>'
        )

    # Left factor: carries theta, sees the data only through T. The piece to keep.
    body += [
        f'<rect x="{lx}" y="{fy}" width="{lw}" height="{fh}" rx="10" '
        f'fill="{ACCENT_SOFT}" stroke="{ACCENT}" stroke-width="1.5"/>',
        f'<text x="{lx + lw / 2:.1f}" y="{fy + 32:.1f}" font-size="17" '
        f'font-weight="700" text-anchor="middle" fill="{INK}">g( T(x), θ )</text>',
        f'<text x="{lx + lw / 2:.1f}" y="{fy + 56:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">θ touches the data</text>',
        f'<text x="{lx + lw / 2:.1f}" y="{fy + 73:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">only through T</text>',
        f'<text x="{lx + lw / 2:.1f}" y="{fy + fh + 22:.1f}" font-size="12" '
        f'font-weight="700" text-anchor="middle" fill="{ACCENT}">keep this</text>',
    ]

    body.append(
        f'<text x="{(lx + lw + rx) / 2:.1f}" y="{fy + fh / 2 + 8:.1f}" '
        f'font-size="22" text-anchor="middle" fill="{MUTED}">&#215;</text>'
    )

    # Right factor: data alone, free of theta. Discardable for inference on theta.
    body += [
        f'<rect x="{rx}" y="{fy}" width="{rw}" height="{fh}" rx="10" '
        f'fill="#ffffff" stroke="{RULE_STRONG}" stroke-width="1.3"/>',
        f'<text x="{rx + rw / 2:.1f}" y="{fy + 32:.1f}" font-size="17" '
        f'font-weight="700" text-anchor="middle" fill="{MUTED}">h( x )</text>',
        f'<text x="{rx + rw / 2:.1f}" y="{fy + 56:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">data alone,</text>',
        f'<text x="{rx + rw / 2:.1f}" y="{fy + 73:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">free of θ</text>',
        f'<text x="{rx + rw / 2:.1f}" y="{fy + fh + 22:.1f}" font-size="12" '
        f'font-weight="700" text-anchor="middle" fill="{MUTED}">discardable</text>',
    ]

    return write_svg(
        "factorization.svg",
        svg_doc(
            width,
            height,
            "The likelihood factors into a theta-bearing piece that sees the data "
            "only through T, times a theta-free piece of the data alone.",
            body,
        ),
    )


def fig_information_curvature() -> Path:
    """Plot: a sharp vs a flat log-likelihood, curvature and bound contrasted."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.9))

    theta0 = 0.5
    theta = np.linspace(0.18, 0.82, 400)
    I_sharp, I_flat = 130.0, 20.0
    ell_sharp = -0.5 * I_sharp * (theta - theta0) ** 2
    ell_flat = -0.5 * I_flat * (theta - theta0) ** 2

    ax.plot(theta, ell_sharp, color=ACCENT, lw=2.4, label="sharp: much information")
    ax.plot(theta, ell_flat, color=AMBER, lw=2.4, label="flat: little information")
    ax.plot([theta0], [0.0], marker="o", color=INK, markersize=7, zorder=6)
    ax.text(
        theta0,
        0.30,
        "same best estimate",
        ha="center",
        va="bottom",
        color=INK_SOFT,
        fontsize=8,
    )

    # Two nested precision intervals the peaks can afford, stacked so the narrow
    # (sharp) and wide (flat) arrows never overlap. Half-width scales as
    # 1/sqrt(I); the constant keeps the wider flat arrow inside the axes.
    d_sharp = 1.25 / np.sqrt(I_sharp)
    d_flat = 1.25 / np.sqrt(I_flat)
    y_loose, y_tight = -1.7, -2.6
    ax.annotate(
        "",
        xy=(theta0 + d_flat, y_loose),
        xytext=(theta0 - d_flat, y_loose),
        arrowprops=dict(arrowstyle="<->", color=AMBER, lw=1.7),
    )
    ax.text(
        theta0,
        y_loose - 0.22,
        "loose bound",
        ha="center",
        va="top",
        color=AMBER,
        fontsize=8.5,
        fontweight="bold",
    )
    ax.annotate(
        "",
        xy=(theta0 + d_sharp, y_tight),
        xytext=(theta0 - d_sharp, y_tight),
        arrowprops=dict(arrowstyle="<->", color=ACCENT, lw=1.7),
    )
    ax.text(
        theta0,
        y_tight - 0.22,
        "tight bound",
        ha="center",
        va="top",
        color=ACCENT,
        fontsize=8.5,
        fontweight="bold",
    )

    ax.annotate(
        "high curvature",
        xy=(theta0 - 0.058, -0.5 * I_sharp * 0.058**2),
        xytext=(0.205, -0.95),
        color=ACCENT,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "low curvature",
        xy=(0.725, -0.5 * I_flat * (0.725 - theta0) ** 2),
        xytext=(0.60, -0.92),
        color=AMBER,
        fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    ax.set_xlabel("parameter  θ")
    ax.set_ylabel("log-likelihood  (peak set to 0)")
    ax.set_xlim(0.18, 0.82)
    ax.set_ylim(-4.0, 0.75)
    ax.set_yticks([0, -1, -2, -3, -4])
    ax.legend(loc="lower center", handlelength=1.4)
    fig.tight_layout()
    return save_plot(fig, "information-curvature.svg")


def fig_prior_likelihood_posterior() -> Path:
    """Plot: a Normal-Normal update as prior times likelihood giving the posterior."""
    import math

    style_plot()
    x = np.linspace(-3.0, 6.0, 600)

    def normal(mu, var):
        return np.exp(-0.5 * (x - mu) ** 2 / var) / math.sqrt(2 * math.pi * var)

    prior_mu, prior_var = 0.0, 1.0
    like_mu, like_var = 3.0, 0.25  # Data mean 3 with precision 4 (n = 4, sigma^2 = 1).
    # Posterior precision adds; the mean is the precision-weighted average.
    post_prec = 1.0 / prior_var + 1.0 / like_var
    post_var = 1.0 / post_prec
    post_mu = post_var * (prior_mu / prior_var + like_mu / like_var)

    prior = normal(prior_mu, prior_var)
    like = normal(like_mu, like_var)
    post = normal(post_mu, post_var)

    fig, axes = plt.subplots(1, 3, figsize=(8.4, 2.9), sharey=True)
    top = max(post.max(), like.max()) * 1.16

    panels = (
        (axes[0], prior, ACCENT, "prior", "belief before data", prior_mu),
        (axes[1], like, AMBER, "likelihood", "what the data says", like_mu),
        (axes[2], post, VIOLET, "posterior", "sharper than both", post_mu),
    )
    for ax, curve, color, title, sub, center in panels:
        ax.fill_between(x, 0, curve, color=color, alpha=0.14)
        ax.plot(x, curve, color=color, lw=2.2)
        ax.plot(
            [center, center],
            [0, float(np.interp(center, x, curve))],
            color=color,
            lw=1.4,
            ls=(0, (4, 3)),
        )
        ax.set_title(title, loc="left", color=color)
        ax.text(0.03, 0.88, sub, transform=ax.transAxes, fontsize=8, color=MUTED)
        ax.set_ylim(0, top)
        ax.set_xlim(-3, 6)
        ax.set_yticks([])
        ax.set_xticks([0, 3])
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("parameter  μ")
        ax.tick_params(length=0)

    # In the posterior panel, mark where the prior and the data each pulled from.
    ax = axes[2]
    for src in (prior_mu, like_mu):
        ax.axvline(src, color=INK_SOFT, lw=1.0, ls=(0, (2, 3)), alpha=0.45)
    ax.annotate(
        "mean 2.4:\nbetween 0 and 3",
        xy=(post_mu - 0.35, top * 0.16),
        xytext=(-2.7, top * 0.52),
        fontsize=8,
        color=INK_SOFT,
        va="center",
        arrowprops=dict(arrowstyle="->", color=INK_SOFT, lw=1.0),
    )

    fig.tight_layout(pad=0.6)
    return save_plot(fig, "prior-likelihood-posterior.svg")


def fig_posterior_summaries() -> Path:
    """Plot: one posterior and the point summaries that each collapse it to a number."""
    import math

    style_plot()
    a, b = 2.0, 6.0  # Beta(2, 6) posterior: skewed, so its mean and mode separate.
    x = np.linspace(0.0, 1.0, 1000)
    log_b = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    with np.errstate(divide="ignore"):
        pdf = np.exp((a - 1) * np.log(x) + (b - 1) * np.log(1 - x) - log_b)
    pdf = np.nan_to_num(pdf)

    mean = a / (a + b)
    mode = (a - 1) / (a + b - 2)
    # Central 95% credible interval read off the numerical CDF.
    cdf = np.cumsum(pdf)
    cdf /= cdf[-1]
    lo = float(x[np.searchsorted(cdf, 0.025)])
    hi = float(x[np.searchsorted(cdf, 0.975)])

    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    band = (x >= lo) & (x <= hi)
    ax.fill_between(x[band], 0, pdf[band], color=ACCENT_SOFT)
    ax.plot(x, pdf, color=ACCENT, lw=2.2)

    peak = float(pdf.max())
    top = peak * 1.30
    h_mode = float(np.interp(mode, x, pdf))
    h_mean = float(np.interp(mean, x, pdf))
    ax.plot([mode, mode], [0, h_mode], color=VIOLET, lw=1.8)
    ax.plot([mean, mean], [0, h_mean], color=AMBER, lw=1.8, ls=(0, (4, 3)))

    ax.annotate(
        "MAP\n(posterior mode)",
        xy=(mode, h_mode),
        xytext=(mode - 0.03, top * 0.82),
        ha="center",
        fontsize=8,
        color=VIOLET,
        arrowprops=dict(arrowstyle="->", color=VIOLET, lw=1.0),
    )
    ax.annotate(
        "posterior mean",
        xy=(mean, h_mean),
        xytext=(mean + 0.22, top * 0.60),
        ha="center",
        fontsize=8,
        color=AMBER,
        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.0),
    )

    # The credible interval as a bracket beneath the density.
    y_br = -peak * 0.11
    tick = peak * 0.03
    ax.plot([lo, hi], [y_br, y_br], color=INK_SOFT, lw=1.4)
    for edge in (lo, hi):
        ax.plot([edge, edge], [y_br - tick, y_br + tick], color=INK_SOFT, lw=1.4)
    ax.text(
        (lo + hi) / 2,
        y_br - peak * 0.055,
        "95% credible interval",
        ha="center",
        va="top",
        fontsize=8,
        color=INK_SOFT,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(-peak * 0.30, top)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("rate  p")
    ax.tick_params(length=0)
    ax.set_title(
        "The posterior is the answer; each summary is a projection of it", loc="left"
    )
    fig.tight_layout(pad=0.6)
    return save_plot(fig, "posterior-summaries.svg")


def fig_risk_curves() -> Path:
    """Plot: risk curves over theta showing dominance and crossing (no total order)."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))

    theta = np.linspace(-2.6, 2.6, 500)
    mle = np.ones_like(theta)  # delta(x) = x: risk = 1 at every theta.
    inflated = 1.69 + 0.09 * theta**2  # delta(x) = 1.3 x: above 1 everywhere.
    shrink = 0.25 + 0.25 * theta**2  # delta(x) = x / 2: dips low, climbs in the tails.

    ax.plot(theta, inflated, color=BRICK, lw=2.2, label="inflated rule  δ(x) = 1.3x")
    ax.plot(theta, mle, color=ACCENT, lw=2.4, label="MLE  δ(x) = x")
    ax.plot(theta, shrink, color=AMBER, lw=2.2, label="shrinkage  δ(x) = x / 2")

    # Shade where the shrinkage rule beats the MLE (between the two crossings).
    below = shrink < mle
    ax.fill_between(theta, shrink, mle, where=below, color=AMBER, alpha=0.12)

    # The crossings, at theta = ±sqrt(3), where shrinkage stops beating the MLE.
    cross = np.sqrt(3.0)
    for xc in (-cross, cross):
        ax.plot([xc], [1.0], marker="o", color=INK, markersize=4, zorder=6)

    ax.annotate(
        "above the MLE everywhere\n→ inadmissible",
        xy=(0.95, 1.69 + 0.09 * 0.95**2),
        xytext=(-1.15, 1.34),
        color=BRICK,
        fontsize=8,
        ha="left",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.text(
        0.0,
        0.56,
        "below the MLE near 0,\nabove it past the crossings",
        color=INK_SOFT,
        fontsize=8,
        ha="center",
        va="center",
    )
    ax.text(-2.55, 1.09, "flat: same risk at every θ", color=ACCENT, fontsize=8)

    ax.set_xlabel("unknown parameter  θ")
    ax.set_ylabel("risk  R(θ, δ)")
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(0, 2.5)
    ax.legend(loc="upper center", handlelength=1.5)
    fig.tight_layout()
    return save_plot(fig, "risk-curves.svg")


def fig_minimax_bayes() -> Path:
    """Plot: a flat minimax risk against a Bayes rule that dips near the prior center."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))

    theta = np.linspace(-3.2, 3.2, 500)
    mle = np.ones_like(theta)  # Minimax here: flat worst-case risk of 1.
    bayes = 0.25 + 0.25 * theta**2  # Bayes rule for a N(0, 1) prior: delta = x / 2.

    # The prior, drawn low on the same axis to show where the Bayes rule spends
    # its advantage — it dips lowest exactly where the prior places its mass.
    prior = np.exp(-0.5 * theta**2) / np.sqrt(2 * np.pi)
    ax.fill_between(theta, 0, prior, color=ACCENT_SOFT, zorder=0)
    ax.plot(theta, prior, color=MUTED, lw=1.0, alpha=0.7)
    ax.text(0.0, 0.42, "prior over θ", color=MUTED, fontsize=8, ha="center")

    ax.axhline(1.0, color=ACCENT, lw=1.2, ls=(0, (5, 3)))
    ax.plot(theta, mle, color=ACCENT, lw=2.4, label="MLE (minimax)")
    ax.plot(theta, bayes, color=VIOLET, lw=2.4, label="Bayes rule (prior at 0)")

    # Mark the crossings where the Bayes rule stops beating the minimax rule.
    cross = np.sqrt(3.0)
    for xc in (-cross, cross):
        ax.plot([xc], [1.0], marker="o", color=INK, markersize=4, zorder=6)

    ax.annotate(
        "minimax worst case = 1\n(flat guarantee)",
        xy=(2.4, 1.0),
        xytext=(1.1, 1.62),
        color=ACCENT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "dips low where the prior bets,\npays for it in the tails",
        xy=(-2.15, 0.25 + 0.25 * 2.15**2),
        xytext=(-3.15, 1.72),
        color=VIOLET,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    ax.set_xlabel("unknown parameter  θ")
    ax.set_ylabel("risk  R(θ, δ)")
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(0, 2.3)
    ax.legend(loc="upper right", handlelength=1.5)
    fig.tight_layout()
    return save_plot(fig, "minimax-bayes.svg")


def fig_loss_shapes() -> Path:
    """Plot: the four loss functions as shapes of the error they penalize."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))

    e = np.linspace(-3.0, 3.0, 600)
    squared = e**2
    absolute = np.abs(e)
    delta = 1.0
    # Huber: equals e^2 for |e| <= delta, then continues linearly with matching
    # slope, so it hugs squared error at the center and absolute error in the tails.
    huber = np.where(np.abs(e) <= delta, e**2, delta * (2 * np.abs(e) - delta))

    ax.plot(e, squared, color=ACCENT, lw=2.4, label="squared: (c − y)²")
    ax.plot(e, absolute, color=AMBER, lw=2.4, label="absolute: |c − y|")
    ax.plot(e, huber, color=VIOLET, lw=2.2, ls=(0, (5, 2)), label="Huber (blend)")

    # 0-1 loss: flat at one everywhere except a narrow exact-hit notch at zero.
    eps = 0.12
    ax.plot([-3, -eps], [1, 1], color=BRICK, lw=2.0)
    ax.plot([eps, 3], [1, 1], color=BRICK, lw=2.0)
    ax.plot([0], [0], marker="o", color=BRICK, markersize=5, zorder=6)
    ax.plot([0, 0], [0, 1], color=BRICK, lw=1.0, ls=(0, (1, 2)), alpha=0.6)
    ax.text(2.98, 1.12, "0–1: only exact counts", color=BRICK, fontsize=8, ha="right")

    ax.annotate(
        "Huber: quadratic\ncore, linear tails",
        xy=(1.6, 2 * 1.6 - 1),
        xytext=(2.15, 3.0),
        color=VIOLET,
        fontsize=8,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    ax.set_xlabel("error   c − y")
    ax.set_ylabel("loss")
    ax.set_xlim(-3, 3)
    ax.set_ylim(0, 7.2)
    ax.legend(loc="upper center", handlelength=1.6)
    fig.tight_layout()
    return save_plot(fig, "loss-shapes.svg")


def fig_quantile_loss() -> Path:
    """Plot: pinball loss for three quantile levels, and where each bottoms out."""
    import math

    style_plot()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.5))

    taus = ((0.1, VIOLET), (0.5, ACCENT), (0.9, AMBER))
    r = np.linspace(-3.0, 3.0, 600)

    # Left: pinball loss L_tau(r) = tau*r for r >= 0, (tau-1)*r for r < 0 — a tilted V.
    for tau, color in taus:
        loss = np.where(r >= 0, tau * r, (tau - 1.0) * r)
        ax1.plot(r, loss, color=color, lw=2.3, label=f"τ = {tau:g}")
    # Label the steep arm of tau=0.9 in the open space to its lower right.
    ax1.text(
        2.35,
        0.62,
        "steep side:\nunder-predicting\ncosts more",
        color=AMBER,
        fontsize=7.5,
        ha="center",
        va="center",
    )
    ax1.set_title("Pinball loss tilts with τ", loc="left")
    ax1.set_xlabel("residual   y − c")
    ax1.set_ylabel("loss")
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(0, 2.9)
    ax1.legend(loc="upper center", handlelength=1.4)

    # Right: a right-skewed density with the three quantiles it targets.
    x = np.linspace(0.0, 8.0, 700)
    k, theta = 2.0, 1.0  # Gamma(2, 1): right-skewed, so its quantiles spread apart.
    log_pdf = (
        (k - 1) * np.log(np.maximum(x, 1e-9))
        - x / theta
        - (math.lgamma(k) + k * math.log(theta))
    )
    pdf = np.exp(log_pdf)
    ax2.plot(x, pdf, color=INK_SOFT, lw=2.0)
    ax2.fill_between(x, pdf, color=ACCENT_SOFT, alpha=0.6)

    cdf = np.cumsum(pdf)
    cdf /= cdf[-1]
    offsets = {0.1: -0.18, 0.5: 0.18, 0.9: 0.0}  # Nudge labels off the peak.
    for tau, color in taus:
        q = float(x[np.searchsorted(cdf, tau)])
        h = float(np.interp(q, x, pdf))
        ax2.plot([q, q], [0, h], color=color, lw=2.0)
        ax2.text(
            q + offsets[tau],
            h + 0.016,
            f"{tau:g}",
            color=color,
            fontsize=8,
            ha="center",
        )
    ax2.set_title("…so its minimizer is that quantile", loc="left")
    ax2.set_xlabel("value  y")
    ax2.set_ylabel("density")
    ax2.set_xlim(0, 8)
    ax2.set_ylim(0, 0.44)
    ax2.set_yticks([])
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(length=0)

    fig.tight_layout()
    return save_plot(fig, "quantile-loss.svg")


def fig_constraint_geometry() -> Path:
    """Plot: the L2 ball vs L1 diamond meeting elliptical residual contours.

    Ridge's round ball is touched off the axes (both coefficients nonzero);
    lasso's diamond is touched at a corner on an axis (one coefficient exactly
    zero). The constrained minima are found on a grid so the tangencies are
    correct rather than hand-placed. The L1 budget satisfies t <= h1 - w*h2, the
    condition that forces the first-quadrant fit onto the corner.
    """
    style_plot()
    fig, (ax_l2, ax_l1) = plt.subplots(1, 2, figsize=(8.2, 4.1))

    # Elliptical residual contours: RSS(b) = (b1 - h1)^2 + w * (b2 - h2)^2,
    # centered on the least-squares solution and taller in the b2 direction.
    h1, h2 = 2.55, 0.72  # The unconstrained least-squares solution.
    w = 2.15  # Anisotropy: b2 deviations cost more, so the contours are elliptical.

    grid = np.linspace(-1.15, 3.15, 700)
    B1, B2 = np.meshgrid(grid, grid)
    rss = (B1 - h1) ** 2 + w * (B2 - h2) ** 2

    r = 1.08  # L2 budget radius.
    t = 0.95  # L1 budget; t <= h1 - w*h2 guarantees the corner solution.

    def constrained_min(mask):
        """Return the grid point of least RSS inside the feasible region."""
        masked = np.where(mask, rss, np.inf)
        idx = np.unravel_index(np.argmin(masked), masked.shape)
        return B1[idx], B2[idx]

    sol_l2 = constrained_min(B1**2 + B2**2 <= r**2)
    sol_l1 = constrained_min(np.abs(B1) + np.abs(B2) <= t)

    def draw(ax, region_xy, sol, title, sparse):
        # A ring of elliptical contours, the middle one passing through the fit.
        sol_level = (sol[0] - h1) ** 2 + w * (sol[1] - h2) ** 2
        levels = sol_level * np.array([0.16, 0.42, 0.72, 1.0, 1.45, 2.1])
        ax.contour(
            B1, B2, rss, levels=levels, colors=ACCENT, linewidths=0.9, alpha=0.55
        )

        # Faint axes through the origin so "on an axis" reads clearly.
        ax.axhline(0, color=RULE_STRONG, linewidth=0.9, zorder=0)
        ax.axvline(0, color=RULE_STRONG, linewidth=0.9, zorder=0)

        # The budget region.
        ax.fill(
            *region_xy, facecolor=ACCENT_SOFT, edgecolor=AMBER, linewidth=1.8, zorder=1
        )

        # The least-squares solution (ellipse center) and the constrained fit.
        ax.plot(
            [h1],
            [h2],
            marker="+",
            color=INK_SOFT,
            markersize=10,
            markeredgewidth=1.6,
            zorder=5,
        )
        ax.text(
            h1 + 0.08,
            h2 + 0.12,
            "least squares",
            color=INK_SOFT,
            fontsize=7.5,
            va="bottom",
        )
        ax.plot([sol[0]], [sol[1]], marker="o", color=BRICK, markersize=7, zorder=6)

        if sparse:
            ax.annotate(
                "corner:\nβ₂ = 0",
                xy=(sol[0], sol[1]),
                xytext=(sol[0] - 0.15, sol[1] - 0.95),
                color=BRICK,
                fontsize=8,
                ha="center",
                arrowprops=dict(arrowstyle="->", color=BRICK, lw=1.0),
            )
        else:
            ax.annotate(
                "off-axis:\nboth nonzero",
                xy=(sol[0], sol[1]),
                xytext=(sol[0] - 1.05, sol[1] + 0.75),
                color=BRICK,
                fontsize=8,
                ha="center",
                arrowprops=dict(arrowstyle="->", color=BRICK, lw=1.0),
            )

        ax.set_title(title, loc="left")
        ax.set_xlabel("β₁")
        ax.set_ylabel("β₂")
        ax.set_xlim(-1.15, 3.15)
        ax.set_ylim(-1.15, 2.35)
        ax.set_aspect("equal")
        ax.set_xticks([0])
        ax.set_yticks([0])

    # The L2 ball as a smooth ring; the L1 diamond as its four corners.
    ang = np.linspace(0, 2 * np.pi, 160)
    ball_xy = (r * np.cos(ang), r * np.sin(ang))
    diamond_xy = ([t, 0, -t, 0], [0, t, 0, -t])

    draw(ax_l2, ball_xy, sol_l2, "Ridge: the round L2 ball", sparse=False)
    draw(ax_l1, diamond_xy, sol_l1, "Lasso: the L1 diamond", sparse=True)

    fig.tight_layout()
    return save_plot(fig, "constraint-geometry.svg")


def fig_prior_densities() -> Path:
    """Plot: the Gaussian (ridge) and Laplace (lasso) priors at equal variance.

    Both are centered at zero with variance one, so the shapes alone tell the
    story: the Laplace has a sharp cusp at zero and heavier tails, the
    probabilistic face of sparsity.
    """
    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.7))

    x = np.linspace(-4.2, 4.2, 800)
    s = 1.0  # Gaussian standard deviation, so variance 1.
    b = 1.0 / np.sqrt(2.0)  # Laplace scale giving variance 2 b^2 = 1.

    gauss = np.exp(-0.5 * (x / s) ** 2) / (s * np.sqrt(2 * np.pi))
    laplace = np.exp(-np.abs(x) / b) / (2 * b)

    ax.fill_between(x, laplace, color=AMBER, alpha=0.10)
    ax.plot(x, gauss, color=ACCENT, linewidth=2.2, label="Gaussian prior → ridge")
    ax.plot(x, laplace, color=AMBER, linewidth=2.2, label="Laplace prior → lasso")

    ax.annotate(
        "cusp at zero:\nextra belief β ≈ 0",
        xy=(0, laplace[np.argmin(np.abs(x))]),
        xytext=(0.75, 0.63),
        color=AMBER,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "heavier tails:\na few large β allowed",
        xy=(3.1, laplace[np.argmin(np.abs(x - 3.1))]),
        xytext=(1.55, 0.34),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )

    ax.set_xlabel("coefficient  β")
    ax.set_ylabel("prior density")
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(0, 0.78)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(length=0)
    ax.legend(loc="upper right")

    fig.tight_layout()
    return save_plot(fig, "prior-densities.svg")


def fig_kfold_schematic() -> Path:
    """Diagram: a data bar split into k folds, each held out once in rotation."""
    width, height = 720, 430
    body = [eyebrow(30, 40, "HOLD OUT EACH FOLD ONCE")]

    k = 5
    x0, bar_w = 70, 470
    fold_w = bar_w / k
    gap = 3.0

    # Top: the full dataset, one bar split into k folds.
    top_y, top_h = 66, 40
    body.append(
        f'<text x="{x0}" y="{top_y - 14:.1f}" font-size="12" font-weight="600" '
        f'fill="{INK_SOFT}">all data, split into {k} folds</text>'
    )
    for f in range(k):
        fx = x0 + f * fold_w
        body += node_box(
            fx + gap / 2,
            top_y,
            fold_w - gap,
            top_h,
            f"fold {f + 1}",
            fill=ACCENT_SOFT,
            stroke=ACCENT,
            font_size=11,
            text_fill=ACCENT,
        )

    # Rounds: each row trains on all but one fold; the held-out fold is highlighted.
    row_y0, row_h, row_step = 148, 34, 48
    for r in range(k):
        ry = row_y0 + r * row_step
        for f in range(k):
            fx = x0 + f * fold_w
            if f == r:
                fill, stroke, tf, lab = AMBER, AMBER, "#ffffff", "test"
            else:
                fill, stroke, tf, lab = "#ffffff", RULE_STRONG, MUTED, "train"
            body += node_box(
                fx + gap / 2,
                ry,
                fold_w - gap,
                row_h,
                lab,
                fill=fill,
                stroke=stroke,
                font_size=10,
                text_fill=tf,
            )
        body.append(
            f'<text x="{x0 - 12:.1f}" y="{ry + row_h / 2 + 4:.1f}" font-size="11" '
            f'text-anchor="end" fill="{MUTED}">round {r + 1}</text>'
        )

    # The averaging brace on the right, folding k scores into one estimate.
    br_x = x0 + bar_w + 24
    body.append(arrow_marker(INK_SOFT, "kf_arrow"))
    body.append(
        f'<line x1="{br_x:.1f}" y1="{row_y0:.1f}" x2="{br_x:.1f}" '
        f'y2="{row_y0 + (k - 1) * row_step + row_h:.1f}" stroke="{RULE_STRONG}" '
        f'stroke-width="1.4"/>'
    )
    mid_y = row_y0 + ((k - 1) * row_step + row_h) / 2
    body.append(
        f'<line x1="{br_x:.1f}" y1="{mid_y:.1f}" x2="{br_x + 22:.1f}" y2="{mid_y:.1f}" '
        f'stroke="{INK_SOFT}" stroke-width="1.4" marker-end="url(#kf_arrow)"/>'
    )
    body.append(
        f'<text x="{br_x + 30:.1f}" y="{mid_y - 6:.1f}" font-size="11.5" '
        f'font-weight="700" fill="{INK}">average</text>'
    )
    body.append(
        f'<text x="{br_x + 30:.1f}" y="{mid_y + 11:.1f}" font-size="11" '
        f'fill="{MUTED}">= CV(λ)</text>'
    )

    return write_svg(
        "k-fold-schematic.svg",
        svg_doc(
            width,
            height,
            "A data bar split into five folds, with five rounds below it: each round "
            "holds out one fold for testing and trains on the rest, and the five "
            "held-out scores average into one cross-validation estimate.",
            body,
        ),
    )


def fig_cross_validation_curve() -> Path:
    """Plot: CV error as a U over the penalty, with training error sliding down."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.9))

    log_lam = np.linspace(-4.0, 4.0, 400)
    lam = 10.0**log_lam

    # Training error rises monotonically with the penalty: lowest at lambda = 0.
    train = 0.10 + 0.60 / (1.0 + np.exp(-1.0 * (log_lam - 1.0)))

    # CV error is a U: a variance term high at small lambda (overfitting) falls as
    # the penalty grows, while a bias term (underfitting) climbs with it.
    variance = 0.85 / (1.0 + np.exp(1.3 * (log_lam + 0.5)))
    bias = 0.015 * np.exp(0.9 * log_lam)
    cv = 0.30 + variance + bias
    se = 0.05 + 0.02 * (np.abs(log_lam) / 4.0)  # Fold-to-fold spread band.

    i_min = int(np.argmin(cv))
    lam_min = lam[i_min]
    # One-standard-error rule: largest lambda whose CV is within 1 SE of the min.
    thresh = cv[i_min] + se[i_min]
    right = np.where((np.arange(len(cv)) > i_min) & (cv <= thresh))[0]
    i_1se = right[-1] if len(right) else i_min
    lam_1se = lam[i_1se]

    ax.fill_between(lam, cv - se, cv + se, color=ACCENT_SOFT, alpha=0.7, linewidth=0)
    ax.plot(lam, cv, color=ACCENT, linewidth=2.4, label="cross-validation error")
    ax.plot(
        lam,
        train,
        color=MUTED,
        linewidth=2.0,
        linestyle=(0, (5, 3)),
        label="training error",
    )

    ax.plot([lam_min], [cv[i_min]], marker="o", color=ACCENT, markersize=7, zorder=6)
    ax.axvline(lam_min, color=INK_SOFT, linewidth=1.0, linestyle=(0, (2, 3)))
    ax.plot([lam_1se], [cv[i_1se]], marker="o", color=AMBER, markersize=7, zorder=6)
    ax.axvline(lam_1se, color=AMBER, linewidth=1.0, linestyle=(0, (2, 3)))

    ax.set_xscale("log")
    ax.set_xlim(lam[0], lam[-1])
    ax.set_ylim(0, 1.55)
    ax.set_xlabel("penalty  λ   (log scale)")
    ax.set_ylabel("prediction error")

    ax.annotate(
        "CV minimum",
        xy=(lam_min, cv[i_min]),
        xytext=(lam_min * 0.02, 0.72),
        color=INK_SOFT,
        fontsize=8,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "one-SE choice",
        xy=(lam_1se, cv[i_1se]),
        xytext=(lam_1se * 6.0, 0.80),
        color=AMBER,
        fontsize=8,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.0),
    )
    ax.text(lam[6], cv[6] + 0.04, "overfit", color=MUTED, fontsize=8, va="bottom")
    ax.text(
        lam[-6],
        cv[-6] + 0.04,
        "underfit",
        color=MUTED,
        fontsize=8,
        ha="right",
        va="bottom",
    )
    ax.text(
        lam[3],
        0.045,
        "training error keeps falling → picks λ = 0",
        color=MUTED,
        fontsize=7.5,
        va="bottom",
    )
    ax.legend(loc="upper center")
    fig.tight_layout()
    return save_plot(fig, "cross-validation-curve.svg")


def fig_effective_degrees_of_freedom() -> Path:
    """Plot: ridge effective degrees of freedom sliding from p down to zero."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.7))

    # A spread of squared singular values: a few large, some middling, a shaky tail.
    rng = np.random.default_rng(3)
    p = 12
    d2 = np.sort(
        np.concatenate(
            [
                rng.uniform(6.0, 14.0, 3),
                rng.uniform(0.6, 3.0, 5),
                rng.uniform(0.02, 0.3, 4),
            ]
        )
    )[::-1]

    log_lam = np.linspace(-3.0, 4.0, 400)
    lam = 10.0**log_lam
    df = np.array([(d2 / (d2 + L)).sum() for L in lam])

    ax.axhline(p, color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)))
    ax.text(
        lam[-3],
        p - 0.5,
        f"p = {p}  (least squares)",
        color=MUTED,
        fontsize=8,
        va="top",
        ha="right",
    )
    for lvl in range(0, p + 1, 3):
        ax.axhline(lvl, color=RULE, linewidth=0.7, zorder=0)

    ax.plot(lam, df, color=ACCENT, linewidth=2.6)
    ax.fill_between(lam, 0, df, color=ACCENT_SOFT, alpha=0.5, linewidth=0)

    ax.set_xscale("log")
    ax.set_xlim(lam[0], lam[-1])
    ax.set_ylim(0, p + 1.4)
    ax.set_xlabel("penalty  λ   (log scale)")
    ax.set_ylabel("effective degrees of freedom  tr(Hλ)")

    ax.annotate(
        "full complexity",
        xy=(lam[10], df[10]),
        xytext=(lam[55], p - 3.6),
        color=INK_SOFT,
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "collapses toward zero",
        xy=(lam[-40], df[-40]),
        xytext=(lam[205], 5.6),
        color=INK_SOFT,
        fontsize=8,
        ha="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    fig.tight_layout()
    return save_plot(fig, "effective-degrees-of-freedom.svg")


def fig_stein_risk() -> Path:
    """Plot: total risk of the sample mean (flat) vs James-Stein (below everywhere)."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))

    p = 8  # Number of means estimated at once; unit noise per coordinate.
    dist = np.linspace(0.0, 6.0, 500)  # Distance of the truth from the center.
    lam = dist**2  # Noncentrality: squared distance from the shrinkage center.

    mean_risk = np.full_like(dist, float(p))  # Sample mean: flat at p.
    # Standard approximation E[1/chi^2_p(lam)] ~ 1/(p - 2 + lam) gives the shape.
    js_risk = p - (p - 2) ** 2 / (p - 2 + lam)

    ax.fill_between(dist, js_risk, mean_risk, color=AMBER, alpha=0.12)
    ax.plot(dist, mean_risk, color=ACCENT, lw=2.4, label="sample mean  (report each X)")
    ax.plot(dist, js_risk, color=AMBER, lw=2.4, label="James-Stein  (shrink to center)")

    ax.plot([0.0], [2.0], marker="o", color=INK, markersize=4, zorder=6)
    ax.annotate(
        "biggest win at the center:\nrisk falls from 8 to 2",
        xy=(0.0, 2.0),
        xytext=(0.9, 3.0),
        color=INK_SOFT,
        fontsize=8,
        ha="left",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.text(
        2.9,
        7.75,
        "approaches but never reaches\nthe sample mean",
        color=INK_SOFT,
        fontsize=8,
        ha="left",
        va="top",
    )
    ax.text(
        0.1, 8.2, "flat: same risk wherever the truth sits", color=ACCENT, fontsize=8
    )

    ax.set_xlabel("distance of the true means from the shrinkage center")
    ax.set_ylabel("total risk  (expected sum of squared errors)")
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 9)
    ax.legend(loc="lower right", handlelength=1.6)
    fig.tight_layout()
    return save_plot(fig, "stein-risk.svg")


def _star(cx: float, cy: float, r: float, fill: str) -> str:
    """Return a five-pointed star centered at (cx, cy) with circumradius r."""
    import math

    pts = []
    for k in range(10):
        rad = r if k % 2 == 0 else r * 0.42
        ang = -math.pi / 2 + k * math.pi / 5
        pts.append(f"{cx + rad * math.cos(ang):.1f},{cy + rad * math.sin(ang):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def fig_stein_overshoot() -> Path:
    """Diagram: high-dimensional noise is perpendicular, so X overshoots theta."""
    import math

    width, height = 700, 430
    body = [
        eyebrow(30, 40, "THE RAW ESTIMATE IS TOO LONG"),
        arrow_marker(AMBER, "ov_pull"),
    ]

    ox, oy = 90.0, 350.0  # Origin (the shrinkage center).
    tx, ty = 430.0, 250.0  # Tip of the true vector theta.
    xx, xy = 560.0, 90.0  # The observed point X.

    body.append(f'<circle cx="{ox}" cy="{oy}" r="5" fill="{INK}"/>')
    body.append(
        f'<text x="{ox - 6:.1f}" y="{oy + 22:.1f}" font-size="12" '
        f'text-anchor="middle" fill="{INK_SOFT}">center</text>'
    )

    # Leg 1: the true vector theta, origin to its tip.
    body.append(
        f'<line x1="{ox}" y1="{oy}" x2="{tx}" y2="{ty}" stroke="{ACCENT}" '
        f'stroke-width="2.6"/>'
    )
    body.append(
        f'<text x="{(ox + tx) / 2 - 6:.1f}" y="{(oy + ty) / 2 + 26:.1f}" '
        f'font-size="14" font-style="italic" fill="{ACCENT}">true θ</text>'
    )
    body.append(f'<circle cx="{tx}" cy="{ty}" r="5" fill="{ACCENT}"/>')

    # Leg 2: the noise, rising at a right angle from the tip of theta to X.
    body.append(
        f'<line x1="{tx}" y1="{ty}" x2="{xx}" y2="{xy}" stroke="{MUTED}" '
        f'stroke-width="2.2" stroke-dasharray="6 4"/>'
    )
    body.append(
        f'<text x="{(tx + xx) / 2 + 34:.1f}" y="{(ty + xy) / 2:.1f}" '
        f'font-size="12.5" fill="{MUTED}">noise ⊥ θ</text>'
    )

    # The right-angle marker at the tip of theta.
    d1 = (ox - tx, oy - ty)
    d2 = (xx - tx, xy - ty)
    n1 = math.hypot(*d1)
    n2 = math.hypot(*d2)
    s = 16.0
    u1 = (d1[0] / n1 * s, d1[1] / n1 * s)
    u2 = (d2[0] / n2 * s, d2[1] / n2 * s)
    body.append(
        f'<path d="M {tx + u1[0]:.1f} {ty + u1[1]:.1f} '
        f"L {tx + u1[0] + u2[0]:.1f} {ty + u1[1] + u2[1]:.1f} "
        f'L {tx + u2[0]:.1f} {ty + u2[1]:.1f}" fill="none" '
        f'stroke="{MUTED}" stroke-width="1.2"/>'
    )

    # The hypotenuse: origin to X, the observed vector.
    body.append(
        f'<line x1="{ox}" y1="{oy}" x2="{xx}" y2="{xy}" stroke="{BRICK}" '
        f'stroke-width="2.6"/>'
    )
    body.append(f'<circle cx="{xx}" cy="{xy}" r="5" fill="{BRICK}"/>')
    body.append(
        f'<text x="{xx + 14:.1f}" y="{xy + 4:.1f}" font-size="14" '
        f'fill="{BRICK}">observed X</text>'
    )
    mx, my = (ox + xx) / 2 - 40, (oy + xy) / 2 - 8
    body.append(
        f'<text x="{mx:.1f}" y="{my:.1f}" font-size="12.5" fill="{BRICK}" '
        f'transform="rotate(-25 {mx:.1f} {my:.1f})">longer than θ</text>'
    )

    # The pull: X reeled back along the hypotenuse toward the center.
    px = ox + (xx - ox) * 0.62
    py = oy + (xy - oy) * 0.62
    body.append(
        f'<line x1="{xx - 8:.1f}" y1="{xy + 6:.1f}" x2="{px + 6:.1f}" '
        f'y2="{py - 4:.1f}" stroke="{AMBER}" stroke-width="2.2" '
        f'stroke-dasharray="2 4" marker-end="url(#ov_pull)"/>'
    )
    body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{AMBER}"/>')
    body.append(
        f'<text x="{px - 10:.1f}" y="{py + 22:.1f}" font-size="12.5" '
        f'text-anchor="middle" fill="{AMBER}">shrunk</text>'
    )

    body.append(
        f'<text x="30" y="{height - 20:.1f}" font-size="12" fill="{INK_SOFT}">'
        f"Noise adds nearly ⊥ θ, so ‖X‖² ≈ ‖θ‖² + pσ² — "
        f"the observed X runs longer than the truth.</text>"
    )

    return write_svg(
        "stein-overshoot.svg",
        svg_doc(
            width,
            height,
            "A right triangle from the origin: the true vector theta as one leg, "
            "perpendicular noise as the other, and the longer observed vector X as "
            "the hypotenuse, with X pulled back toward the center to land closer to "
            "theta.",
            body,
        ),
    )


def fig_borrowing_strength() -> Path:
    """Diagram: raw estimates of unrelated quantities pulled toward a shared center."""
    width, height = 720, 430
    body = [
        eyebrow(30, 38, "SHRINK ALL OF THEM TOWARD ONE CENTER"),
        arrow_marker(AMBER, "bs_pull"),
    ]

    # Value axis geometry: value v in [0, 1] maps to x in [x0, x1].
    x0, x1 = 250.0, 660.0
    center = 0.5  # The shared shrinkage center (grand average), on a common scale.
    shrink = 0.6  # Pull factor: shrunk = center + shrink * (raw - center).

    def xof(v: float) -> float:
        return x0 + v * (x1 - x0)

    # Each row: an unrelated quantity, its true value, and its raw reading. The raw
    # readings overshoot outward from the center, so shrinking lands nearer truth.
    rows = (
        ("batting average", 0.80, 0.95),
        ("wheat yield", 0.20, 0.05),
        ("used-car price", 0.65, 0.82),
        ("toxin level", 0.35, 0.16),
        ("exam score", 0.55, 0.70),
    )
    y0, step, lane_h = 78.0, 62.0, 62.0

    xc = xof(center)
    top = y0 - 14
    bot = y0 + (len(rows) - 1) * step + lane_h - 30
    body.append(
        f'<line x1="{xc:.1f}" y1="{top:.1f}" x2="{xc:.1f}" y2="{bot:.1f}" '
        f'stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="5 4"/>'
    )
    body.append(
        f'<text x="{xc:.1f}" y="{top - 6:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{MUTED}">shared center</text>'
    )

    for i, (name, truth, raw) in enumerate(rows):
        cy = y0 + i * step
        body.append(
            f'<line x1="{x0 - 4:.1f}" y1="{cy:.1f}" x2="{x1 + 8:.1f}" y2="{cy:.1f}" '
            f'stroke="{RULE}" stroke-width="1.2"/>'
        )
        body.append(
            f'<text x="{x0 - 20:.1f}" y="{cy + 4:.1f}" font-size="12.5" '
            f'text-anchor="end" fill="{INK_SOFT}">{name}</text>'
        )

        shrunk = center + shrink * (raw - center)
        xr, xs, xt = xof(raw), xof(shrunk), xof(truth)

        body.append(
            f'<line x1="{xr:.1f}" y1="{cy:.1f}" '
            f'x2="{xs + (6 if xs < xr else -6):.1f}" y2="{cy:.1f}" '
            f'stroke="{AMBER}" stroke-width="1.6" marker-end="url(#bs_pull)"/>'
        )
        body.append(_star(xt, cy, 8.0, ACCENT))
        body.append(
            f'<circle cx="{xr:.1f}" cy="{cy:.1f}" r="6" fill="{PAPER}" '
            f'stroke="{ACCENT}" stroke-width="2.2"/>'
        )
        body.append(f'<circle cx="{xs:.1f}" cy="{cy:.1f}" r="6" fill="{AMBER}"/>')

    # A compact legend along the bottom.
    ly = bot + 34
    lx = x0 - 20
    body.append(_star(lx + 6, ly - 4, 7.0, ACCENT))
    body.append(
        f'<text x="{lx + 20:.1f}" y="{ly:.1f}" font-size="11.5" fill="{INK_SOFT}">'
        f"truth</text>"
    )
    body.append(
        f'<circle cx="{lx + 118:.1f}" cy="{ly - 4:.1f}" r="6" fill="{PAPER}" '
        f'stroke="{ACCENT}" stroke-width="2.2"/>'
    )
    body.append(
        f'<text x="{lx + 132:.1f}" y="{ly:.1f}" font-size="11.5" fill="{INK_SOFT}">'
        f"raw estimate</text>"
    )
    body.append(f'<circle cx="{lx + 268:.1f}" cy="{ly - 4:.1f}" r="6" fill="{AMBER}"/>')
    body.append(
        f'<text x="{lx + 282:.1f}" y="{ly:.1f}" font-size="11.5" fill="{INK_SOFT}">'
        f"shrunk estimate</text>"
    )

    return write_svg(
        "borrowing-strength.svg",
        svg_doc(
            width,
            height,
            "Five lanes for unrelated quantities, each with a raw estimate pulled "
            "toward a shared center to a shrunk estimate, landing closer to the true "
            "value.",
            body,
        ),
    )


def fig_wilks_chi_square() -> Path:
    """Plot: chi-square reference curves for -2 log Lambda under Wilks' theorem."""
    style_plot()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))

    x = np.linspace(0.04, 10.0, 700)
    root2pi = np.sqrt(2 * np.pi)
    chi1 = x ** (-0.5) * np.exp(-x / 2) / root2pi  # df = 1.
    chi2 = np.exp(-x / 2) / 2.0  # df = 2.
    chi3 = x**0.5 * np.exp(-x / 2) / root2pi  # df = 3.

    ax.plot(x, chi1, color=ACCENT, lw=2.4, label="χ², df = 1  (one restriction)")
    ax.plot(x, chi2, color=AMBER, lw=2.2, label="χ², df = 2  (two restrictions)")
    ax.plot(x, chi3, color=VIOLET, lw=2.2, label="χ², df = 3  (three restrictions)")

    # The 5% critical value for df = 1, and the tail beyond it: the size-alpha region.
    crit = 3.84
    tail = x >= crit
    ax.fill_between(x, 0, chi1, where=tail, color=BRICK, alpha=0.16)
    ax.axvline(crit, color=MUTED, lw=1.0, ls=(0, (4, 3)))

    ax.annotate(
        "tail past the cutoff = α\n(reject H₀ out here)",
        xy=(4.8, 0.018),
        xytext=(5.5, 0.20),
        color=BRICK,
        fontsize=8,
        ha="left",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.text(
        3.66,
        0.47,
        "5% cutoff for df = 1\n(−2 log Λ = 3.84)",
        color=INK_SOFT,
        fontsize=8,
        ha="right",
        va="top",
    )

    ax.set_xlabel("likelihood-ratio statistic  −2 log Λ")
    ax.set_ylabel("density under H₀")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 0.55)
    ax.legend(loc="upper right", handlelength=1.5)
    fig.tight_layout()
    return save_plot(fig, "wilks-chi-square.svg")


def fig_pvalue_null_distribution() -> Path:
    """Plot: the p-value is Uniform under the null, right-skewed under an effect."""
    import math

    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.9))

    # Standard normal CDF via the complementary error function (no SciPy needed).
    phi = np.vectorize(lambda z: 0.5 * math.erfc(-z / math.sqrt(2.0)))

    rng = np.random.default_rng(0)
    n = 300_000
    effect = 2.6  # True effect in standard-error units; a well-powered study.

    # One-sided z-test p-values: p = 1 - Phi(Z), with Z drawn under each world.
    p_null = 1.0 - phi(rng.standard_normal(n))
    p_alt = 1.0 - phi(rng.standard_normal(n) + effect)

    bins = np.linspace(0.0, 1.0, 21)
    d_null, _ = np.histogram(p_null, bins=bins, density=True)
    d_alt, _ = np.histogram(p_alt, bins=bins, density=True)
    centers = 0.5 * (bins[:-1] + bins[1:])

    # Shade the p < 0.05 rejection strip.
    ax.axvspan(0.0, 0.05, color=AMBER, alpha=0.14, linewidth=0)

    ax.bar(
        centers,
        d_alt,
        width=0.045,
        color=ACCENT_SOFT,
        edgecolor=ACCENT,
        linewidth=1.0,
        label="a real effect is present",
        zorder=3,
    )
    ax.step(
        bins,
        np.append(d_null, d_null[-1]),
        where="post",
        color=MUTED,
        linewidth=2.0,
        linestyle=(0, (5, 3)),
        label="the null is true (Uniform)",
        zorder=4,
    )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, max(d_alt) * 1.18)
    ax.set_xlabel("p-value")
    ax.set_ylabel("density")

    ax.annotate(
        "5% of null p-values\nland here — that is α",
        xy=(0.03, 1.0),
        xytext=(0.32, max(d_alt) * 0.60),
        color=INK_SOFT,
        fontsize=8,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax.annotate(
        "far more of the effect's\nmass lands here — power",
        xy=(0.035, max(d_alt) * 0.9),
        xytext=(0.34, max(d_alt) * 0.98),
        color=ACCENT,
        fontsize=8,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.0),
    )
    ax.legend(loc="center right")
    fig.tight_layout()
    return save_plot(fig, "pvalue-null-distribution.svg")


def fig_power_curve() -> Path:
    """Plot: statistical power climbing with sample size, at three effect sizes."""
    import math

    style_plot()
    fig, ax = plt.subplots(figsize=(6.4, 3.9))

    phi = np.vectorize(lambda z: 0.5 * math.erfc(-z / math.sqrt(2.0)))
    z_crit = 1.959963985  # Two-sided α = 0.05 critical value.

    n = np.arange(4, 401)
    effects = [
        (0.2, "small effect (d = 0.2)", BRICK),
        (0.5, "medium effect (d = 0.5)", AMBER),
        (0.8, "large effect (d = 0.8)", ACCENT),
    ]

    ax.axhline(0.8, color=INK_SOFT, linewidth=1.0, linestyle=(0, (2, 3)))
    ax.text(
        398, 0.815, "80% target", color=INK_SOFT, fontsize=8, ha="right", va="bottom"
    )

    for d, label, color in effects:
        ncp = d * np.sqrt(n)  # Noncentrality for a one-sample z-test in SD units.
        power = phi(ncp - z_crit) + phi(-ncp - z_crit)
        ax.plot(n, power, color=color, linewidth=2.4, label=label)
        # Mark where each curve first reaches the 80% target.
        reached = np.where(power >= 0.8)[0]
        if len(reached):
            i = reached[0]
            ax.plot([n[i]], [power[i]], marker="o", color=color, markersize=6, zorder=6)

    ax.set_xlim(n[0], n[-1])
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("sample size  n")
    ax.set_ylabel("power  (1 − β)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    return save_plot(fig, "power-curve.svg")


def fig_false_discovery_base_rate() -> Path:
    """Diagram: how a low base rate floods significant results with false positives."""
    width, height = 760, 430
    body = [eyebrow(30, 40, "A 5% TEST ON A 10% BASE RATE")]

    body.append(arrow_marker(MUTED, "fdr_arrow"))

    # Top box: the pool of hypotheses.
    top_x, top_y, top_w, top_h = 300, 60, 160, 46
    body += node_box(
        top_x,
        top_y,
        top_w,
        top_h,
        "1000 hypotheses",
        fill="#ffffff",
        stroke=RULE_STRONG,
        font_size=13,
        weight=600,
    )

    # Second level: real effects vs no effect.
    real_x, real_y, lvl_w, lvl_h = 130, 168, 200, 46
    null_x = 430
    body += node_box(
        real_x,
        real_y,
        lvl_w,
        lvl_h,
        "100 real effects  (10%)",
        fill=ACCENT_SOFT,
        stroke=ACCENT,
        text_fill=ACCENT,
        font_size=12,
        weight=600,
    )
    body += node_box(
        null_x,
        real_y,
        lvl_w,
        lvl_h,
        "900 no effect",
        fill="#ffffff",
        stroke=RULE_STRONG,
        text_fill=MUTED,
        font_size=12,
        weight=600,
    )
    # Arrows from top to the two branches.
    body.append(
        f'<line x1="{top_x + 40:.1f}" y1="{top_y + top_h:.1f}" '
        f'x2="{real_x + lvl_w / 2:.1f}" y2="{real_y:.1f}" stroke="{MUTED}" '
        f'stroke-width="1.4" marker-end="url(#fdr_arrow)"/>'
    )
    body.append(
        f'<line x1="{top_x + top_w - 40:.1f}" y1="{top_y + top_h:.1f}" '
        f'x2="{null_x + lvl_w / 2:.1f}" y2="{real_y:.1f}" stroke="{MUTED}" '
        f'stroke-width="1.4" marker-end="url(#fdr_arrow)"/>'
    )

    # Third level: significant results from each branch.
    sig_y, sig_w, sig_h = 276, 200, 46
    body += node_box(
        real_x,
        sig_y,
        sig_w,
        sig_h,
        "≈ 80 significant  (power 80%)",
        fill=ACCENT_SOFT,
        stroke=ACCENT,
        text_fill=ACCENT,
        font_size=11.5,
        weight=600,
    )
    body += node_box(
        null_x,
        sig_y,
        sig_w,
        sig_h,
        "≈ 45 significant  (α = 5%)",
        fill="#fbe9e6",
        stroke=BRICK,
        text_fill=BRICK,
        font_size=11.5,
        weight=600,
    )
    body.append(
        f'<line x1="{real_x + lvl_w / 2:.1f}" y1="{real_y + lvl_h:.1f}" '
        f'x2="{real_x + sig_w / 2:.1f}" y2="{sig_y:.1f}" stroke="{ACCENT}" '
        f'stroke-width="1.4" marker-end="url(#fdr_arrow)"/>'
    )
    body.append(
        f'<line x1="{null_x + lvl_w / 2:.1f}" y1="{real_y + lvl_h:.1f}" '
        f'x2="{null_x + sig_w / 2:.1f}" y2="{sig_y:.1f}" stroke="{BRICK}" '
        f'stroke-width="1.4" marker-end="url(#fdr_arrow)"/>'
    )
    body.append(
        f'<text x="{real_x + sig_w / 2:.1f}" y="{sig_y + sig_h + 18:.1f}" '
        f'font-size="10.5" text-anchor="middle" fill="{ACCENT}">true positives</text>'
    )
    body.append(
        f'<text x="{null_x + sig_w / 2:.1f}" y="{sig_y + sig_h + 18:.1f}" '
        f'font-size="10.5" text-anchor="middle" fill="{BRICK}">false positives</text>'
    )

    # Summary bar.
    bar_x, bar_y, bar_w, bar_h = 130, 360, 500, 34
    tp_frac = 80.0 / 125.0
    body.append(
        f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_w * tp_frac:.1f}" '
        f'height="{bar_h}" rx="4" fill="{ACCENT}"/>'
    )
    body.append(
        f'<rect x="{bar_x + bar_w * tp_frac:.1f}" y="{bar_y:.1f}" '
        f'width="{bar_w * (1 - tp_frac):.1f}" height="{bar_h}" rx="4" fill="{BRICK}"/>'
    )
    body.append(
        f'<text x="{bar_x + bar_w * tp_frac / 2:.1f}" y="{bar_y + bar_h / 2 + 4:.1f}" '
        f'font-size="11" text-anchor="middle" fill="#ffffff" font-weight="600">80 true</text>'
    )
    body.append(
        f'<text x="{bar_x + bar_w * tp_frac + bar_w * (1 - tp_frac) / 2:.1f}" '
        f'y="{bar_y + bar_h / 2 + 4:.1f}" font-size="11" text-anchor="middle" '
        f'fill="#ffffff" font-weight="600">45 false</text>'
    )
    body.append(
        f'<text x="{bar_x + bar_w:.1f}" y="{bar_y - 8:.1f}" font-size="11.5" '
        f'text-anchor="end" fill="{INK_SOFT}" font-weight="600">'
        f"125 significant results → 36% are false discoveries</text>"
    )

    svg = svg_doc(width, height, "Base-rate flow showing false discoveries", body)
    return write_svg("false-discovery-base-rate.svg", svg)


def fig_coverage_intervals() -> Path:
    """Plot: many 95% intervals from repeated samples against the one fixed truth."""
    style_plot()
    rng = np.random.default_rng(4)
    true_theta = 0.0  # The one fixed parameter every interval is trying to trap.
    n = 25
    sigma = 1.0
    se = sigma / np.sqrt(n)
    z = 1.96  # The normal quantile behind a 95% interval.
    n_rep = 22

    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    n_miss = 0
    for i in range(n_rep):
        xbar = rng.normal(true_theta, se)
        lo, hi = xbar - z * se, xbar + z * se
        y = n_rep - i
        covers = lo <= true_theta <= hi
        color = ACCENT if covers else BRICK
        if not covers:
            n_miss += 1
        ax.plot(
            [lo, hi],
            [y, y],
            color=color,
            linewidth=2.2,
            solid_capstyle="round",
            alpha=0.5 if not covers else 0.9,
        )
        ax.plot([xbar], [y], marker="o", color=color, markersize=3.4, zorder=5)

    ax.axvline(true_theta, color=INK_SOFT, linestyle="--", linewidth=1.4, zorder=1)
    ax.text(
        true_theta + 0.01,
        n_rep + 0.9,
        "the fixed truth θ",
        color=INK_SOFT,
        fontsize=8.5,
        ha="left",
        va="center",
    )
    n_cover = n_rep - n_miss
    ax.set_title(
        f"{n_cover} of {n_rep} intervals catch θ; {n_miss} miss (red)", loc="left"
    )
    ax.set_xlabel("value of the parameter")
    ax.set_ylabel("independent repetition of the experiment")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(length=0, axis="y")
    ax.set_ylim(0.2, n_rep + 2.0)
    fig.tight_layout()
    return save_plot(fig, "coverage-intervals.svg")


def fig_credible_intervals() -> Path:
    """Plot: equal-tailed vs highest-posterior-density 95% intervals on a skew posterior."""
    style_plot()
    k, theta = 2.0, 1.0  # A right-skewed posterior: mode at 1, long right tail.
    x = np.linspace(0.0, 9.0, 4000)
    dens = _gamma_pdf(x, k, theta)
    dx = x[1] - x[0]
    cdf = np.cumsum(dens) * dx

    def quantile(p):
        return float(x[np.searchsorted(cdf, p)])

    # Equal-tailed interval: chop 2.5% of probability off each tail.
    et_lo, et_hi = quantile(0.025), quantile(0.975)

    # HPD interval as a density level set: lower a horizontal water level until the
    # mass above it reaches 95%. For a unimodal density the region above the level
    # is a single interval whose two ends sit at equal density.
    target = 0.95
    lo_h, hi_h = 0.0, float(dens.max())
    for _ in range(80):
        h = 0.5 * (lo_h + hi_h)
        mass = float(dens[dens >= h].sum() * dx)
        if mass > target:
            lo_h = h
        else:
            hi_h = h
    hpd_level = 0.5 * (lo_h + hi_h)
    above = np.where(dens >= hpd_level)[0]
    hpd_lo, hpd_hi = float(x[above[0]]), float(x[above[-1]])

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(6.0, 5.4), sharex=True, gridspec_kw={"hspace": 0.34}
    )

    # Top: equal-tailed. Symmetric probability, asymmetric interval on a skew.
    ax_top.plot(x, dens, color=ACCENT, linewidth=2.2)
    m = (x >= et_lo) & (x <= et_hi)
    ax_top.fill_between(x[m], 0, dens[m], color=ACCENT_SOFT)
    for xb in (et_lo, et_hi):
        ax_top.plot(
            [xb, xb],
            [0, dens[np.searchsorted(x, xb)]],
            color=VIOLET,
            linewidth=1.3,
            linestyle=(0, (4, 3)),
        )
    ax_top.text(
        et_lo, -0.03, f"{et_lo:.2f}", color=VIOLET, fontsize=7.5, ha="center", va="top"
    )
    ax_top.text(
        et_hi, -0.03, f"{et_hi:.2f}", color=VIOLET, fontsize=7.5, ha="center", va="top"
    )
    ax_top.annotate("2.5%", xy=(0.32, 0.02), color=MUTED, fontsize=7, ha="center")
    ax_top.annotate(
        "2.5%", xy=(et_hi + 0.45, 0.02), color=MUTED, fontsize=7, ha="center"
    )
    ax_top.set_title("Equal-tailed: equal probability cut from each tail", loc="left")
    ax_top.set_ylabel("posterior density")

    # Bottom: HPD. A flat water level; the ends sit at equal height, interval shorter.
    ax_bot.plot(x, dens, color=ACCENT, linewidth=2.2)
    m2 = (x >= hpd_lo) & (x <= hpd_hi)
    ax_bot.fill_between(x[m2], 0, dens[m2], color="#f0e2c8")
    ax_bot.axhline(hpd_level, color=AMBER, linewidth=1.2, linestyle=(0, (4, 3)))
    ax_bot.text(
        8.8,
        hpd_level + 0.007,
        "equal density at the two ends",
        color=AMBER,
        fontsize=7.5,
        ha="right",
        va="bottom",
    )
    for xb in (hpd_lo, hpd_hi):
        ax_bot.plot([xb, xb], [0, hpd_level], color=AMBER, linewidth=1.4)
    ax_bot.text(
        hpd_lo, -0.03, f"{hpd_lo:.2f}", color=AMBER, fontsize=7.5, ha="center", va="top"
    )
    ax_bot.text(
        hpd_hi, -0.03, f"{hpd_hi:.2f}", color=AMBER, fontsize=7.5, ha="center", va="top"
    )
    ax_bot.set_title(
        "Highest posterior density: shortest interval holding 95%", loc="left"
    )
    ax_bot.set_ylabel("posterior density")
    ax_bot.set_xlabel("parameter value")

    for ax in (ax_top, ax_bot):
        ax.set_ylim(0, 0.42)
        ax.set_xlim(0, 9)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.tick_params(length=0, axis="y")

    return save_plot(fig, "credible-intervals.svg")


def fig_test_interval_duality() -> Path:
    """Diagram: invert a test — the null values whose test accepts form the interval."""
    width, height = 760, 470
    body = [eyebrow(30, 40, "AN INTERVAL IS A FAMILY OF TESTS")]

    # Statistic space runs left to right in pixels; each row is a candidate null
    # value theta0 whose level-alpha test either accepts or rejects the one observed
    # estimate. The rows whose acceptance band covers the estimate are the interval.
    stat_lo, stat_hi = -5.0, 9.0
    px_lo, px_hi = 236.0, 690.0
    sx = (px_hi - px_lo) / (stat_hi - stat_lo)

    def xof(v):
        return px_lo + (v - stat_lo) * sx

    x_obs = 2.0  # The single observed estimate, fixed across every row.
    c = 2.4  # Half-width of each test's acceptance region, in statistic units.
    theta0s = [6, 5, 4, 3, 2, 1, 0, -1, -2]
    y0, step = 74, 40
    x_obs_px = xof(x_obs)

    accepted_rows = []
    for i, t0 in enumerate(theta0s):
        y = y0 + i * step
        center = xof(t0)
        lo, hi = center - c * sx, center + c * sx
        accept = lo <= x_obs_px <= hi
        color = ACCENT if accept else BRICK
        if accept:
            accepted_rows.append((i, y, t0))
        body.append(
            f'<text x="150" y="{y + 4:.1f}" font-size="12.5" text-anchor="end" '
            f'fill="{INK if accept else MUTED}" font-weight="{700 if accept else 400}">'
            f"θ₀ = {t0}</text>"
        )
        body.append(
            f'<line x1="{lo:.1f}" y1="{y:.1f}" x2="{hi:.1f}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-width="6" stroke-linecap="round" '
            f'opacity="{0.9 if accept else 0.38}"/>'
        )
        if accept:
            body.append(
                f'<text x="714" y="{y + 5:.1f}" font-size="15" text-anchor="middle" '
                f'fill="{ACCENT}" font-weight="700">✓</text>'
            )
        else:
            body.append(
                f'<text x="714" y="{y + 5:.1f}" font-size="15" text-anchor="middle" '
                f'fill="{BRICK}" opacity="0.7">✗</text>'
            )

    # The fixed observed estimate: one vertical line through every row.
    top_y = y0 - 24
    bot_y = y0 + (len(theta0s) - 1) * step + 24
    body.append(
        f'<line x1="{x_obs_px:.1f}" y1="{top_y:.1f}" x2="{x_obs_px:.1f}" '
        f'y2="{bot_y:.1f}" stroke="{INK_SOFT}" stroke-width="1.6" '
        f'stroke-dasharray="5 4"/>'
    )
    body.append(
        f'<text x="{x_obs_px:.1f}" y="{top_y - 6:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}" font-weight="600">observed estimate</text>'
    )

    # Bracket the accepted rows on the left as the confidence interval.
    if accepted_rows:
        y_top = accepted_rows[0][1] - step / 2
        y_bot = accepted_rows[-1][1] + step / 2
        bx = 170
        body.append(
            f'<path d="M {bx + 10:.1f} {y_top:.1f} H {bx:.1f} V {y_bot:.1f} '
            f'H {bx + 10:.1f}" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>'
        )
        ymid = (y_top + y_bot) / 2
        body.append(
            f'<text x="{bx - 8:.1f}" y="{ymid:.1f}" font-size="11" '
            f'text-anchor="middle" fill="{ACCENT}" font-weight="700" '
            f'transform="rotate(-90 {bx - 8:.1f} {ymid:.1f})">1−α interval</text>'
        )

    body.append(
        f'<text x="{(px_lo + px_hi) / 2:.1f}" y="{bot_y + 34:.1f}" font-size="11.5" '
        f'text-anchor="middle" fill="{INK_SOFT}">Each row tests H₀: θ = θ₀. '
        f"The un-rejected θ₀ (blue, ✓) are the interval.</text>"
    )

    return write_svg(
        "test-interval-duality.svg",
        svg_doc(
            width,
            height,
            "A stack of candidate null values, each with an acceptance band in "
            "statistic space; the fixed observed estimate falls inside some bands "
            "and not others, and the null values whose test accepts form the "
            "confidence interval.",
            body,
        ),
    )


# ---------------------------------------------------------------------------
# The cover and the icons.
#
# The book's identity is a normal bell curve over a shaded area, with an amber
# dot at its peak — the universal picture of a distribution, and the object
# every chapter ultimately reasons about.
# ---------------------------------------------------------------------------


def _bell_points(
    x_left: float, x_right: float, y_bottom: float, y_top: float, n: int = 140
) -> list[tuple[float, float]]:
    """Trace a standard-normal bell across a box (y grows downward, as in SVG)."""
    import math

    span_x = x_right - x_left
    span_y = y_bottom - y_top
    pts = []
    for i in range(n + 1):
        u = -3.4 + 6.8 * i / n
        value = math.exp(-u * u / 2.0)
        pts.append((x_left + (i / n) * span_x, y_bottom - value * span_y))
    return pts


def bell_svg(
    x_left: float,
    x_right: float,
    y_bottom: float,
    y_top: float,
    *,
    stroke_w: float,
    node_r: float,
    axes: bool = False,
) -> str:
    """Emit the identity motif: a shaded bell curve with an amber dot at its peak."""
    pts = _bell_points(x_left, x_right, y_bottom, y_top)
    curve_d = " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    x_mid = (x_left + x_right) / 2.0
    parts = []
    if axes:
        parts.append(
            f'<line x1="{x_left - 8:.1f}" y1="{y_bottom:.1f}" '
            f'x2="{x_right + 8:.1f}" y2="{y_bottom:.1f}" '
            f'stroke="{RULE_STRONG}" stroke-width="1.5"/>'
        )
    parts.append(
        f'<path d="M {x_left:.1f} {y_bottom:.1f} L {curve_d} '
        f'L {x_right:.1f} {y_bottom:.1f} Z" fill="{ACCENT_SOFT}" stroke="none"/>'
    )
    parts.append(
        f'<path d="M {curve_d}" fill="none" stroke="{ACCENT}" '
        f'stroke-width="{stroke_w:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    parts.append(
        f'<circle cx="{x_mid:.1f}" cy="{y_top:.1f}" r="{node_r:.1f}" fill="{AMBER}"/>'
    )
    return "\n".join(parts)


def fig_cover() -> Path:
    """The book cover: title over the bell-curve motif, framed like a monograph."""
    width, height = 640, 960
    # Wrap the title (large serif) and subtitle (small sans) to the cover width
    # so any book's title fits without hand-tuning.
    title = "The Shape of Statistical Theory"
    subtitle = "How the pieces of theoretical statistics fit — distributions, estimation, risk, and regularization, from intuition up."
    title_lines = textwrap.wrap(title, width=14) or ["Untitled"]
    subtitle_lines = textwrap.wrap(subtitle, width=42)[:3]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="Book cover: The Shape of Statistical Theory. A '
        f'normal bell curve over a shaded area, with a dot at its peak.">',
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
        f'<rect x="26" y="26" width="{width - 52}" height="{height - 52}" '
        f'fill="none" stroke="{RULE_STRONG}" stroke-width="1.5"/>',
        f'<text x="72" y="152" font-family="{SANS}" font-size="16" '
        f'font-weight="650" letter-spacing="5" fill="{ACCENT}">A TEXTBOOK</text>',
    ]
    for i, line in enumerate(title_lines):
        parts.append(
            f'<text x="68" y="{232 + i * 72}" font-family="{SERIF}" font-size="58" '
            f'font-weight="700" fill="{INK}">{line}</text>'
        )

    parts.append(bell_svg(150, 490, 706, 496, stroke_w=3.5, node_r=10, axes=True))

    parts.append(
        f'<path d="M 72 830 L 148 830" stroke="{RULE_STRONG}" stroke-width="1.5"/>'
    )
    for i, line in enumerate(subtitle_lines):
        parts.append(
            f'<text x="72" y="{862 + i * 23}" font-family="{SANS}" font-size="15.5" '
            f'fill="{MUTED}">{line}</text>'
        )
    parts.append("</svg>")
    return write_root_asset("cover.svg", "\n".join(parts))


def fig_icon() -> Path:
    """The favicon: the bell-curve motif alone on a rounded paper tile."""
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" role="img" '
        'aria-label="Site icon: a normal bell curve over a shaded area.">',
        f'<rect width="180" height="180" rx="36" fill="{PAPER}"/>',
        bell_svg(30, 150, 140, 52, stroke_w=6, node_r=9),
        "</svg>",
    ]
    return write_root_asset("icon.svg", "\n".join(parts))


def fig_touch_icon() -> Path:
    """The apple-touch-icon: the favicon motif, full-bleed PNG (iOS rounds it).

    iOS does not accept SVG here, so matplotlib re-draws the same geometry as
    `fig_icon` at exactly 180 by 180 pixels.
    """
    from matplotlib.patches import Circle, Polygon, Rectangle

    dpi = 100
    fig = plt.figure(figsize=(1.8, 1.8), dpi=dpi)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_xlim(0, 180)
    ax.set_ylim(180, 0)  # Flip y so the geometry matches the SVG coordinates.
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 180, 180, facecolor=PAPER, edgecolor="none"))

    px = 72 / dpi  # One SVG stroke pixel is this many matplotlib points.
    pts = _bell_points(30, 150, 140, 52)

    area = [(30, 140)] + pts + [(150, 140)]
    ax.add_patch(Polygon(area, closed=True, facecolor=ACCENT_SOFT, edgecolor="none"))
    ax.plot(
        [p[0] for p in pts],
        [p[1] for p in pts],
        color=ACCENT,
        linewidth=6 * px,
        solid_capstyle="round",
        solid_joinstyle="round",
    )
    ax.add_patch(Circle((90, 52), radius=9, facecolor=AMBER, edgecolor="none"))

    path = ASSETS_DIR / "apple-touch-icon.png"
    fig.savefig(path, dpi=dpi, facecolor=PAPER)
    plt.close(fig)
    return path


FIGURES = (
    # Ch 1 · What This Book Is About
    fig_two_moves,
    fig_field_map,
    fig_one_question,
    # Ch 2 · Random Variables and Distributions
    fig_cdf_pdf,
    fig_joint_marginals,
    # Ch 3 · Expectation, Moments, and Their Uses
    fig_center_of_mass,
    fig_moment_shapes,
    fig_mgf_convolution,
    # Ch 4 · Families of Distributions
    fig_exponential_family_umbrella,
    fig_sufficient_statistic,
    fig_outside_the_family,
    # Ch 5 · Convergence and the Limit Theorems
    fig_convergence_modes,
    fig_lln_settling,
    # Ch 6 · What Makes a Good Estimator
    fig_estimator_sampling_distributions,
    fig_consistency_concentration,
    # Ch 7 · Sufficiency and Information
    fig_factorization,
    fig_information_curvature,
    # Ch 8 · Maximum Likelihood
    fig_mle_asymptotics,
    fig_mle_pitfalls,
    # Ch 9 · The Bayesian View
    fig_prior_likelihood_posterior,
    fig_posterior_summaries,
    # Ch 10 · Loss Functions
    fig_loss_shapes,
    fig_quantile_loss,
    # Ch 11 · Risk and Decision Theory
    fig_risk_curves,
    fig_minimax_bayes,
    # Ch 12 · The Bias–Variance Tradeoff
    fig_dartboard,
    # Ch 13 · The Shrinkage Surprise
    fig_stein_risk,
    fig_stein_overshoot,
    fig_borrowing_strength,
    # Ch 14 · Penalties and Priors
    fig_constraint_geometry,
    fig_prior_densities,
    # Ch 15 · Choosing the Penalty
    fig_kfold_schematic,
    fig_cross_validation_curve,
    fig_effective_degrees_of_freedom,
    # Ch 16 · Hypothesis Testing
    fig_wilks_chi_square,
    # Ch 17 · P-values, Power, and Errors
    fig_pvalue_null_distribution,
    fig_false_discovery_base_rate,
    fig_power_curve,
    # Ch 18 · Confidence and Credible Intervals
    fig_coverage_intervals,
    fig_credible_intervals,
    fig_test_interval_duality,
    # Cover and icons
    fig_cover,
    fig_icon,
    fig_touch_icon,
)


def main() -> None:
    """Regenerate every figure and report where it went."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for make in FIGURES:
        path = make()
        assert (
            path.exists()
        ), f"Figure function '{make.__name__}' did not write its file."
        print(f"  wrote {path.relative_to(ROOT)}")
    print(f"Generated {len(FIGURES)} figures.")


if __name__ == "__main__":
    main()
