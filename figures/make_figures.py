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
    fig_dartboard,
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
