# The Shape of Statistical Theory

How the pieces of theoretical statistics fit — distributions, estimation, risk, and regularization, from intuition up.

The book is generated from Markdown by a small Python build (no framework).

> **How this book was made.** This is an AI-generated textbook. The prose,
> figures, quizzes, and citations were drafted by a large language model —
> Zorian directing — and then checked against primary sources. It exists so
> its author can learn this subject by synthesizing the current literature; treat
> it as a well-cited study companion, not a peer-reviewed authority, and verify
> load-bearing claims against the cited sources before relying on them.

## Status

Scaffolded, not yet drafted. Every chapter renders as a navigable stub from its
outline in `toc.py`. Authoring conventions live in **`CLAUDE.md`** — read it
before writing. The one drafted chapter (`content/transformer.md`) is a worked
example that shows every feature; delete it once your own chapters land.

## Build

```bash
pip install markdown pymdown-extensions pygments matplotlib   # once
python figures/make_figures.py    # regenerate figures, cover, and icons
python build.py                   # regenerate docs/
python -m http.server -d docs     # preview at http://localhost:8000
```

`docs/` is build output and is gitignored; CI regenerates it on every push.

## Layout

| Path | Role |
|---|---|
| `toc.py` | Single source of truth for structure |
| `CLAUDE.md` | Authoring guide and conventions |
| `references.py` / `quizzes.py` / `glossary.py` | Single sources of truth for citations, quizzes, glossary |
| `content/<slug>.md` | One Markdown file per drafted chapter (optional) |
| `figures/make_figures.py` | Generates every figure as SVG, plus cover/icons |
| `build.py` | The generator |
| `assets/style.css` | The full visual design (macOS-native fonts, no CDN) |
| `docs/` | Build output. Do not edit by hand; not committed to git. |

## Deploy

See `DEPLOY.md`. In short: push to a public GitHub repo, set **Settings → Pages
→ Source → GitHub Actions**, and the workflow builds and publishes on every push
to `main`. The book will be live at
`https://zorian15.github.io/shape-of-statistical-theory/`.

## Template

This book was generated from the
[textbook-template](https://github.com/zorian15/textbook-template) copier
template. To pull later engine improvements, run `copier update` in this repo.
