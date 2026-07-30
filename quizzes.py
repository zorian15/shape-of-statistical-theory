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
    "loss-functions": (
        Question(
            prompt="The best constant summary under absolute-error loss is the median rather than the mean. Which fact about expected absolute loss explains this?",
            options=(
                "Its derivative at c is P(Y < c) minus P(Y > c), which vanishes only where equal mass sits on either side of c.",
                "Its derivative at c is 2 times (c minus E[Y]), which vanishes exactly at the mean of Y and nowhere else.",
                "Absolute loss is not differentiable at zero, so no stationary point exists and the median is chosen only by convention.",
                "Its second derivative is a positive constant, so the loss is minimized at the arithmetic average of the sample values.",
            ),
            answer=0,
            explanation="Raising c helps for every point below it and hurts for every point above, so the slope is the difference of those two probabilities; it is zero when half the mass lies on each side, which is the definition of the median. The 2(c − E[Y]) slope is the one for squared error, and it lands on the mean.",
        ),
        Question(
            prompt="A single gross outlier is added to a fixed sample. What happens to the squared-error minimizer and the absolute-error minimizer?",
            options=(
                "Both shift toward the outlier by the same amount, since each loss is increasing in the size of the error.",
                "The mean moves toward the outlier without bound as it grows, while the median barely shifts at all.",
                "The median moves toward the outlier while the mean stays fixed, because absolute loss weights large errors more heavily.",
                "Neither moves, because one point cannot change a minimizer computed over the whole sample.",
            ),
            answer=1,
            explanation="Squared loss charges an outlier the square of its distance, so relieving that penalty drags the mean arbitrarily far; absolute loss charges only the distance, so the outlier gets a bounded vote and the median is essentially unmoved. This bounded influence is exactly what 'robustness' names.",
        ),
        Question(
            prompt="A colleague says squared-error loss produces a 'more accurate' estimate than absolute-error loss. What is the right correction?",
            options=(
                "Squared error is more accurate only for symmetric data, where the mean and median happen to coincide anyway.",
                "Absolute error is the more accurate of the two because it is robust to outliers in every distribution.",
                "Neither is more accurate; they optimize different targets, and squared loss merely penalizes large errors more, yielding the mean.",
                "Squared error is more accurate whenever the sample is large, since the mean is a consistent estimator.",
            ),
            answer=2,
            explanation="Calling one loss 'accurate' smuggles in an unstated cost structure. The two minimize different functionals — the mean and the median — and which you want depends on what your mistakes cost, not on any intrinsic accuracy ranking.",
        ),
        Question(
            prompt="Huber loss is quadratic for small residuals and linear for large ones. What does that shape buy?",
            options=(
                "Exact unbiasedness for any error distribution, which neither squared nor absolute loss can offer on its own.",
                "A closed-form minimizer that is always a fixed weighted average of the sample mean and the sample median.",
                "Full independence from its threshold, since the transition point has no effect on the resulting fit.",
                "Near-squared efficiency on the well-behaved bulk of the data, plus the outlier resistance of absolute loss in the tails.",
            ),
            answer=3,
            explanation="The quadratic core keeps the good small-error behavior of squared loss where the data is clean, and the linear tails cap an outlier's influence the way absolute loss does. The threshold is a genuine dial: sending it to infinity recovers squared error, to zero recovers absolute error.",
        ),
        Question(
            prompt="Pinball (quantile) loss with parameter tau = 0.9 does what?",
            options=(
                "Penalizes under-predictions nine times as steeply as over-predictions, so its minimizer is the 0.9 quantile.",
                "Penalizes over-predictions nine times as steeply as under-predictions, so its minimizer is the 0.1 quantile.",
                "Penalizes both directions equally but scaled by 0.9, so its minimizer is still the median of the data.",
                "Penalizes large errors quadratically and small errors linearly, so its minimizer is a trimmed mean.",
            ),
            answer=0,
            explanation="The slopes are tau and 1 − tau, so at tau = 0.9 the ratio is nine to one against under-prediction; the minimizer climbs until only ten percent of the mass lies above it — the 0.9 quantile. Sweeping tau from 0 to 1 traces the whole distribution one quantile at a time.",
        ),
        Question(
            prompt="Under 0–1 loss, the optimal constant summary of a distribution is its mode. Why the mode rather than the mean or median?",
            options=(
                "0–1 loss grows with the error size, so it rewards the value nearest to the bulk of the probability mass.",
                "0–1 loss is symmetric, so it selects the balance point of the distribution, which is the mean.",
                "0–1 loss counts only exact hits, so the best fixed guess is the single most probable value.",
                "0–1 loss integrates over the tails, so it favors the median as the most central choice.",
            ),
            answer=2,
            explanation="Because a near miss and a wild miss are charged identically, being close earns nothing; the only way to lower expected loss is to raise the chance of an exact hit, which means parking on the peak of the density. This is why classification uses the most-probable-class rule.",
        ),
    ),
    "risk-and-decision-theory": (
        Question(
            prompt=(
                "The risk of a decision rule is a function of what — that is, what "
                "does it assign a number to?"
            ),
            options=(
                "The unknown parameter: it gives one expected-loss value for each "
                "value the truth could take.",
                "The observed dataset: it gives the loss the rule actually incurred "
                "on the particular sample you drew.",
                "The estimate the rule produced, scored against the very data it was "
                "computed from.",
                "The prior distribution, averaging the rule's loss over your prior "
                "beliefs about the parameter.",
            ),
            answer=0,
            explanation=(
                "Risk fixes the truth at theta and averages the loss over the "
                "sampling distribution, so it returns one height per theta — a curve, "
                "not a number. The loss on the sample you drew (the second option) is "
                "the random quantity risk averages away; averaging risk against a "
                "prior (the fourth) gives the Bayes risk, a single number, which is a "
                "later step, not the risk itself."
            ),
        ),
        Question(
            prompt="A decision rule is inadmissible exactly when:",
            options=(
                "some other rule has risk no larger at every parameter value and "
                "strictly smaller at at least one value.",
                "some other rule has smaller risk at the single parameter value that "
                "happens to be the true one.",
                "its worst-case risk over the parameter is larger than that of some "
                "other available rule.",
                "its Bayes risk under the chosen prior exceeds the Bayes risk of the "
                "Bayes decision rule.",
            ),
            answer=0,
            explanation=(
                "Inadmissibility means being dominated: beaten weakly everywhere and "
                "strictly somewhere. The 'true value' option is a trap — you never "
                "know the true theta, so you cannot rank rules by their risk there. "
                "Losing on worst-case risk (minimax) or on Bayes risk (Bayes) is a "
                "different, weaker kind of loss and does not make a rule inadmissible."
            ),
        ),
        Question(
            prompt=(
                "Minimax rules frequently turn out to have constant risk across the "
                "whole parameter space. Why?"
            ),
            options=(
                "Leveling the curve removes any bulge an adversary could exploit, so "
                "the maximum is pushed as low as it can go.",
                "Constant risk is a requirement for admissibility, and every minimax "
                "rule is guaranteed to be admissible.",
                "A minimax rule discards the data by construction, so its risk simply "
                "cannot depend on the parameter.",
                "Averaging the risk against the least favorable prior mechanically "
                "forces the resulting curve to be horizontal.",
            ),
            answer=0,
            explanation=(
                "Minimizing the peak of a risk curve tends to flatten it — the "
                "'equalizer' intuition — because any point left bulging is a point the "
                "adversary aims at. The least-favorable-prior option is the tempting "
                "near-miss: a minimax rule often IS Bayes against that prior, but the "
                "averaging does not by itself force a flat curve; the equalizing "
                "pressure comes from minimizing the maximum."
            ),
        ),
        Question(
            prompt=(
                "You adopt squared-error loss and want the Bayes decision rule. For a "
                "given dataset, the action it outputs is:"
            ),
            options=(
                "the posterior mean, since the mean minimizes expected squared error "
                "under the posterior.",
                "the posterior median, since it splits the posterior probability into "
                "two equal halves.",
                "the posterior mode, the single most probable parameter value given "
                "the data.",
                "the maximum-likelihood estimate, since squared loss discards the "
                "prior entirely.",
            ),
            answer=0,
            explanation=(
                "Minimizing Bayes risk is the same as minimizing posterior expected "
                "loss dataset by dataset, and the loss selects the summary: squared "
                "error picks the mean, absolute error the median, and 0-1 loss the "
                "mode. The MLE option is wrong on two counts — the Bayes rule keeps "
                "the prior, and even a flat prior would give the posterior mean, not "
                "the mode the MLE tracks."
            ),
        ),
        Question(
            prompt=(
                "Two estimators have risk curves that cross. Which statement is "
                "correct?"
            ),
            options=(
                "Neither dominates the other, so which is 'better' depends on whether "
                "you judge by a minimax or a Bayes criterion.",
                "The one with lower risk at the true parameter dominates it, making "
                "that estimator the admissible choice.",
                "Whichever has the smaller worst-case risk dominates the other, by "
                "the definition of dominance.",
                "They must share the same Bayes risk under every prior, because their "
                "curves intersect somewhere.",
            ),
            answer=0,
            explanation=(
                "Crossing curves cannot be ordered by dominance, which is the whole "
                "reason minimax and Bayes exist as tie-breakers. Dominance requires "
                "one curve weakly below the other everywhere; a smaller worst case is "
                "a minimax judgment, not dominance; and intersecting curves can have "
                "wildly different Bayes risks depending on where the prior puts mass."
            ),
        ),
        Question(
            prompt=(
                "Under broad conditions, a minimax rule can be re-described in "
                "Bayesian terms as:"
            ),
            options=(
                "the Bayes decision rule for the least favorable prior, the prior "
                "that makes the smallest achievable Bayes risk as large as possible.",
                "the Bayes decision rule for a flat prior, which assigns every "
                "parameter value equal weight before the data.",
                "the rule achieving the lowest average risk taken across all priors "
                "one could possibly write down.",
                "the admissible rule whose entire risk curve lies below that of every "
                "other admissible rule.",
            ),
            answer=0,
            explanation=(
                "Minimax is Bayes aimed at the adversary's prior: the least "
                "favorable prior is the one maximizing the Bayes risk of its own "
                "Bayes rule, and that rule is minimax. A flat prior is a common but "
                "wrong guess (least favorable priors are rarely uniform), and the "
                "last option describes a rule that dominates all others — which, for "
                "crossing curves, cannot exist."
            ),
        ),
    ),
    "what-makes-a-good-estimator": (
        Question(
            prompt=(
                "You compute an estimate and it happens to equal the true parameter "
                "exactly. What does this tell you about the estimator you used?"
            ),
            options=(
                "Little on its own — a rule's quality lives in its sampling "
                "distribution, not in one lucky estimate.",
                "It proves the estimator is unbiased, since on this sample its output "
                "landed on the true parameter value.",
                "It proves the estimator is consistent, since hitting the truth shows "
                "its error is capable of reaching zero.",
                "It shows the estimator has low variance, since matching the target "
                "implies little spread around that target.",
            ),
            answer=0,
            explanation=(
                "Bias, variance, and consistency are all features of the rule's "
                "sampling distribution across every dataset it could see, not of one "
                "realized number. A single hit is consistent with a wildly biased or "
                "high-variance rule, just as a stopped clock is right twice a day."
            ),
        ),
        Question(
            prompt=(
                "For a normal population variance, dividing the sum of squared "
                "deviations by n minus 1 is unbiased, while dividing by n is biased. "
                "Which statement is correct?"
            ),
            options=(
                "The divide-by-n estimator has smaller mean squared error: the "
                "variance it saves outweighs the bias it adds.",
                "The divide-by-(n-1) estimator has smaller mean squared error, since "
                "eliminating bias is what minimizes total error.",
                "The two estimators have identical mean squared error, differing only "
                "by a factor that cancels in expectation.",
                "The comparison is undefined, because mean squared error is meaningful "
                "only for unbiased estimators.",
            ),
            answer=0,
            explanation=(
                "Because MSE is squared bias plus variance, the unbiased choice need "
                "not minimize it. Dividing by n lowers the variance term more than the "
                "bias term costs; pushing to n plus 1 minimizes MSE outright. MSE is "
                "defined for any estimator, biased or not."
            ),
        ),
        Question(
            prompt="In what sense can an unbiased estimator still be a poor choice?",
            options=(
                "It can carry enormous variance, so although it is right on average it "
                "lands far off on any single sample.",
                "It can be inconsistent, because unbiasedness keeps the distribution "
                "centered but stops it from ever narrowing.",
                "It can turn biased in large samples, since unbiasedness at finite n "
                "need not survive as n goes to infinity.",
                "It can ignore the model, because unbiased estimators are derived "
                "without any reference to the likelihood at all.",
            ),
            answer=0,
            explanation=(
                "Unbiasedness constrains only the center of the sampling distribution, "
                "not its spread, so an unbiased rule can be uselessly noisy. "
                "Unbiasedness neither forces nor forbids consistency, and it does not "
                "by itself decay with n — those distractors confuse independent "
                "properties."
            ),
        ),
        Question(
            prompt=(
                "Consider the rule 'estimate the population mean by reporting only the "
                "first observation and discarding the rest.' How does it behave?"
            ),
            options=(
                "Unbiased but inconsistent: its expectation equals the mean, yet its "
                "spread never shrinks as n grows.",
                "Consistent but biased: a lone draw underuses the data, though it still "
                "converges to the mean over time.",
                "Both unbiased and consistent, since each observation has the right "
                "mean and averaging only sharpens that.",
                "Neither unbiased nor consistent, since a single observation cannot "
                "match the population mean in expectation.",
            ),
            answer=0,
            explanation=(
                "A single draw has the population mean as its expectation, so the rule "
                "is unbiased; but it ignores the growing sample, so its variance never "
                "falls and it never concentrates on the truth. This is the cleanest "
                "proof that unbiasedness and consistency are independent."
            ),
        ),
        Question(
            prompt=(
                "An estimator is proven consistent. What does this guarantee about its "
                "performance at the sample size you actually have?"
            ),
            options=(
                "By itself nothing: consistency is a statement about the limit, and "
                "consistent rules can differ widely at finite n.",
                "That its bias vanishes at every finite sample size, which is precisely "
                "what convergence to the truth demands.",
                "That its standard error is already small, since consistency means the "
                "sampling distribution has concentrated.",
                "That it outperforms any inconsistent rival at that n, because "
                "convergence must dominate non-convergence.",
            ),
            answer=0,
            explanation=(
                "Consistency is an asymptotic promise: the distribution collapses onto "
                "the truth eventually, saying nothing about a fixed n. Two consistent "
                "estimators can concentrate at very different rates, which is why the "
                "1/sqrt(n) rate and its optimal constant (Chapters 7 and 19) are what "
                "actually separate good rules from merely-consistent ones."
            ),
        ),
    ),
    "sufficiency-and-information": (
        Question(
            prompt="What is the precise sense in which a statistic T is sufficient for a parameter theta?",
            options=(
                "Given the value of T, the conditional distribution of the raw data no longer depends on theta.",
                "T is an unbiased estimator of theta whose sampling variance exactly attains the Cramer-Rao information floor for the model at hand.",
                "T converges to the true value of theta as the sample size grows without bound.",
                "T is the function of the data that maximizes the likelihood for every theta.",
            ),
            answer=0,
            explanation="Sufficiency is a statement about a conditional distribution: once T is known, the leftover randomness in the data is generated by a mechanism that never consults theta, so nothing beyond T can help estimate it. This is a property of the statistic relative to a model, not a claim that T estimates, converges to, or maximizes anything.",
        ),
        Question(
            prompt="The Fisher-Neyman factorization writes the likelihood as g(T(x), theta) times h(x). Why can the factor h(x) be ignored when inferring theta?",
            options=(
                "Because it rescales every candidate theta by the same amount, so it cannot change which theta the data prefers.",
                "Because it is always equal to one for any distribution in the exponential family.",
                "Because it integrates to one over the data and therefore contributes nothing to the total probability.",
                "Because it is the part of the likelihood that the maximum likelihood estimator sets to zero.",
            ),
            answer=0,
            explanation="Since h(x) carries no theta, it multiplies the likelihood of every candidate parameter equally and drops out of any comparison or ratio. It is not generally one (for the Poisson it is 1/x!), and it is exactly where evidence against the model would hide, so 'ignore it' holds only for inference on theta inside an assumed model.",
        ),
        Question(
            prompt="Fisher information I(theta) is often described as the curvature of the log-likelihood at the truth. What does a small I(theta) tell you?",
            options=(
                "The log-likelihood is flat near the truth, so many parameters explain the data about equally well and precise estimation is hard.",
                "The estimator you chose must be biased, so its sampling distribution is centered far from the true parameter value no matter how much data you collect.",
                "The sample size is too small, a problem that vanishes once enough data is collected.",
                "The model has more than one parameter, so information leaks into the off-diagonal terms.",
            ),
            answer=0,
            explanation="Small curvature means a broad, gently sloping peak: the data barely distinguishes the best theta from its neighbors, so no unbiased estimator can be very precise. Low information is a property of the model's shape at theta, distinct from bias, and it is a per-observation quantity that total information n*I(theta) scales up with more data rather than being 'cured' by it.",
        ),
        Question(
            prompt="An estimator is reported with variance strictly below 1/(n I(theta)). What is the most likely explanation?",
            options=(
                "The estimator is biased, since the Cramer-Rao bound only floors the variance of unbiased estimators.",
                "The Fisher information was computed with the wrong sign of the second derivative.",
                "The estimator is inconsistent and its variance estimate cannot be trusted.",
                "The sample violated independence, so the information failed to add across observations.",
            ),
            answer=0,
            explanation="The Cramer-Rao bound is a floor for unbiased estimators only; biased rules routinely beat it by trading a little bias for a large drop in variance, which is exactly how shrinkage estimators win. Beating the bound is a signal that unbiasedness was given up on purpose, not evidence of an arithmetic or independence error.",
        ),
        Question(
            prompt="The maximum likelihood estimator usually does not attain the Cramer-Rao bound exactly at finite n. Why is the bound still central to how it is judged?",
            options=(
                "Because the MLE is asymptotically efficient: as n grows its variance approaches 1/(n I(theta)), making the bound its large-sample precision.",
                "Because the MLE is exactly unbiased at every sample size, so it sits on the bound by construction.",
                "Because the bound is achieved by the sample mean, which the MLE always equals.",
                "Because the bound guarantees the MLE has the strictly smallest variance among all estimators whatsoever, biased or unbiased, at every finite sample size and for every model.",
            ),
            answer=0,
            explanation="Under mild regularity the MLE's variance converges to the inverse information, so the floor that no one touches at finite n becomes the exact asymptotic variance of the estimator you were going to use. The MLE is generally biased at finite n, need not equal the sample mean, and the bound never constrains biased estimators, which can dip below it.",
        ),
        Question(
            prompt="The entire ordered sample is always a sufficient statistic. What does this reveal about sufficiency?",
            options=(
                "Sufficiency alone does not demand compression; you usually want the minimal sufficient statistic, the coarsest summary that still loses nothing.",
                "The ordered sample is the only sufficient statistic that exists for a general model.",
                "Sufficiency and minimality are one and the same property, so any statistic that is sufficient is already the maximally compressed summary, and hunting for a smaller one is wasted effort.",
                "It shows the exponential family is the only family with a sufficient statistic of fixed size.",
            ),
            answer=0,
            explanation="Keeping everything trivially loses no information, so sufficiency by itself is a weak requirement; the useful target is the minimal sufficient statistic, the maximal compression that stays sufficient. Many sufficient statistics coexist, minimality is a strictly stronger condition, and fixed-dimension sufficiency (the Pitman-Koopman-Darmois result) is a separate exponential-family fact.",
        ),
    ),
    "maximum-likelihood": (
        Question(
            prompt=(
                "You compute the maximum-likelihood estimate and the likelihood is "
                "very high there. What does that high likelihood value actually tell "
                "you?"
            ),
            options=(
                "That the data you observed would be relatively unsurprising under "
                "that parameter, and nothing more.",
                "That this parameter is very probably the true value that generated the data, a direct probability statement about theta itself.",
                "That this parameter has high posterior probability under a flat "
                "prior.",
                "That the estimate is unbiased and has reached the Cramér-Rao bound.",
            ),
            answer=0,
            explanation=(
                "The likelihood is a function of the parameter but a distribution over "
                "data, so a high value means the observed data was well anticipated, "
                "not that the parameter is probably true. The probability that theta "
                "lies somewhere, given the data, is the Bayesian posterior and needs a "
                "prior (Chapter 9). A flat prior does make the posterior proportional "
                "to the likelihood, but that is a separate, normalized object and the "
                "prior may not even be proper."
            ),
        ),
        Question(
            prompt=(
                "The maximum-likelihood estimator of a Normal's variance is the average "
                "squared deviation from the sample mean, dividing by n. Compared with "
                "the usual sample variance that divides by n minus one, the MLE:"
            ),
            options=(
                "systematically underestimates the variance, by a factor of (n-1)/n "
                "that shrinks as n grows.",
                "overestimates the variance because it reuses the sample mean inside "
                "the deviations.",
                "is unbiased, because maximum likelihood always targets unbiased "
                "estimates.",
                "has larger variance but exactly the same expected value as the n "
                "minus one version.",
            ),
            answer=0,
            explanation=(
                "Because the sample mean is fit from the same data, the squared "
                "deviations are a touch too small and the expectation is (n-1)/n times "
                "the true variance — biased low, worst at small n. Maximum likelihood "
                "optimizes likelihood, not unbiasedness, which is why the n minus one "
                "divisor is used when unbiasedness is wanted. The bias vanishes as n "
                "grows, which is consistency."
            ),
        ),
        Question(
            prompt=(
                "Under regularity conditions, in what precise sense is the MLE hard to "
                "beat as the sample grows?"
            ),
            options=(
                "Its sampling distribution approaches a Normal centered at the truth "
                "whose variance meets the Cramer-Rao floor.",
                "Its bias reaches zero faster than any other estimator's at every "
                "finite sample size.",
                "It has the smallest mean squared error of any estimator at every "
                "sample size.",
                "It converges to the truth faster than the law of large numbers allows "
                "for an average.",
            ),
            answer=0,
            explanation=(
                "Asymptotic efficiency is a large-sample statement: the MLE becomes "
                "approximately Normal around the truth with variance 1/(n I), the "
                "lowest an unbiased estimator can reach. It is not a finite-sample "
                "claim — a biased estimator can have smaller mean squared error at a "
                "given n (Chapters 12 and 13) — and the rate is the ordinary 1/sqrt(n) "
                "of the central limit theorem, not faster."
            ),
        ),
        Question(
            prompt=(
                "For the uniform distribution on the interval from 0 to theta, setting "
                "the derivative of the log-likelihood to zero fails to locate the MLE. "
                "Why, and what is the MLE?"
            ),
            options=(
                "The support depends on theta, so the likelihood peaks at a boundary "
                "corner; the MLE is the sample maximum.",
                "The log-likelihood is not concave in theta, so the score equation "
                "returns a spurious minimum instead of a maximum and its sign must be "
                "flipped to locate the peak.",
                "The likelihood is flat in theta, so every positive parameter is an "
                "equally good estimate.",
                "The Fisher information is infinite, so the score is undefined and no "
                "MLE exists at all.",
            ),
            answer=0,
            explanation=(
                "The density is positive only for theta at least as large as every "
                "observation, so the likelihood rises to a corner at the sample maximum "
                "and is cut off below it — the derivative is never zero there. This "
                "violates the regularity condition that the support not move with the "
                "parameter, so the MLE is max of the observations, and its distribution "
                "is skewed and biased rather than Normal."
            ),
        ),
        Question(
            prompt=(
                "You fit a model by maximum likelihood, but the true data-generating "
                "distribution is not a member of your model family. As n grows, the "
                "MLE converges to:"
            ),
            options=(
                "the parameter whose model is closest to the truth in Kullback-Leibler "
                "divergence.",
                "the true distribution's parameters, since consistency guarantees "
                "reaching the truth.",
                "no fixed value; the estimate keeps drifting and never settles as data "
                "accumulates.",
                "the parameter that minimizes squared error between the model and the "
                "observed data.",
            ),
            answer=0,
            explanation=(
                "With the truth outside the family there is no true theta to reach, so "
                "the MLE settles on the pseudo-true value: the model in the family that "
                "is nearest the truth in KL divergence. Consistency assumed a "
                "correctly specified model, so it does not apply. The danger is that "
                "this projection comes with confident-looking error bars for a model "
                "that may not represent the data at all."
            ),
        ),
    ),
    "the-bayesian-view": (
        Question(
            prompt="In the full statement of Bayes' rule, the denominator is the marginal likelihood p(x), the probability of the data averaged over the prior. What is its role in shaping the posterior?",
            options=(
                "It is a constant in the parameter, renormalizing the product so the posterior integrates to one; the shape is set by prior times likelihood.",
                "It reweights the prior toward the parameter values the data supports, and is what actually moves belief from the prior to the posterior.",
                "It rescales the posterior's height so that a larger evidence produces a sharper, more confident posterior distribution.",
                "It carries the likelihood's contribution, so discarding it would leave the posterior proportional to the prior alone.",
            ),
            answer=0,
            explanation="The evidence does not depend on the parameter, so it cannot reweight one value against another or 'move' belief — that work is done entirely by the numerator, prior times likelihood. It is a pure normalizing constant. Its one further use is across models rather than within one: comparing the evidence of competing models is the basis of Bayes factors.",
        ),
        Question(
            prompt="You report a 95% credible interval for a parameter. How does its meaning differ from a 95% confidence interval?",
            options=(
                "The credible interval places 95% posterior probability on the parameter being inside; the confidence interval's 95% describes the procedure's long-run coverage, not this interval.",
                "They are the same idea computed two ways, so the distinction is purely philosophical and never changes the numbers you report.",
                "The credible interval is always the wider of the two, because folding in a prior necessarily adds extra uncertainty to the estimate.",
                "The confidence interval is the one making a direct probability claim about where the fixed parameter lies, while the credible interval merely describes the long-run behavior of the sampling procedure across repeats.",
            ),
            answer=0,
            explanation="The guarantees live in different places: the credible interval's probability is about the parameter given your posterior, while the confidence interval's is about the method across repeated samples and says nothing about whether this particular interval traps the truth. The last option swaps the two, the classic misreading Chapter 18 is built to prevent. Numerically they can even coincide while meaning different things.",
        ),
        Question(
            prompt="A Beta prior on a rate meets Bernoulli data and yields a Beta posterior; a Gamma prior on a Poisson rate stays Gamma. Why do such conjugate pairs exist so reliably?",
            options=(
                "Each likelihood is an exponential family, and its conjugate prior is built so that updating adds the data's sufficient statistic to the prior's pseudo-counts, keeping the family.",
                "The prior and likelihood merely happen to share the same functional form by lucky coincidence, which is exactly why conjugacy works only for a short, memorized list of special named pairs and never generalizes beyond them.",
                "Conjugacy holds whenever the prior is uninformative, since a flat prior cannot change the shape of the likelihood that it multiplies.",
                "The posterior stays in the family because the evidence integral is finite, which forces the normalized product back into the prior's form.",
            ),
            answer=0,
            explanation="Conjugacy is the exponential-family structure of Chapter 4 seen in Bayesian dress: because the parameter meets the data only through a sufficient statistic in the exponent, updating just increments the prior's counts. It has nothing to do with the prior being flat, and it is a structural guarantee, not a lucky coincidence for a handful of named pairs.",
        ),
        Question(
            prompt="Under a flat prior, the MAP estimate coincides with the maximum-likelihood estimate. Does that make Bayesian inference just maximum likelihood with extra bookkeeping?",
            options=(
                "No; the Bayesian keeps the whole posterior — its spread is calibrated uncertainty and its mean can differ from the mode, which a single point discards.",
                "Yes; with a flat prior the two estimates agree exactly, so the entire posterior distribution holds no information whatsoever beyond the single maximum-likelihood point estimate you already had.",
                "No; the MAP and the MLE in fact disagree even under a flat prior, because the mode is computed on a rescaled version of the likelihood.",
                "Yes; the posterior is guaranteed symmetric about the MLE, so quoting the mode conveys exactly what the full posterior would.",
            ),
            answer=0,
            explanation="Matching the MLE at the peak is not the same as carrying no more information: the posterior's whole shape is the uncertainty, the mean parts from the mode whenever it is skewed, and 'flat' is not innocent — it can be improper and is not invariant to reparameterization. The MAP and MLE do coincide under a flat prior, so the option claiming they disagree is simply wrong.",
        ),
        Question(
            prompt="An analyst uses a prior that is uniform on [0, 0.5] for a coin's bias p, then collects flips that are overwhelmingly heads. What does the posterior conclude?",
            options=(
                "It never puts any probability above 0.5, because the prior gave that region zero density and Bayes' rule multiplies, so no data can revive it.",
                "It shifts smoothly past 0.5 toward the observed proportion, since a large enough sample always overwhelms whatever prior you started with.",
                "It concentrates exactly at 0.5, the largest value the prior permitted, with a variance that shrinks to zero as more flips arrive.",
                "It becomes undefined, because the data contradict the prior and the evidence integral in the denominator diverges to infinity.",
            ),
            answer=0,
            explanation="A prior is a statement about what is possible, not merely likely: multiplying a region by zero leaves it zero forever, so the posterior piles up against the 0.5 boundary but can never cross it, no matter how lopsided the flips. The 'data always washes out the prior' rule holds only when the prior grants the truth positive probability, which this one refuses to do.",
        ),
        Question(
            prompt="With a Beta(alpha, beta) prior and n = s + f observed trials, the posterior mean is a weighted average of the prior mean and the data proportion. What plays the role of the prior's weight?",
            options=(
                "The quantity alpha + beta, a prior sample size that the data outvotes once n grows past it.",
                "The number of observed successes s, so that a longer run of successes makes the prior count for more.",
                "The posterior variance, which grows with the data and thereby increases the prior's pull on the mean.",
                "The ratio s over f of successes to failures, which fixes how strongly the prior is weighted.",
            ),
            answer=0,
            explanation="The posterior mean weights the prior mean by (alpha + beta) / (alpha + beta + n) and the data proportion by n / (alpha + beta + n), so alpha + beta behaves like a count of imagined prior trials. Real data overrules it as soon as n exceeds it — the exact sense in which belief starts near the prior and ends near the data.",
        ),
    ),
    "what-this-book-is": (
        Question(
            prompt="The chapter calls theoretical statistics 'one question in many disguises.' Which pairing best captures the two moves it says the subject is built from?",
            options=(
                "Turning data into a guess or decision, and judging the rule used before any data is seen.",
                "Collecting a large enough sample, and then computing the correct summary statistic from it.",
                "Choosing the right named test, and reporting the p-value it produces.",
                "Estimating a parameter, and then testing whether that estimate is statistically significant.",
            ),
            answer=0,
            explanation="The first move is inference (data to a guess); the second, and the one that makes it a theory, is evaluating the procedure over its sampling distribution — before the data arrives. Testing and significance are one application, not the whole subject, and the second move is about grading the rule, not the single estimate it happened to output.",
        ),
        Question(
            prompt="Why does the book insist on reasoning about samples that never actually occurred?",
            options=(
                "Because the quality of a procedure is a property of the rule across all samples it could produce, not of the one dataset you saw.",
                "Because a larger set of imagined samples always reduces the bias of the estimate you report.",
                "Because the true parameter is itself a random quantity, so averaging a statistic over many hypothetical samples is precisely how you estimate the parameter's own distribution.",
                "Because without simulated extra samples you cannot compute an estimate from real data at all.",
            ),
            answer=0,
            explanation="'This estimate equals 53' says nothing about whether the method is good — a broken clock also emits a number. Guarantees like accuracy and precision live in what the rule would do across the samples the model allows. In the frequentist reading the parameter is fixed, not random; treating it as random is the Bayesian stance, a different framing.",
        ),
        Question(
            prompt="The chapter frames the six parts as a single chain in which each link is forced by the previous one. What forces the move from estimation to loss and risk?",
            options=(
                "To say which of two estimators is better, you need a way to score being wrong and average that score, which estimation alone does not supply.",
                "Estimation can only handle one parameter at a time, so risk is introduced to handle many parameters jointly.",
                "Estimators are always biased, so risk is needed as a separate correction applied after estimating.",
                "Loss and risk replace estimation once the sample size is large, because asymptotics take over.",
            ),
            answer=0,
            explanation="'Good' cannot be settled inside estimation: comparing guesses requires a loss function and its expectation, the risk. That scoreboard is also what later reveals the bias-variance surprise. Risk is not a patch applied after estimating, nor a large-sample replacement for it — it is the yardstick that makes 'better' meaningful.",
        ),
        Question(
            prompt="A statistical model, as the chapter defines it, is best described as which of the following?",
            options=(
                "A family of probability distributions, one per possible parameter value, that you are willing to treat as how the data was produced.",
                "The single distribution that actually generated the observed data, discovered by fitting.",
                "The estimator you choose to summarize the data into a parameter guess.",
                "A guarantee that the assumptions behind a chosen method are satisfied by the data.",
            ),
            answer=0,
            explanation="A model is a whole family of candidate distributions indexed by the parameter — a menu the world is assumed to have chosen from, not a proven fact. It is an assumption you adopt, distinct from the estimator that maps data to a guess; and adopting it guarantees nothing about whether it is adequate, which is exactly why checking it matters.",
        ),
        Question(
            prompt="The chapter argues you should learn the theory rather than memorize a table of named tests. What is the deeper of the two reasons it gives?",
            options=(
                "The theory lets you derive a method for a situation no existing recipe fits, because every recipe is the same risk question answered for a particular model and loss.",
                "The theory proves that named tests are usually wrong, so they should be avoided in practice.",
                "The theory is faster to apply than looking a method up in a reference table.",
                "The theory removes any need to state your modeling assumptions, because minimizing risk automatically discovers whatever assumptions a given situation requires and quietly handles them for you.",
            ),
            answer=0,
            explanation="Beyond telling you when a method is valid (the first reason), the theory reveals that maximum likelihood, ridge, the bootstrap, and the rest are one question — least risk under a model and loss — solved under different assumptions, so you can build the method you need. It does not make assumptions disappear; it makes them visible, which is what keeps you from misusing a recipe.",
        ),
    ),
    "random-variables": (
        Question(
            prompt="For a continuous random variable, what does the value f(x) of the density at a point x actually represent?",
            options=(
                "A probability per unit length near x, which can exceed one; only its integral over a set is a probability.",
                "The probability that the variable equals x exactly, which is why f must stay between zero and one.",
                "The probability that the variable falls at or below x, accumulated from the left tail.",
                "The fraction of a large sample expected to land exactly on the value x, on average.",
            ),
            answer=0,
            explanation="A density is a rate — probability per unit of x — so its height is not capped at one and can be large where probability is concentrated (a Beta(2,2) density crests at 1.5). Probability comes only from area, the integral over an interval. The chance of any single exact value is zero for a continuous variable, and the running total 'at or below x' is the CDF, not the density.",
        ),
        Question(
            prompt="Which object is guaranteed to exist and fully describe the distribution of any random variable, whether it is continuous, discrete, or a mixture of both?",
            options=(
                "The cumulative distribution function, a nondecreasing function running from zero to one.",
                "The probability density function, obtained by differentiating the distribution everywhere.",
                "The probability mass function, assigning a lump of probability to each attainable value.",
                "The moment generating function, which encodes the distribution through its derivatives at zero.",
            ),
            answer=0,
            explanation="Only the CDF F(x) = P(X <= x) is universal: it exists for every distribution and characterizes it. A density requires the CDF to be differentiable (continuous case); a mass function requires the variable to be discrete; and a moment generating function need not even exist (some distributions have no finite moments). The CDF is the odometer that always reads out.",
        ),
        Question(
            prompt="You have the joint density of X and Y. How do you obtain the marginal density of X, and what does it discard?",
            options=(
                "Integrate the joint over y; this discards all information about how X and Y depend on each other.",
                "Fix Y at its mean and read the resulting slice; this discards the variability of Y around that mean.",
                "Divide the joint by the density of Y; this discards the overall scale of the distribution.",
                "Evaluate the joint along the line y equals x; this discards the off-diagonal part of the density.",
            ),
            answer=0,
            explanation="Marginalizing sums out the other variable — f_X(x) = integral of f(x,y) dy — which projects the joint landscape onto the x axis as its shadow. What vanishes is the dependence structure: correlation and every finer coupling live only in the joint, so two very different joints can share identical marginals. Dividing by f_Y(y) gives a conditional, not a marginal.",
        ),
        Question(
            prompt="Two random variables are independent exactly when which condition holds?",
            options=(
                "Their joint density factors into the product of their two marginal densities for all values.",
                "Their correlation coefficient is zero, so no linear relationship ties them together.",
                "Their joint density is symmetric under swapping the roles of the two variables.",
                "Knowing the sum of the two variables reveals nothing about either one separately.",
            ),
            answer=0,
            explanation="Independence is the factorization f(x,y) = f_X(x) f_Y(y), equivalently every conditional equals the matching marginal. Zero correlation is strictly weaker — it rules out only linear tilt, and uncorrelated-but-dependent variables are easy to build (put mass on a symmetric ring). Symmetry under swapping is 'exchangeable,' a different property, and knowing the sum generally does constrain each part.",
        ),
        Question(
            prompt="Why does assuming your data points are independent and identically distributed matter so much for the machinery of later chapters?",
            options=(
                "The joint density becomes a product, so the log-likelihood becomes a sum — the form maximum likelihood and the limit theorems require.",
                "It guarantees each data point is drawn without replacement, so the sample exactly reproduces the population.",
                "It forces every marginal distribution to be normal, which is what the central limit theorem assumes as input.",
                "It makes the CDF differentiable, so a density exists and expectations can be computed by integration.",
            ),
            answer=0,
            explanation="Under i.i.d. sampling the joint factors into a product of identical densities, so taking logs turns it into a sum of terms — exactly what maximum likelihood maximizes and what the law of large numbers and central limit theorem average over. The CLT constrains the sum's limit, not the marginals' shape (they need not be normal), and i.i.d. describes sampling with replacement from a fixed distribution, not a census of the population.",
        ),
    ),
    "expectation-and-moments": (
        Question(
            prompt="You want the expected value of X + Y, where X and Y are strongly correlated. What does linearity of expectation let you do?",
            options=(
                "Add E[X] and E[Y] directly, because the identity holds regardless of any dependence between the two.",
                "Add E[X] and E[Y], but only after checking that X and Y are uncorrelated first.",
                "Add E[X] and E[Y], then adjust the total by their covariance term.",
                "Nothing shortcuts it: with dependence you must work from the joint law of X + Y.",
            ),
            answer=0,
            explanation="Linearity of expectation asks nothing of the joint distribution — the expectation of a sum reads only off each variable's marginal, which dependence leaves untouched. The covariance correction belongs to the variance of a sum, not its mean; that is the one squaring makes sensitive to dependence.",
        ),
        Question(
            prompt="For a standard Cauchy distribution, how does the sample mean of a large dataset behave as the sample size grows?",
            options=(
                "It never settles down, because the Cauchy has no finite mean for the law of large numbers to converge to.",
                "It converges to zero, the Cauchy's center of symmetry, only more slowly than the sample mean of well-behaved normal data would settle onto its own center.",
                "It converges to the true mean once the sample size exceeds the distribution's degrees of freedom.",
                "It converges to the median, since mean and median always coincide for a symmetric law.",
            ),
            answer=0,
            explanation="The Cauchy's tails are heavy enough that the integral defining E[X] diverges, so no mean exists and the law of large numbers has no target — the sample mean of Cauchy data is itself Cauchy, no matter how large n is. Symmetry supplies a center of symmetry but not a finite expectation.",
        ),
        Question(
            prompt="Two distributions share the same mean and the same variance, but one has visibly heavier tails. Which moment first tells them apart?",
            options=(
                "The fourth central moment, kurtosis, which gauges how much of the variance comes from extreme deviations.",
                "The third central moment, skewness, which gauges the asymmetry between the two tails.",
                "The second central moment, variance, once it is rescaled to strip out the units.",
                "The first moment, the mean, once it is recomputed using only the tail observations.",
            ),
            answer=0,
            explanation="Tail weight is the province of the fourth central moment; both distributions could be symmetric, so skewness may be zero for each and distinguish nothing. Variance is equal by assumption, and the mean says nothing about shape — reading moments in order zooms from location to spread to lean to tails.",
        ),
        Question(
            prompt="Why is the moment generating function the natural tool for finding the distribution of a sum of independent variables?",
            options=(
                "It turns the convolution of their densities into a plain product of MGFs, which you match to a known fingerprint.",
                "It replaces the sum with whichever of the two variables happens to be larger, whose MGF then dominates and stands in for the product of the two.",
                "It averages the two densities, and the MGF of that average identifies the sum.",
                "It differentiates the joint density, converting the convolution into an easy derivative.",
            ),
            answer=0,
            explanation="For independent variables M_{X+Y}(t) = M_X(t) M_Y(t), so the convolution that combines densities becomes ordinary multiplication. Because an MGF (where it exists) determines the law uniquely, you recognize the product as a known distribution's fingerprint and read off the answer.",
        ),
        Question(
            prompt="A distribution has finite moments of every order. Must it then have a moment generating function in an interval around zero?",
            options=(
                "No — the lognormal has all of its moments finite yet its MGF diverges for every positive argument.",
                "Yes — having all moments finite is exactly the condition that makes the MGF converge.",
                "Yes, as long as the distribution is also symmetric about its mean.",
                "No, unless the distribution additionally has bounded support.",
            ),
            answer=0,
            explanation="Having every moment finite is strictly weaker than having an MGF: the MGF needs the whole moment series to sum, which demands roughly exponential tails, and the lognormal's moments grow too fast for that. This is why the uniqueness guarantee is stated for the MGF or characteristic function, not for the raw moment sequence.",
        ),
        Question(
            prompt="For which of these identities is independence (or at least zero correlation) genuinely required, rather than optional?",
            options=(
                "Var(X + Y) = Var(X) + Var(Y).",
                "E[X + Y] = E[X] + E[Y].",
                "E[aX] = a E[X] for a constant a.",
                "E[X] exists whenever X has finitely many possible values.",
            ),
            answer=0,
            explanation="The variance of a sum carries a covariance cross term that vanishes only when the two are uncorrelated. The expectation identities hold unconditionally, which is exactly the asymmetry the chapter dwells on: the mean is linear across dependent variables, but the variance is not.",
        ),
    ),
    "distribution-families": (
        Question(
            prompt=(
                "What is the defining structural feature that makes a family of "
                "distributions an exponential family?"
            ),
            options=(
                "The parameter touches the data only through the dot product of a "
                "natural parameter and a sufficient statistic, inside one "
                "exponential with fixed support.",
                "The density decays like e to the minus x out in both of its tails, "
                "giving it exponentially light tails and therefore guaranteeing that "
                "moments of every single order stay finite.",
                "The density factors into a piece that depends only on x times a "
                "piece that is a polynomial in the parameter theta.",
                "The moment-generating function coincides with the density itself, "
                "up to a normalizing constant that depends on the parameter.",
            ),
            answer=0,
            explanation=(
                "Exponential family is about algebraic form, not tail behavior: "
                "p(x | theta) = h(x) exp(eta(theta) . T(x) - A(theta)), with x "
                "entering only through T(x) linearly in eta. The tempting trap is to "
                "confuse the exponential *family* with the exponential *distribution* "
                "or with exponentially light tails, a different idea entirely; the "
                "Gaussian, Poisson, and beta are all in the family despite very "
                "different tails."
            ),
        ),
        Question(
            prompt=(
                "You draw an independent, identically distributed sample of size n "
                "from an exponential family. What is enough to keep about the sample "
                "to lose nothing about theta?"
            ),
            options=(
                "The sum of T over the sample, together with n; the individual "
                "values and their order can be thrown away.",
                "The full ordered sample, because collapsing it to a sum discards "
                "information the parameter needs about the tails.",
                "The sample mean and the sample variance, which suffice for any "
                "family whatsoever.",
                "The largest and smallest observations, which together bracket where "
                "the parameter can lie.",
            ),
            answer=0,
            explanation=(
                "Multiplying the densities makes the exponents add, so theta appears "
                "only alongside the single quantity sum of T(x_i): that sum (with n) "
                "is sufficient. Its dimension is fixed no matter how large n grows, "
                "which is the rare and precious property the exponential form "
                "guarantees. Keeping the sample mean and variance is only sufficient "
                "for special families such as the Gaussian, not in general."
            ),
        ),
        Question(
            prompt="Why is the uniform distribution on [0, theta] not an exponential family?",
            options=(
                "Its support, the set where the density is positive, moves with "
                "theta, and no fixed function h(x) of the data alone can encode a "
                "boundary that depends on the parameter.",
                "It has no finite mean, so the log-partition function A(theta) "
                "diverges and cannot normalize the density.",
                "Its density fails to be a smooth function of theta at the upper "
                "boundary, and exponential families require smooth dependence.",
                "Its density is flat rather than curved, and an exponential family "
                "must place unequal probability across its support.",
            ),
            answer=0,
            explanation=(
                "The disqualifier is the moving support: 1{0 <= x <= theta} ties the "
                "positive region to theta, which the template forbids because h "
                "depends on x alone and A on theta alone. The 'no finite mean' option "
                "is a real fact about a *different* outsider, the Cauchy, planted "
                "here as a tempting cross-trap; the uniform has perfectly finite "
                "moments and still fails, for the support reason."
            ),
        ),
        Question(
            prompt=(
                "The uniform on [0, theta] has the maximum of the sample as a "
                "one-dimensional sufficient statistic, yet it is not an exponential "
                "family. What does this establish?"
            ),
            options=(
                "Having a low-dimensional sufficient statistic does not by itself "
                "make a family exponential; the exponential guarantee also needs the "
                "support to stay fixed as the parameter varies.",
                "Sufficiency and exponential-family membership are equivalent, so the "
                "uniform must in fact be an exponential family in disguise.",
                "The maximum is not genuinely sufficient here, since it ignores what "
                "the smaller observations say about theta.",
                "Exponential families are the only distributions that possess any "
                "sufficient statistic at all, so the uniform is the exception that "
                "proves the rule.",
            ),
            answer=0,
            explanation=(
                "Sufficiency alone is not the signature. The Pitman-Koopman-Darmois "
                "result gives exponential families a fixed-dimension sufficient "
                "statistic only *among families with fixed support*; drop that "
                "condition, as the uniform does, and you can still have a tidy "
                "sufficient statistic (the maximum) without being in the family. "
                "Fixed support is doing real work in the theorem."
            ),
        ),
        Question(
            prompt=(
                "In the natural parameterization of an exponential family, how do you "
                "recover the mean of the sufficient statistic, E[T(X)]?"
            ),
            options=(
                "Differentiate the log-partition function A once with respect to the "
                "natural parameter eta.",
                "Take the reciprocal of the second derivative of A with respect to "
                "the natural parameter eta, whose curvature you then invert to reach "
                "the mean.",
                "Find the value of eta at which A attains its maximum.",
                "Integrate the base measure h(x) over the whole support.",
            ),
            answer=0,
            explanation=(
                "The log-partition function stores the cumulants: the first "
                "derivative of A gives E[T(X)] and the second gives Var(T(X)). That "
                "is why moments in an exponential family are a matter of "
                "differentiation rather than integration, and it is the same duality "
                "that powers modern variational inference."
            ),
        ),
        Question(
            prompt=(
                "For an exponential family, the maximum-likelihood estimate of the "
                "parameter is characterized by which condition?"
            ),
            options=(
                "The model's expected sufficient statistic equals the sample average "
                "of that statistic: E_theta[T(X)] = (1/n) sum of T(x_i).",
                "The base measure h(x) is maximized at the observed data points.",
                "The natural parameter eta is chosen to make the log-partition "
                "function A(eta) as small as possible.",
                "The sample mean is driven to zero once the data have been centered "
                "at the parameter.",
            ),
            answer=0,
            explanation=(
                "Setting the derivative of the log-likelihood to zero and using that "
                "A' = E_theta[T] turns fitting into moment-matching: pick the theta "
                "whose model average of T matches the data's average of T. The "
                "sufficient statistic is exactly the quantity both sides compare, "
                "tying maximum likelihood back to sufficiency."
            ),
        ),
    ),
    "convergence": (
        Question(
            prompt="Which chain correctly orders the three modes of convergence from strongest to weakest?",
            options=(
                "Almost sure implies in probability implies in distribution.",
                "In distribution implies in probability implies almost sure.",
                "In probability implies almost sure implies in distribution.",
                "Almost sure implies in distribution implies in probability.",
            ),
            answer=0,
            explanation=(
                "The modes nest strongest to weakest, and the arrows run one way only. "
                "A sequence can converge in distribution without settling on any value, "
                "and in probability without its path ever quieting. The one partial "
                "converse is that convergence in distribution to a constant implies "
                "convergence in probability to it."
            ),
        ),
        Question(
            prompt="A researcher averages 10,000 draws from a strongly right-skewed distribution and is puzzled that the histogram of the raw observations is still skewed. What is the error?",
            options=(
                "They expected the raw data to become normal, but the CLT concerns the sampling distribution of the mean, not the observations.",
                "They used too few observations; by 10,000 the raw data should look visibly normal.",
                "They should have standardized each observation before building the histogram.",
                "Strongly skewed distributions fall outside the CLT, so no normality is promised at all.",
            ),
            answer=0,
            explanation=(
                "The CLT is a statement about the standardized mean, not the raw draws. "
                "The observations keep their skew forever no matter how many you collect; "
                "it is the sampling distribution of the average that turns normal."
            ),
        ),
        Question(
            prompt="Two analysts use the normal approximation for a sample mean at n = 30. One's source is mildly skewed, the other's severely skewed. What does the CLT actually guarantee?",
            options=(
                "Convergence to normality for both, but at different speeds, so n = 30 may suffice for one and badly fail the other.",
                "Normality at n = 30 for both, since 30 is the threshold the theorem establishes.",
                "Normality only for the mildly skewed source; severe skew violates the hypotheses.",
                "Nothing at any finite n; the approximation is meaningless until n is infinite.",
            ),
            answer=0,
            explanation=(
                "The theorem promises convergence, not a speed. How fast the sampling "
                "distribution becomes normal depends on the source, so 'n = 30' is a folk "
                "rule of thumb, not a theorem — a heavy skew can need hundreds of samples."
            ),
        ),
        Question(
            prompt="Why does the central limit theorem fail for independent draws from a Cauchy distribution?",
            options=(
                "Its variance is infinite, so the root-n rescaling is wrong and the sample mean never concentrates.",
                "Its draws are not independent, which violates the theorem's core assumption.",
                "Its mean is infinite, so there is no fixed target for the average to converge to.",
                "The theorem still holds, but convergence is too slow to observe in practice.",
            ),
            answer=0,
            explanation=(
                "Finite variance is the price of admission. With Cauchy draws no single "
                "extreme value ever gets diluted, and remarkably the sample mean has the "
                "same distribution as one draw for any n. Such sums converge to stable "
                "laws, but the normal is not among them."
            ),
        ),
        Question(
            prompt="The weak law of large numbers can be read straight off one fact about the sample mean. Which fact?",
            options=(
                "Its variance equals sigma-squared over n, which shrinks to zero as n grows.",
                "Its bias equals sigma over root n, which shrinks to zero as n grows.",
                "Its distribution is exactly normal for every n by construction.",
                "Its largest single observation comes to dominate the sum as n grows.",
            ),
            answer=0,
            explanation=(
                "The sample mean is unbiased with variance sigma-squared over n. A zero-bias "
                "estimator whose variance vanishes must concentrate on its target — that is "
                "Chebyshev's inequality turning shrinking variance into shrinking probability "
                "of being far off."
            ),
        ),
        Question(
            prompt="Convergence in distribution is generally weaker than convergence in probability, yet they coincide in one important case. Which?",
            options=(
                "When the limit is a constant, convergence in distribution to it implies convergence in probability.",
                "When the sequence is bounded, the two modes are always equivalent.",
                "When every term is normally distributed, distributional convergence forces almost sure convergence.",
                "When the limit has finite variance, the weaker mode automatically upgrades to the stronger.",
            ),
            answer=0,
            explanation=(
                "Converging in distribution to a fixed point leaves nowhere for the mass to "
                "hide, so it coincides with convergence in probability. This is why the LLN, "
                "whose limit is the constant mu, can be stated in either mode."
            ),
        ),
    ),
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
