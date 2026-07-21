"""Single source of truth for the end-of-chapter "Check yourself" quizzes.

Each chapter closes with a short set of challenging multiple-choice questions.
`build.py` renders it automatically after the References; a small inline script
makes it interactive: the reader picks an option, the choice is marked right or
wrong, the correct answer is revealed, and an explanation appears.

The questions are meant to be *hard* in the way a sharp reviewer's question is
hard. The distractors are plausible misconceptions, stated with the same
confidence and detail as the answer, so that neither length nor specificity ever
signals which option is correct. The renderer shuffles the options on load, so
the position of the answer carries no information either — write the options in
any order and point `answer` at the right one. Each explanation carries a
second-layer detail the prose only gestures at, so the quiz teaches rather than
merely confirms.

Question strings are **plain text**. `build.py` HTML-escapes everything, which
would neutralize MathJax delimiters, so do not write `$...$` or `\\(...\\)`
here; phrase math in words or with plain symbols instead.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    """One multiple-choice question.

    `options` are shuffled at render time, so their order here does not matter;
    `answer` is the index (into this tuple) of the single correct option.
    `explanation` is revealed after the reader answers and should teach, not
    just confirm. Because the display order is randomized, never write an option
    that refers to another by position (e.g. "same as A").
    """

    prompt: str
    options: tuple[str, ...]
    answer: int
    explanation: str

    def __post_init__(self) -> None:
        assert self.prompt.strip(), "Question has an empty prompt."
        assert len(self.options) >= 3, f"{self.prompt!r}: need at least 3 options."
        assert all(o.strip() for o in self.options), f"{self.prompt!r}: empty option."
        assert (
            0 <= self.answer < len(self.options)
        ), f"{self.prompt!r}: answer index {self.answer} is out of range."
        assert self.explanation.strip(), f"{self.prompt!r}: empty explanation."


_QUIZZES: dict[str, tuple[Question, ...]] = {
    "the-bias-variance-tradeoff": (
        Question(
            prompt="Under squared-error loss, the mean squared error of an estimator of a fixed parameter decomposes into exactly two pieces. What are they?",
            options=(
                "Its squared bias plus its variance.",
                "Its bias plus its standard deviation.",
                "Its variance plus the noise variance of the data.",
                "Its squared bias plus the sample size.",
            ),
            answer=0,
            explanation="For squared-error loss, MSE = (bias)^2 + variance — a clean, exact identity, not an approximation, because the cross term in the expansion has expectation zero. Bias and standard deviation are in different units and cannot be added, and the irreducible noise term appears only when you predict a fresh noisy observation, not when you estimate a fixed parameter.",
        ),
        Question(
            prompt="A colleague insists on using only unbiased estimators. Why is that not automatically the right call?",
            options=(
                "A biased estimator can have strictly smaller mean squared error, since a little bias can buy a larger cut in variance.",
                "Unbiased estimators fail to exist for almost every parameter worth estimating.",
                "Unbiased estimators are always more expensive to compute than biased ones.",
                "Bias and variance measure the same quantity, so removing one removes the other.",
            ),
            answer=0,
            explanation="MSE trades bias against variance, and the minimum of their sum often sits at a nonzero bias. Pulling an estimate toward a center adds bias but can shrink variance by more, lowering total error — the whole reason regularization works. Unbiased estimators usually do exist; the point is that optimality is about total risk, not about zeroing the bias term.",
        ),
        Question(
            prompt="As you increase a regularization penalty (shrinking an estimate harder toward zero), what typically happens to bias and variance?",
            options=(
                "Bias grows while variance falls.",
                "Bias falls while variance grows.",
                "Both grow together.",
                "Both fall together.",
            ),
            answer=0,
            explanation="Heavier shrinkage pulls the estimate away from what the data alone would say, raising bias, while making the estimate less sensitive to the particular sample, lowering variance. Total risk is U-shaped in the penalty: too little regularization is all variance, too much is all bias, and the sweet spot lies in between.",
        ),
        Question(
            prompt="You observe z with mean beta and variance one, and estimate beta by z / (1 + lambda). The risk-minimizing penalty lambda* depends on what?",
            options=(
                "The noise variance relative to the size of beta squared.",
                "The sample size alone, with no dependence on beta whatsoever.",
                "The observed value z alone, chosen only after the data is seen.",
                "Nothing at all: lambda* is always zero because z is already unbiased.",
            ),
            answer=0,
            explanation="Minimizing risk gives lambda* = sigma^2 / beta^2: shrink harder when noise is large relative to signal, and less when the signal is strong. It is emphatically not always zero — that is the surprise, since lambda = 0 is the unbiased estimate z, yet a positive penalty lowers risk. And lambda* is a property of the problem, not something read off one observed z.",
        ),
        Question(
            prompt="'Variance' in the bias-variance decomposition refers to variability of what?",
            options=(
                "Of the estimator, across hypothetical repeated samples from the same population.",
                "Of the individual data points inside a single observed sample.",
                "Of the true parameter, which is being treated as a random quantity.",
                "Of the residuals that remain after the model is fit a single time.",
            ),
            answer=0,
            explanation="The variance term measures how much the estimator would bounce around if you redrew the data many times — a thought experiment over samples, not a spread visible inside one dataset. Confusing it with the within-sample spread of the data, or with one fit's residuals, is the usual slip; in the frequentist decomposition the parameter is fixed, not random.",
        ),
    ),
}


def _validate(
    quizzes: dict[str, tuple[Question, ...]],
) -> dict[str, tuple[Question, ...]]:
    """Assert each chapter has 4-6 questions."""
    for slug, questions in quizzes.items():
        assert (
            4 <= len(questions) <= 6
        ), f"Quiz for '{slug}' has {len(questions)} questions; expected 4-6."
    return quizzes


QUIZZES: dict[str, tuple[Question, ...]] = _validate(_QUIZZES)
