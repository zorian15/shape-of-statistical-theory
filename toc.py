"""Single source of truth for the book's structure.

`build.py` imports `BOOK` from this module and generates one HTML file per
entry, plus the landing page. To reorder, rename, or add a chapter, edit this
file and rerun the build. If a chapter has a matching `content/<slug>.md`, that
prose is rendered; otherwise a stub page is synthesized from the `outline`
declared here, so the whole book is always navigable even before it is written.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chapter:
    """One page of the book.

    `slug` is the file stem (used for `content/<slug>.md` and `<slug>.html`).
    `label` is the display number shown in navigation and section numbering:
    a digit for chapters, a letter for appendices, or an empty string for
    unnumbered front matter. `outline` is a list of (section_title, note)
    pairs describing what the chapter should eventually cover; it is only used
    to synthesize the stub when no drafted markdown exists yet.
    """

    slug: str
    label: str
    title: str
    outline: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Part:
    """A titled group of chapters, rendered as a heading in the sidebar."""

    title: str
    chapters: tuple[Chapter, ...]


PREFACE = Chapter(
    slug="preface",
    label="",
    title="Preface",
    outline=(),
)


BOOK: tuple[Part, ...] = (
    Part(
        title="I · The Language of Distributions",
        chapters=(
            Chapter(
                slug="what-this-book-is",
                label="1",
                title="What This Book Is About",
                outline=(
                    (
                        "One question, many disguises",
                        "Theoretical statistics as the study of how to learn from "
                        "data under uncertainty, and how to judge a procedure.",
                    ),
                    (
                        "The map of the field",
                        "Distributions, estimation, risk, and regularization as one "
                        "connected story, previewed.",
                    ),
                ),
            ),
            Chapter(
                slug="random-variables",
                label="2",
                title="Random Variables and Distributions",
                outline=(
                    (
                        "A distribution is a bookkeeping device",
                        "CDFs, densities, and mass functions as three views of the "
                        "same object.",
                    ),
                    (
                        "Joint, marginal, conditional",
                        "How distributions combine, and what independence buys.",
                    ),
                ),
            ),
            Chapter(
                slug="expectation-and-moments",
                label="3",
                title="Expectation, Moments, and Their Uses",
                outline=(
                    (
                        "Expectation as a weighted average",
                        "Linearity, and why it is the workhorse of the whole "
                        "subject.",
                    ),
                    (
                        "Moments and what they miss",
                        "Variance, higher moments, and the moment generating "
                        "function as a fingerprint.",
                    ),
                ),
            ),
            Chapter(
                slug="distribution-families",
                label="4",
                title="Families of Distributions",
                outline=(
                    (
                        "The exponential family",
                        "The unifying structure behind the familiar distributions, "
                        "and why it keeps appearing.",
                    ),
                    (
                        "Sufficiency, previewed",
                        "How the shape of a family tells you what to remember from "
                        "the data.",
                    ),
                ),
            ),
            Chapter(
                slug="convergence",
                label="5",
                title="Convergence and the Limit Theorems",
                outline=(
                    (
                        "Modes of convergence",
                        "In probability, almost surely, in distribution — what each "
                        "promises, sketched.",
                    ),
                    (
                        "The two theorems that run statistics",
                        "The law of large numbers and the central limit theorem, "
                        "and why the normal is everywhere.",
                    ),
                ),
            ),
        ),
    ),
    Part(
        title="II · Estimation",
        chapters=(
            Chapter(
                slug="what-makes-a-good-estimator",
                label="6",
                title="What Makes a Good Estimator",
                outline=(
                    (
                        "Bias, variance, and mean squared error",
                        "The three numbers that summarize an estimator, and how "
                        "they trade off.",
                    ),
                    (
                        "Consistency",
                        "The bare minimum: getting the right answer with enough "
                        "data.",
                    ),
                ),
            ),
            Chapter(
                slug="sufficiency-and-information",
                label="7",
                title="Sufficiency and Information",
                outline=(
                    (
                        "Sufficiency: what to keep",
                        "The statistic that loses nothing, and the factorization "
                        "that reveals it.",
                    ),
                    (
                        "Fisher information and the Cramér–Rao bound",
                        "How much a sample can tell you, and the floor on any "
                        "unbiased estimator's variance.",
                    ),
                ),
            ),
            Chapter(
                slug="maximum-likelihood",
                label="8",
                title="Maximum Likelihood",
                outline=(
                    (
                        "The likelihood as a scoreboard",
                        "Choosing the parameter that makes the data least "
                        "surprising.",
                    ),
                    (
                        "Why it usually works",
                        "Asymptotic efficiency, and the failure modes to respect.",
                    ),
                ),
            ),
            Chapter(
                slug="the-bayesian-view",
                label="9",
                title="The Bayesian View",
                outline=(
                    (
                        "Priors, posteriors, and updating",
                        "Treating the parameter as uncertain, and letting data move "
                        "belief.",
                    ),
                    (
                        "Conjugacy and its convenience",
                        "When the update stays in the family, and what that buys.",
                    ),
                ),
            ),
        ),
    ),
    Part(
        title="III · Loss, Risk, and Decisions",
        chapters=(
            Chapter(
                slug="loss-functions",
                label="10",
                title="Loss Functions: What You Are Rewarding",
                outline=(
                    (
                        "Squared, absolute, and beyond",
                        "How the loss you choose decides the estimator you get.",
                    ),
                    (
                        "Robustness and the shape of loss",
                        "Huber, quantile, and 0–1 loss, and what each forgives.",
                    ),
                ),
            ),
            Chapter(
                slug="risk-and-decision-theory",
                label="11",
                title="Risk and Decision Theory",
                outline=(
                    (
                        "Risk as expected loss",
                        "Judging a procedure before you see the data.",
                    ),
                    (
                        "Admissibility, minimax, and Bayes risk",
                        "Three lenses for calling one procedure better than "
                        "another.",
                    ),
                ),
            ),
            Chapter(
                slug="the-bias-variance-tradeoff",
                label="12",
                title="The Bias–Variance Tradeoff",
                outline=(
                    (
                        "Decomposing the error",
                        "How risk splits into bias squared plus variance, exactly.",
                    ),
                    (
                        "Why a little bias can help",
                        "The tradeoff, and the surprise that unbiased is rarely "
                        "optimal.",
                    ),
                ),
            ),
        ),
    ),
    Part(
        title="IV · Regularization and Shrinkage",
        chapters=(
            Chapter(
                slug="the-shrinkage-surprise",
                label="13",
                title="The Shrinkage Surprise",
                outline=(
                    (
                        "Stein's paradox",
                        "Why pulling estimates toward a center beats treating them "
                        "separately, in three or more dimensions.",
                    ),
                    (
                        "Borrowing strength",
                        "The intuition behind shrinkage that survives the shock.",
                    ),
                ),
            ),
            Chapter(
                slug="penalties-and-priors",
                label="14",
                title="Penalties and Priors",
                outline=(
                    (
                        "Ridge, lasso, and what they prefer",
                        "The two penalties, and the geometry that makes one sparse.",
                    ),
                    (
                        "Regularization is a prior",
                        "Penalized estimation as maximum a posteriori, made "
                        "concrete.",
                    ),
                ),
            ),
            Chapter(
                slug="choosing-the-penalty",
                label="15",
                title="Choosing the Penalty",
                outline=(
                    (
                        "Cross-validation and effective degrees of freedom",
                        "Letting the data pick how much to shrink.",
                    ),
                    (
                        "The regularization path",
                        "Watching the whole family of fits at once.",
                    ),
                ),
            ),
        ),
    ),
    Part(
        title="V · Testing and Inference",
        chapters=(
            Chapter(
                slug="hypothesis-testing",
                label="16",
                title="Hypothesis Testing",
                outline=(
                    (
                        "The Neyman–Pearson framing",
                        "Trading off two kinds of error, and the most powerful "
                        "test.",
                    ),
                    (
                        "The likelihood ratio",
                        "The statistic that keeps showing up, and why.",
                    ),
                ),
            ),
            Chapter(
                slug="p-values-power-and-errors",
                label="17",
                title="P-values, Power, and Errors",
                outline=(
                    (
                        "What a p-value is and is not",
                        "Reading it honestly, and the traps that follow.",
                    ),
                    (
                        "Power and sample size",
                        "The question you should ask before collecting data.",
                    ),
                ),
            ),
            Chapter(
                slug="intervals",
                label="18",
                title="Confidence and Credible Intervals",
                outline=(
                    (
                        "Two interval philosophies",
                        "What frequentist coverage promises, and what a credible "
                        "interval says instead.",
                    ),
                    (
                        "Duality with testing",
                        "Why an interval is a family of tests in disguise.",
                    ),
                ),
            ),
        ),
    ),
    Part(
        title="VI · Asymptotics and the Modern View",
        chapters=(
            Chapter(
                slug="asymptotic-efficiency",
                label="19",
                title="Asymptotic Efficiency",
                outline=(
                    (
                        "Large-sample behavior of the MLE",
                        "Why maximum likelihood is hard to beat as data grows, "
                        "sketched.",
                    ),
                    (
                        "The information floor, again",
                        "How the Cramér–Rao bound returns as an asymptotic ideal.",
                    ),
                ),
            ),
            Chapter(
                slug="the-bootstrap",
                label="20",
                title="The Bootstrap",
                outline=(
                    (
                        "Resampling to fake a sampling distribution",
                        "Using the data as its own population, and when that is "
                        "honest.",
                    ),
                    (
                        "What it can and cannot do",
                        "The failure cases worth respecting.",
                    ),
                ),
            ),
            Chapter(
                slug="high-dimensional-phenomena",
                label="21",
                title="High-Dimensional Phenomena",
                outline=(
                    (
                        "When p grows with n",
                        "How classical intuitions bend, and why regularization "
                        "becomes essential.",
                    ),
                    (
                        "A look at the frontier",
                        "Where the theory is still being written; the book's "
                        "conclusion.",
                    ),
                ),
            ),
        ),
    ),
)


APPENDICES: tuple[Chapter, ...] = (
    Chapter(
        slug="probability-refresher",
        label="A",
        title="A Probability Refresher",
        outline=(
            (
                "The probability you will lean on",
                "A compact reference for the distributions, expectations, and "
                "limit results the chapters assume.",
            ),
        ),
    ),
    Chapter(
        slug="glossary",
        label="B",
        title="Glossary",
        outline=(),
    ),
)


def all_pages() -> tuple[Chapter, ...]:
    """Return every page in reading order: preface, chapters, then appendices."""
    pages: list[Chapter] = [PREFACE]
    for part in BOOK:
        pages.extend(part.chapters)
    pages.extend(APPENDICES)
    slugs = [page.slug for page in pages]
    assert len(slugs) == len(
        set(slugs)
    ), "Duplicate slug detected in the table of contents."
    return tuple(pages)
