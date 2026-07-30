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
    Term(
        "Parameter",
        "A fixed but unknown feature of the world — a number or handful of numbers — that pins down which distribution in a model actually generated the data.",
    ),
    Term(
        "Statistical model",
        "A family of probability distributions, one for each possible parameter value, adopted as a description of how the data was produced; an assumption to be judged for adequacy, not a fact.",
    ),
    Term(
        "Random variable",
        "A numerical quantity whose value is uncertain — formally a function from outcomes to the real line; its distribution says how probability is spread over the values it can take.",
    ),
    Term(
        "Cumulative distribution function (CDF)",
        "The function F(x) = P(X <= x) giving the probability a variable lands at or below x. It exists for every distribution, runs from 0 to 1, and never decreases.",
    ),
    Term(
        "Probability density function (pdf)",
        "For a continuous variable, the rate F'(x) at which the CDF climbs; probability over an interval is the area under it. A density is not a probability and its height can exceed one.",
    ),
    Term(
        "Probability mass function (pmf)",
        "For a discrete variable, the function p(x) = P(X = x) placing a lump of probability directly on each attainable value; the lumps sum to one.",
    ),
    Term(
        "Joint distribution",
        "The distribution of two or more variables together, spending the unit of probability over combinations of their values rather than over single values.",
    ),
    Term(
        "Marginal distribution",
        "The distribution of one variable alone, recovered from a joint distribution by summing or integrating the other variables away; the joint's shadow on one axis.",
    ),
    Term(
        "Conditional distribution",
        "The distribution of one variable once another is fixed at a specific value, obtained by slicing the joint at that value and renormalizing so probability sums to one again.",
    ),
    Term(
        "Independence",
        "The property that knowing one variable tells you nothing about another; equivalently, their joint distribution factors into the product of their marginals.",
    ),
    Term(
        "Expectation",
        "The probability-weighted average of a random variable — a sum or integral of its values weighted by their likelihood; the balance point (center of mass) of its distribution. Also called the expected value or mean.",
    ),
    Term(
        "Linearity of expectation",
        "The rule that the expectation of a sum equals the sum of the expectations, and that constants pull out: E[aX + bY] = a E[X] + b E[Y]. It holds whether or not the variables are independent.",
    ),
    Term(
        "Moment",
        "An expectation of a power of a random variable. The k-th (raw) moment is E[X^k]; the k-th central moment, E[(X - mean)^k], measures shape relative to the mean.",
    ),
    Term(
        "Central moment",
        "A moment taken about the mean, E[(X - mean)^k], so it describes shape rather than location. Variance, skewness, and kurtosis are built from the second, third, and fourth central moments.",
    ),
    Term(
        "Variance (of a distribution)",
        "The second central moment, E[(X - mean)^2]: the average squared distance of a random variable from its mean, and the standard measure of a distribution's spread.",
    ),
    Term(
        "Standard deviation",
        "The square root of the variance, which restores the original units of the variable and so gives an interpretable measure of spread.",
    ),
    Term(
        "Skewness",
        "The standardized third central moment, measuring a distribution's asymmetry. Positive skew means a longer right tail, negative a longer left tail, and zero any symmetric law.",
    ),
    Term(
        "Kurtosis",
        "The standardized fourth central moment, measuring how much of the variance comes from rare extreme deviations — that is, tail weight. The normal distribution has kurtosis 3; 'excess kurtosis' subtracts that reference off.",
    ),
    Term(
        "Covariance",
        "The expectation E[(X - mean_X)(Y - mean_Y)], measuring how two variables move together. It is the cross term that makes the variance of a sum depart from the sum of the variances unless the variables are uncorrelated.",
    ),
    Term(
        "Moment generating function",
        "The function M_X(t) = E[e^{tX}]. Its derivatives at zero produce the moments, and where it exists near zero it determines the distribution uniquely and turns sums of independent variables into products.",
    ),
    Term(
        "Characteristic function",
        "The function E[e^{itX}] with an imaginary exponent. Because e^{itX} stays bounded, it exists for every distribution, uniquely determines the law, and turns sums into products — the always-available substitute for the moment generating function.",
    ),
    Term(
        "Exponential family",
        "A class of distributions whose density can be written as h(x) exp(eta(theta) . T(x) - A(theta)), so the parameter touches the data only through a natural parameter times a sufficient statistic inside one exponential. Most familiar distributions (normal, Bernoulli, Poisson, exponential, gamma, beta) are members, which is why sufficiency, conjugate priors, and clean moment formulas all appear together.",
    ),
    Term(
        "Sufficient statistic",
        "A function of the data that carries everything the sample tells you about the parameter, so the raw data can be discarded once you know it. In an exponential family the statistic T (summed over the sample) is sufficient and has a fixed size no matter how large the sample grows.",
    ),
    Term(
        "Natural parameter",
        "The parameter of an exponential family rewritten into the coordinate eta in which it multiplies the sufficient statistic linearly; for a Bernoulli coin it is the log-odds. Also called the canonical parameter.",
    ),
    Term(
        "Log-partition function",
        "The term A(theta) in an exponential family, the logarithm of the normalizing constant that makes the density integrate to one. It is determined by the other pieces, and its derivatives in the natural parameter give the mean and variance of the sufficient statistic.",
    ),
    Term(
        "Base measure",
        "The factor h(x) in an exponential family: the part of the density that depends on the data alone and does not move as the parameter changes.",
    ),
    Term(
        "Conjugate prior",
        "A prior distribution chosen so that, after updating on data, the posterior stays in the same family as the prior; the update just adjusts a few numbers. Every exponential family has a matched conjugate prior (for example, a Beta prior for a Bernoulli rate stays Beta).",
    ),
    Term(
        "Convergence in probability",
        "A sequence of random variables converges in probability to a limit if, for every fixed tolerance, the chance of being farther than that tolerance from the limit shrinks to zero. This is the mode that defines consistency.",
    ),
    Term(
        "Almost sure convergence",
        "The strongest common mode: with probability one, the actual sequence of values you observe converges to the limit in the ordinary sense. It implies convergence in probability, but not conversely.",
    ),
    Term(
        "Convergence in distribution",
        "The weakest common mode: the cumulative distribution functions converge at every point where the limit is continuous. It constrains only the shape of the distribution, not where any particular draw lands.",
    ),
    Term(
        "Law of large numbers",
        "The theorem that the sample mean of independent draws converges to the true mean as the sample grows. The weak law states this in probability, the strong law almost surely. It is why estimation by averaging works.",
    ),
    Term(
        "Central limit theorem",
        "The theorem that the standardized sample mean of independent draws with finite variance converges in distribution to a normal, regardless of the source distribution. It is why the normal appears everywhere and why standard errors work.",
    ),
    Term(
        "Sampling distribution",
        "The distribution of a statistic (such as the sample mean) across repeated samples from the same population; the object that lets you judge a procedure before seeing data, and describes how much the statistic would vary if you drew fresh data.",
    ),
    Term(
        "Standard error",
        "The standard deviation of an estimator's sampling distribution — the typical distance between an estimate and its target. For a sample mean it is the population standard deviation divided by the square root of the sample size.",
    ),
    Term(
        "Estimand",
        "The fixed unknown quantity you are trying to estimate — the target an estimator aims at, usually a parameter or a function of one.",
    ),
    Term(
        "Unbiased estimator",
        "An estimator whose expected value equals the estimand for every possible parameter value, so its guesses average out to the truth. Being unbiased constrains only the center of the sampling distribution, not its spread, so it does not imply low error.",
    ),
    Term(
        "Fisher-Neyman factorization theorem",
        "The practical test for sufficiency: a statistic T is sufficient for the parameter exactly when the likelihood factors into a piece depending on the data only through T (and on the parameter) times a piece of the data alone.",
    ),
    Term(
        "Minimal sufficient statistic",
        "The coarsest sufficient statistic — the maximal compression of the data that still loses no information about the parameter. Any other sufficient statistic can be reduced to it.",
    ),
    Term(
        "Score function",
        "The derivative of the log-likelihood with respect to the parameter. It is zero at the maximum likelihood estimate, and its expected square is the Fisher information.",
    ),
    Term(
        "Fisher information",
        "A measure of how much a sample tells you about a parameter, equal to the expected squared score and, for smooth models, to the expected curvature (negative second derivative) of the log-likelihood at the truth. A sharp likelihood peak means high information; a flat one means low.",
    ),
    Term(
        "Fisher information matrix",
        "The multi-parameter version of Fisher information: a matrix of expected curvatures and cross-curvatures of the log-likelihood surface, whose inverse floors the covariance of any unbiased estimator.",
    ),
    Term(
        "Cramer-Rao bound",
        "A lower bound on the variance of any unbiased estimator: the variance cannot fall below one over the total Fisher information, 1/(n I(theta)). It sets the best precision the data can buy, and biased estimators may fall below it.",
    ),
    Term(
        "Efficiency",
        "How close an estimator comes to the Cramer-Rao floor, measured as the ratio of the bound to the estimator's variance; it runs from 0 (wasteful) to 1 (best possible). An efficient estimator attains the floor.",
    ),
    Term(
        "Likelihood function",
        "For fixed observed data, the model's probability (or density) of that data read as a function of the parameter. It scores each candidate parameter by how well it would have anticipated the data; it is not a probability distribution over the parameter.",
    ),
    Term(
        "Log-likelihood",
        "The logarithm of the likelihood function. Taking the log turns the product over an independent sample into a sum without moving the peak, and it is the function one actually maximizes in practice.",
    ),
    Term(
        "Maximum likelihood estimator (MLE)",
        "The parameter value that maximizes the likelihood (equivalently, the log-likelihood) of the observed data — the top of the likelihood scoreboard, the setting under which the data is least surprising.",
    ),
    Term(
        "Asymptotic normality",
        "The property that an estimator's sampling distribution approaches a Normal centered at the target as the sample size grows. Under regularity the MLE is asymptotically normal with variance equal to the Cramer-Rao floor.",
    ),
    Term(
        "Regularity conditions",
        "The technical assumptions — a smooth log-likelihood and a data range that does not depend on the parameter, among others — under which the MLE is consistent and asymptotically normal. Models that break them, such as the uniform on an interval whose endpoint is the parameter, need case-by-case treatment.",
    ),
    Term(
        "Prior distribution",
        "A probability distribution over a parameter that encodes what you believe about it before seeing the current data. Combined with the likelihood through Bayes' rule, it becomes the posterior.",
    ),
    Term(
        "Posterior distribution",
        "The distribution of a parameter after updating the prior with observed data, proportional to the prior times the likelihood. It is the Bayesian's full answer, from which any point estimate or interval is only a summary.",
    ),
    Term(
        "Bayes' rule",
        "The identity that the posterior is proportional to the prior times the likelihood, normalized by the marginal likelihood. It is the single mechanical step that turns a belief held before the data into one held after.",
    ),
    Term(
        "Marginal likelihood (evidence)",
        "The probability of the observed data averaged over all parameter values under the prior, and the denominator in Bayes' rule. Being independent of the parameter, it only renormalizes the posterior, but across models it serves as the score behind Bayes factors.",
    ),
    Term(
        "Credible interval",
        "An interval that holds a stated share, such as 95%, of the posterior probability for a parameter. Unlike a confidence interval, it licenses the direct statement that the parameter lies inside it with that probability, given the prior and data.",
    ),
    Term(
        "Maximum a posteriori (MAP) estimate",
        "The parameter value at which the posterior density is highest — the single most probable value. Under a flat prior it coincides with the maximum-likelihood estimate, and it is what penalized (regularized) estimation computes.",
    ),
    Term(
        "Squared-error loss",
        "The loss (c − y)^2, charging the square of how far an estimate c falls from the truth y. Its best constant summary of a distribution is the mean, and it is the loss under which the bias-variance decomposition holds.",
    ),
    Term(
        "Absolute-error loss",
        "The loss |c − y|, charging the raw distance of a miss rather than its square. Its best constant summary is the median, and its linear growth makes it robust to outliers.",
    ),
    Term(
        "Huber loss",
        "A loss that is quadratic for residuals within a threshold and linear beyond it, blending the small-error efficiency of squared-error loss with the outlier resistance of absolute-error loss. The threshold dials between the two extremes.",
    ),
    Term(
        "0-1 loss",
        "The loss that charges nothing for an exact hit and a flat penalty of one for any miss, regardless of size. Its best constant summary is the mode, and it underlies classification's most-probable-class rule.",
    ),
    Term(
        "Quantile loss",
        "An asymmetric loss, also called pinball loss, that charges an under-prediction slope tau and an over-prediction slope 1 − tau. Its minimizer is the tau-quantile of the distribution, so choosing tau chooses which quantile to estimate.",
    ),
    Term(
        "Robustness",
        "The property that a few extreme or corrupted observations cannot swing an estimate arbitrarily far. It follows from a loss whose penalty grows slowly (for example linearly) in the tails rather than quadratically.",
    ),
    Term(
        "Median",
        "The value that splits a distribution into two halves of probability one-half each. It is the constant summary that minimizes expected absolute-error loss.",
    ),
    Term(
        "Mode",
        "The most probable value of a distribution — the peak of its density or its most likely category. It is the constant summary that minimizes expected 0-1 loss.",
    ),
    Term(
        "Decision rule",
        "Any function that maps observed data to an action — an estimate, or a choice like accept versus reject. Estimators are decision rules; risk is how you grade one.",
    ),
    Term(
        "Risk function",
        "The expected loss of a decision rule when the truth is fixed at a given parameter value, averaged over the sampling distribution of the data. It is a function of the unknown parameter — one height per possible truth, so it is a whole curve rather than a single number.",
    ),
    Term(
        "Dominance",
        "One decision rule dominates another when its risk is no larger at every parameter value and strictly smaller at at least one. The dominated rule can be beaten everywhere at once, so there is never a reason to use it.",
    ),
    Term(
        "Admissibility",
        "A decision rule is admissible if no other rule dominates it, and inadmissible if some rule does. Admissibility is only a floor: it rules out being beaten everywhere, but an admissible rule can still be bad, and it does not by itself single out a best rule.",
    ),
    Term(
        "Minimax",
        "The criterion that judges a decision rule by its worst-case risk over the parameter and prefers the rule whose worst case is smallest. It buys a guarantee against the least favorable value of the unknown, at the cost of defending against truths that may be far from reality.",
    ),
    Term(
        "Least favorable prior",
        "The prior an adversary would choose to make your task hardest — the one that maximizes the Bayes risk of its own Bayes decision rule. Under broad conditions the minimax rule is exactly the Bayes decision rule for this prior.",
    ),
    Term(
        "Bayes risk",
        "The risk curve of a decision rule averaged against a prior distribution over the parameter, collapsing the whole curve to a single number. The rule that minimizes it is the Bayes decision rule for that prior.",
    ),
    Term(
        "Bayes decision rule",
        "The decision rule that minimizes Bayes risk for a given prior, equivalently the rule that minimizes posterior expected loss dataset by dataset. Under squared-error loss it returns the posterior mean, under absolute-error loss the posterior median, under 0-1 loss the posterior mode. Distinct from Bayes' rule the theorem, which computes the posterior itself.",
    ),
    Term(
        "Stein's paradox",
        "The surprising fact that when you estimate three or more means at once under total squared-error loss, the vector of sample means is inadmissible: a shrinkage estimator beats it at every parameter value, even for unrelated quantities.",
    ),
    Term(
        "James-Stein estimator",
        "An estimator of a vector of means that shrinks every coordinate toward a common center by a single data-dependent factor. For three or more coordinates it has strictly smaller total risk than the sample mean everywhere.",
    ),
    Term(
        "Borrowing strength",
        "Estimating many quantities jointly by pulling their estimates toward a shared center, so the ensemble informs each one; also called partial pooling. The pooling corrects the scale of the noise, not the meaning of the quantities.",
    ),
    Term(
        "Ridge regression",
        "A regularized least-squares fit that adds a penalty on the sum of squared coefficients (the L2 penalty); it shrinks every coefficient smoothly toward zero but keeps them all nonzero.",
    ),
    Term(
        "Lasso",
        "A regularized least-squares fit that adds a penalty on the sum of absolute coefficient values (the L1 penalty); it can drive some coefficients exactly to zero, so it selects variables as it shrinks.",
    ),
    Term(
        "L2 penalty",
        "A regularization term equal to the sum of squared coefficients. As the penalty on magnitude behind ridge regression, it corresponds to a Gaussian prior on the coefficients.",
    ),
    Term(
        "L1 penalty",
        "A regularization term equal to the sum of absolute coefficient values. As the penalty behind the lasso, it corresponds to a Laplace prior and its constant slope at zero is what produces exact zeros.",
    ),
    Term(
        "Sparsity",
        "The property of a model in which most coefficients are exactly zero, so only a subset of the predictors is actually used; the lasso induces it, ridge does not.",
    ),
    Term(
        "Laplace prior",
        "The double-exponential prior, with density proportional to exp(-|beta|/b); its sharp cusp at zero and heavy tails make it the prior whose MAP estimate is the lasso fit.",
    ),
    Term(
        "Cross-validation",
        "A way to estimate a model's out-of-sample (generalization) error using only the data at hand, by repeatedly fitting on part of the sample and scoring on the held-out remainder. Used to choose tuning parameters such as a penalty.",
    ),
    Term(
        "k-fold cross-validation",
        "Cross-validation that splits the data into k roughly equal folds, then trains on k-1 folds and scores on the one held out, rotating so every fold is held out once, and averages the k held-out scores.",
    ),
    Term(
        "Leave-one-out cross-validation",
        "The extreme case of k-fold cross-validation with k equal to the sample size: each single observation is held out in turn. Low bias but often high variance, since the training sets barely differ.",
    ),
    Term(
        "Training error",
        "The average loss a model incurs on the very data it was fit to. It measures how hard the fit tried, not how well it generalizes, and falls as regularization weakens, so it cannot be used to choose a penalty.",
    ),
    Term(
        "Generalization error",
        "The expected loss a fitted model would incur on a fresh observation from the same process. The quantity a penalty should minimize, and what cross-validation estimates.",
    ),
    Term(
        "Overfitting",
        "Fitting a model so closely to the training data that it captures noise as if it were signal, giving low training error but poor generalization. The high-variance extreme, reached as the penalty goes to zero.",
    ),
    Term(
        "Underfitting",
        "Constraining a model so heavily that it misses real structure in the data, giving high error on both training and new data. The high-bias extreme, reached as the penalty grows large.",
    ),
    Term(
        "Effective degrees of freedom",
        "A continuous measure of a fitted model's complexity: how many parameters it effectively spends once regularization tethers its coefficients. For a linear smoother it is the trace of the hat matrix, sliding from the parameter count down toward zero as the penalty grows.",
    ),
    Term(
        "Hat matrix",
        "The matrix H that maps observed responses to fitted values, y-hat = H y, for a linear fit. Named because it 'puts the hat on y'; its trace gives the fit's effective degrees of freedom.",
    ),
    Term(
        "Linear smoother",
        "Any fitting method whose fitted values are a fixed linear map of the responses, y-hat = H y. Ridge regression, smoothing splines, and k-nearest-neighbors are examples, and all share the trace-of-H notion of complexity.",
    ),
    Term(
        "One-standard-error rule",
        "A model-selection heuristic that, among all penalties whose cross-validation error is within one standard error of the minimum, picks the largest (most regularized), favoring a simpler model that is statistically indistinguishable from the best.",
    ),
    Term(
        "Degrees of freedom",
        "The number of independent directions in which a fit is free to move to chase the data. For an unpenalized linear model it equals the parameter count; regularization replaces it with a smaller effective count.",
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
