"""Single source of truth for the book's glossary.

The convention is: **every term or abbreviation is defined inline the first time
it appears in the prose, and also added here**. `build.py` renders the
`glossary` appendix from `GLOSSARY`, alphabetically.

Keep each definition to one or two plain sentences aimed at the book's reader —
enough to unblock them, not a textbook entry. Cross-reference other terms by
name rather than restating them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    """One glossary entry.

    `term` is shown as written (keep the canonical casing, e.g. "RNA-seq");
    sorting is case-insensitive. `definition` is one or two plain sentences.
    """

    term: str
    definition: str

    def __post_init__(self) -> None:
        assert self.term.strip(), "Glossary term is empty."
        assert self.definition.strip(), f"Term {self.term!r} has an empty definition."
        assert not self.term.startswith(" "), f"Term {self.term!r} has leading space."


_TERMS: tuple[Term, ...] = (
    Term(
        "Estimator",
        "A rule that turns a sample of data into a guess for an unknown quantity; because the data is random, the estimator is itself a random variable with a distribution.",
    ),
    Term(
        "Bias",
        "The systematic error of an estimator: how far its average value, over repeated samples, sits from the true quantity it targets.",
    ),
    Term(
        "Variance (of an estimator)",
        "How much an estimator's value bounces around from sample to sample; a measure of its instability, separate from whether it is centered correctly.",
    ),
    Term(
        "Mean squared error (MSE)",
        "The expected squared distance between an estimator and its target. Under squared-error loss it equals bias squared plus variance.",
    ),
    Term(
        "Loss function",
        "A rule assigning a penalty to being wrong by a given amount; the choice of loss decides which estimator counts as best.",
    ),
    Term(
        "Risk",
        "The expected loss of a procedure, averaged over the data it might see; the yardstick decision theory uses to compare procedures before the data arrives.",
    ),
    Term(
        "Regularization",
        "Deliberately biasing an estimate — usually by penalizing large or complex fits — to reduce its variance and lower total risk.",
    ),
    Term(
        "Shrinkage",
        "Pulling an estimate toward a fixed center (often zero) or toward other estimates; the mechanism behind ridge regression and Stein estimation.",
    ),
    Term(
        "Consistency",
        "The property that an estimator converges to the true quantity as the sample size grows without bound.",
    ),
)


def _sorted(terms: tuple[Term, ...]) -> tuple[Term, ...]:
    """Return terms sorted case-insensitively, failing on duplicates."""
    seen: set[str] = set()
    for term in terms:
        key = term.term.lower()
        assert key not in seen, f"Duplicate glossary term: {term.term!r}."
        seen.add(key)
    return tuple(sorted(terms, key=lambda t: t.term.lower()))


GLOSSARY: tuple[Term, ...] = _sorted(_TERMS)
