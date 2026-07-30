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
    "hypothesis-testing": (
        Question(
            prompt="In the Neyman–Pearson framework you fix the size alpha and then maximize power, rather than minimizing the total error rate alpha + beta. What does this choice actually encode?",
            options=(
                "A deliberate asymmetry: falsely rejecting a true null is judged the costlier error, so its rate is capped no matter which alternative holds, and power is optimized only under that cap.",
                "A proof that alpha + beta cannot be minimized because beta depends on the unknown true alternative while alpha does not.",
                "A convention that keeps the math tractable but has no decision-theoretic content, since any monotone criterion gives the same test.",
                "An assumption that the null and alternative are equally likely a priori, which is what makes the likelihood ratio threshold equal to one.",
            ),
            answer=0,
            explanation="Fixing alpha treats the two errors asymmetrically on purpose: rejecting a true null is the error you have decided is worse, so you bound it uniformly over the null and do the best you can on beta. Minimizing alpha + beta is itself well defined and corresponds to a Bayes rule under equal losses and equal priors — its threshold is likelihood ratio = 1 — but that is a different, symmetric problem, which is exactly what Neyman–Pearson declines to assume.",
        ),
        Question(
            prompt="The Neyman–Pearson lemma guarantees the likelihood ratio test is most powerful. For which testing problem does that guarantee hold exactly?",
            options=(
                "A simple null against a simple alternative, where each hypothesis names one fully specified distribution.",
                "Any null against any alternative, provided the sample size is large enough for the asymptotics to kick in.",
                "A simple null against a one-sided composite alternative, for every parametric family without exception.",
                "A composite null against a composite alternative, as long as both are drawn from an exponential family.",
            ),
            answer=0,
            explanation="The lemma is a simple-versus-simple result: both hypotheses must be single, fully specified distributions. It extends to a one-sided composite alternative only under the extra structure of a monotone likelihood ratio (Karlin–Rubin), and that yields a uniformly most powerful test — it is not automatic for every family, and it does not survive two-sided alternatives.",
        ),
        Question(
            prompt="A test is described as having 'level 0.05' but 'size 0.03'. What is the relationship being expressed?",
            options=(
                "The level is the promised upper bound on the Type I error rate, while the size is the test's actual worst-case Type I rate; here the test is conservative, spending less alpha than allowed.",
                "The level is the Type I error rate and the size is the Type II error rate, so the test rejects true nulls 5% of the time and misses real effects 3% of the time.",
                "The size is the false-alarm rate at the observed data and the level is its long-run average, so the two differ only by sampling noise.",
                "The level applies before seeing data and the size after, so the size is the posterior probability that the null is true given this sample.",
            ),
            answer=0,
            explanation="Size is the supremum of the rejection probability over the null — what the test really does — while level is the ceiling you claim for it; a test has level alpha when its size is at most alpha. A size below the level means the test is conservative and is leaving power on the table. Neither quantity is a Type II rate or a posterior probability of the null.",
        ),
        Question(
            prompt="You run a generalized likelihood ratio test comparing a full model with 6 free parameters to a nested null that fixes 2 of them. Under Wilks' theorem and its regularity conditions, what is the reference distribution for −2 log Λ?",
            options=(
                "Chi-square with 2 degrees of freedom, the number of parameters the null fixes.",
                "Chi-square with 6 degrees of freedom, the number of free parameters in the full model.",
                "Chi-square with 4 degrees of freedom, the number of parameters left free under the null.",
                "Chi-square with degrees of freedom equal to the sample size minus 6, as in a residual variance estimate.",
            ),
            answer=0,
            explanation="The degrees of freedom equal the drop in dimension from the full model to the null — the number of restrictions imposed, here 2 — not the total parameter count and not the sample size. Miscounting restrictions mis-calibrates every resulting p-value, and the chi-square itself is only the large-sample limit, valid when the null lies in the interior of the parameter space.",
        ),
        Question(
            prompt="You test whether a variance component equals zero using −2 log Λ against a chi-square with 1 degree of freedom. A colleague warns the calibration is wrong. Why?",
            options=(
                "Because a variance cannot be negative, the null sits on the boundary of the parameter space, so the limit is a mixture of a point mass at zero and a chi-square rather than a plain chi-square.",
                "Because variance-component models are never nested, so Wilks' theorem does not apply and only information criteria can compare them.",
                "Because the likelihood ratio is undefined when a parameter equals zero, so the statistic must be computed on the log-variance scale instead.",
                "Because testing a variance requires an F distribution, not a chi-square, whenever the residual degrees of freedom are finite.",
            ),
            answer=0,
            explanation="Zero is a boundary for a variance, which violates the interior-point regularity condition behind Wilks' theorem. Chernoff's result gives the correct limit — often a 50:50 mixture of a spike at zero and a chi-square with one degree of freedom — so using the naive chi-square makes the test conservative and costs power. The models here are genuinely nested; the problem is the boundary, not nesting.",
        ),
    ),
    "p-values-power-and-errors": (
        Question(
            prompt=(
                "A study reports p = 0.01. Which statement correctly describes what "
                "that number means?"
            ),
            options=(
                "There is only a 1% probability that the null hypothesis is true, given the specific data actually observed in this particular study.",
                "Assuming the null is true, data at least this extreme would arise about 1% of the time.",
                "The effect has a 99% chance of replicating in a new experiment.",
                "The measured effect is large enough to be practically important.",
            ),
            answer=1,
            explanation=(
                "A p-value is computed assuming the null holds; it is the tail probability "
                "of a test statistic at least as extreme as observed. It conditions on the "
                "null, so it is not the probability the null is true (that would need a prior "
                "and Bayes' rule). It is not a replication probability, which depends on the "
                "true effect and the new study's power, and it is not an effect size — a huge "
                "sample can make a trivial effect cross any threshold."
            ),
        ),
        Question(
            prompt=(
                "Why is the p-value distributed Uniform(0,1) when the null hypothesis is "
                "true and the test statistic is continuous?"
            ),
            options=(
                "Because most test statistics are approximately normal near the null.",
                "Because the central limit theorem forces the distribution of essentially any test statistic toward uniformity as the sample size grows.",
                "Because plugging a random variable into its own CDF yields a uniform variable.",
                "Because the sample size is assumed large enough for asymptotics to hold.",
            ),
            answer=2,
            explanation=(
                "The p-value is essentially one minus the null CDF evaluated at the statistic, "
                "and feeding a variable through its own CDF is the probability integral "
                "transform, which returns a Uniform(0,1). This is exact for a continuous "
                "statistic, not an asymptotic approximation, and it is precisely what makes a "
                "level-α test reject a true null a fraction α of the time. With a discrete "
                "statistic the p-value is only lumpily uniform."
            ),
        ),
        Question(
            prompt=(
                "You screen 1000 hypotheses at α = 0.05 with 80% power, and only 10% of the "
                "hypotheses correspond to real effects. Roughly what fraction of your "
                "significant results are false positives?"
            ),
            options=(
                "About 5%, because that is the significance level you tested at.",
                "About 20%, because power was 80% so 20% of findings are missed.",
                "About 36%, because the many true nulls generate false positives that swamp the few real hits.",
                "About 1%, since a p-value below 0.05 makes each individual finding very likely to reflect a real effect rather than chance noise.",
            ),
            answer=2,
            explanation=(
                "The 100 real effects yield about 80 true positives; the 900 nulls yield about "
                "0.05 x 900 = 45 false positives. Of 125 significant results, 45 are false, "
                "roughly 36%. The significance level controls the error rate among nulls only; "
                "with a low base rate the sheer number of nulls dominates the mix, which is why "
                "a small p-value need not signal a likely-true finding."
            ),
        ),
        Question(
            prompt=(
                "An underpowered study nonetheless reaches p < 0.05. Why should you distrust "
                "its reported effect size more, not less, because of the low power?"
            ),
            options=(
                "Because low power inflates the p-value, making the result borderline.",
                "Because only unusually large estimates clear the bar, so the significant ones are biased upward.",
                "Because low power almost always flips the sign of the estimated effect, so the reported direction is the one thing you cannot trust.",
                "Because the significance itself corrects the estimate for bias.",
            ),
            answer=1,
            explanation=(
                "At low power the alternative barely separates from the null, so only the "
                "luckiest, most inflated estimates cross the threshold — the winner's curse, or "
                "a Type M (magnitude) error. Significance conditions on clearing the bar, which "
                "selects for overestimates, so the point estimate is biased upward by "
                "construction. A Type S (sign) error, getting the direction wrong, is also "
                "possible but not guaranteed. This is why better-powered replications routinely "
                "find smaller effects than the original."
            ),
        ),
        Question(
            prompt=(
                "For a genome-wide screen of 20,000 tests, why is the Benjamini–Hochberg "
                "procedure usually preferred over a Bonferroni correction?"
            ),
            options=(
                "Because Bonferroni cannot be applied when the number of tests is very large.",
                "Because Bonferroni is built to control the rate of false negatives, while Benjamini-Hochberg is instead built to control the rate of false positives.",
                "Because BH guarantees zero false positives whereas Bonferroni does not.",
                "Because BH controls the expected fraction of false discoveries, keeping power Bonferroni would destroy.",
            ),
            answer=3,
            explanation=(
                "Bonferroni controls the family-wise error rate — the chance of even one false "
                "positive — by testing each hypothesis at α/m, which for m = 20,000 is so strict "
                "it discards nearly every real effect too. BH instead controls the false "
                "discovery rate, the expected share of rejections that are false, tolerating a "
                "controlled sprinkle of false positives to recover many more true discoveries. "
                "Neither guarantees zero false positives; BH's guarantee is on-average, not "
                "never-any."
            ),
        ),
        Question(
            prompt=(
                "A researcher tries several outcome definitions and covariate sets, reporting "
                "only the analysis that reached p < 0.05. Why does this invalidate the reported "
                "p-value even though a single test was ultimately reported?"
            ),
            options=(
                "It does not; reporting one clean analysis is standard and fully valid.",
                "Because properly averaging the reported p-value together with the ones from the discarded analyses would have pushed it even further below the threshold.",
                "Because the choice of analysis depended on the data, so many tests were implicitly run and the null distribution shifted.",
                "Because using covariates always biases a p-value regardless of how they are chosen.",
            ),
            answer=2,
            explanation=(
                "The p-value's uniform-under-the-null guarantee assumes a single, pre-specified "
                "test. When the analysis is chosen because it crossed the threshold — p-hacking, "
                "or its subtler cousin the garden of forking paths — a whole thicket of tests is "
                "effectively run, so the true null distribution of the reported statistic is no "
                "longer the one assumed. Covariate adjustment is not the problem; letting the "
                "data pick the adjustment is. Pre-registration is what restores the guarantee."
            ),
        ),
    ),
    "intervals": (
        Question(
            prompt=(
                "You compute a 95% confidence interval and get [3.1, 4.8]. Which "
                "statement is the only fully correct reading under the frequentist "
                "definition?"
            ),
            options=(
                "If the experiment were repeated many times, about 95% of the "
                "intervals the procedure produces would contain the fixed parameter.",
                "There is a 95% probability that the parameter lies between 3.1 and 4.8, "
                "given the data you actually observed this one time.",
                "The parameter falls in [3.1, 4.8] in 95% of the samples, and outside it "
                "in the other 5%, because the parameter varies from sample to sample.",
                "About 95% of future data points drawn from the population will land "
                "between 3.1 and 4.8, which is what the interval is built to capture.",
            ),
            answer=0,
            explanation=(
                "Coverage is a long-run property of the procedure: 95% of the random "
                "intervals it makes cover the fixed target. Once the data is in, the "
                "endpoints and the parameter are all fixed numbers, so the chance this "
                "interval contains it is 0 or 1, not 0.95. The parameter does not vary "
                "across samples (the intervals do), and an interval for a parameter is "
                "not a prediction interval for new data points."
            ),
        ),
        Question(
            prompt=(
                "What property of a pivotal quantity is exactly what lets you turn it "
                "into a confidence interval with correct coverage?"
            ),
            options=(
                "Its sampling distribution does not depend on the unknown parameter, so "
                "its quantiles are fixed and can be inverted to bracket the parameter.",
                "It is an unbiased estimator of the parameter, so its expected value "
                "equals the target and the interval centers on the truth.",
                "It is exactly normally distributed for every sample size, so the 1.96 "
                "multiplier always delivers precisely 95% coverage.",
                "It is the maximum-likelihood estimator, whose established efficiency "
                "guarantees that the resulting interval comes out as the shortest one attainable at that confidence level.",
            ),
            answer=0,
            explanation=(
                "A pivot mixes data and parameter into a quantity whose distribution is "
                "parameter-free, so you can bracket its fixed quantiles and solve for the "
                "parameter. Being unbiased, exactly normal, or the MLE are none of them "
                "the requirement: the standardized mean with unknown variance is not "
                "normal but a t pivot, and it still gives exact coverage because its "
                "distribution does not depend on the mean."
            ),
        ),
        Question(
            prompt=(
                "By test-interval duality, the 1 minus alpha confidence set for a "
                "parameter is exactly which collection of values?"
            ),
            options=(
                "The null values that a level-alpha test does not reject on the "
                "observed data.",
                "The null values that a level-alpha test does reject, since those are "
                "the ones the data speaks against.",
                "The parameter values at which the likelihood of the observed data "
                "exceeds a fixed absolute threshold.",
                "The parameter values assigned more than 1 minus alpha of the posterior "
                "probability under a flat prior.",
            ),
            answer=0,
            explanation=(
                "The confidence set gathers the nulls that survive testing, and its "
                "coverage follows in one line from the test's level: the true value "
                "escapes rejection with probability 1 minus alpha. Rejected values are "
                "the complement. A raw likelihood cutoff is a different (likelihood-"
                "interval) construction, and a posterior statement is the Bayesian "
                "object, which needs a prior."
            ),
        ),
        Question(
            prompt=(
                "On a right-skewed posterior, how do the equal-tailed and highest "
                "posterior density (HPD) 95% credible intervals compare?"
            ),
            options=(
                "The HPD is the shorter of the two and sits closer to the mode, while "
                "the equal-tailed interval cuts 2.5% from each tail and is stretched by "
                "the long tail.",
                "They are identical, because both are simply two equivalent ways of describing "
                "the very same central 95% region of any posterior distribution you could write down.",
                "The equal-tailed interval is always the shorter, since removing the "
                "extreme tails is the most efficient way to keep 95% of the mass.",
                "The HPD is always wider, because requiring equal density at both "
                "endpoints forces it to reach farther into the tail on each side.",
            ),
            answer=0,
            explanation=(
                "The HPD is by definition the shortest interval holding 95%, with equal "
                "density at its ends, so on a skew it hugs the mode and comes out shorter "
                "than the equal-tailed version. The two coincide only for a symmetric, "
                "unimodal posterior; there the choice does not matter, which is why the "
                "distinction only surfaces under skew."
            ),
        ),
        Question(
            prompt=(
                "Inverting a certain test yields, on your particular dataset, an EMPTY "
                "95% confidence set. What is the right conclusion?"
            ),
            options=(
                "The procedure can still have exact 95% coverage overall; an empty set "
                "on one sample reflects that coverage is a property of the procedure, "
                "not of this interval.",
                "The procedure must be invalid and its true long-run coverage must actually be "
                "below 95%, because a genuinely correct interval procedure can never once come out empty on any sample.",
                "The data must contain an error, because there is always at least one "
                "parameter value consistent with any valid sample.",
                "The parameter has been proven not to exist in the assumed model, which "
                "is the intended meaning of an empty confidence set.",
            ),
            answer=0,
            explanation=(
                "Coverage averages over the sampling distribution, and a procedure can "
                "hit exactly 95% while occasionally emitting an empty set or the whole "
                "line on specific samples (ratios of means and boundary problems are "
                "classic cases). An empty set is not a coverage failure or a data bug; "
                "it is the vivid reminder that the 95% never described this one interval."
            ),
        ),
        Question(
            prompt=(
                "Under a flat prior, the 95% credible interval for a normal mean equals "
                "the 95% confidence interval numerically. What does this coincidence "
                "establish?"
            ),
            options=(
                "Only that the endpoints match here; the two still make different "
                "claims, one about the procedure across repeats and one about the "
                "parameter given the data.",
                "That confidence and credible intervals are fundamentally the same concept, so "
                "the frequentist and the Bayesian readings of an interval are freely interchangeable in general.",
                "That the flat prior was truly uninformative, which is the reason the "
                "two frameworks are guaranteed to agree in every problem.",
                "That the confidence interval secretly assumed a flat prior all along, "
                "so every confidence interval is really a credible interval in "
                "disguise.",
            ),
            answer=0,
            explanation=(
                "Matching numbers do not merge the meanings: one interval reports the "
                "behavior of a rule over hypothetical repeats, the other a posterior "
                "probability about the parameter given this data. The agreement is "
                "special to symmetric, large-sample, flat-prior settings and breaks "
                "under informative priors, skew, boundaries, or small n, so the two are "
                "not interchangeable in general."
            ),
        ),
    ),
    "the-shrinkage-surprise": (
        Question(
            prompt=(
                "Stein's paradox says the vector of sample means is inadmissible "
                "for estimating three or more means at once. What exactly does the "
                "James-Stein estimator improve on, and where?"
            ),
            options=(
                "The total risk, the expected sum of squared errors across all "
                "coordinates, and it is strictly smaller at every true mean "
                "vector.",
                "The risk in each individual coordinate separately, so that every "
                "single coordinate's estimate is guaranteed at least as accurate as "
                "the plain sample mean at every value of that coordinate's true mean.",
                "The total risk, but only when the true means happen to lie close to "
                "the shrinkage center that the estimator pulls toward.",
                "The worst-case risk over all parameter values, leaving the risk "
                "unchanged everywhere except at the least favorable point.",
            ),
            answer=0,
            explanation=(
                "The dominance is over total (summed) risk and holds at every theta, "
                "which is what makes the sample mean inadmissible. It is emphatically "
                "not a per-coordinate guarantee: a single coordinate can get worse. "
                "And the win exists everywhere, not only near the center, though it is "
                "largest there and shrinks toward zero as the truth moves far away."
            ),
        ),
        Question(
            prompt=(
                "Why does shrinkage help even when the quantities being estimated are "
                "utterly unrelated, like a batting average and a wheat yield?"
            ),
            options=(
                "Because with enough unrelated quantities, some are always close to "
                "the center, and shrinkage exploits those without harming the rest.",
                "Because the gain comes from correcting the length of the noise, which "
                "totals p times sigma-squared regardless of how the true means relate.",
                "Because unrelated quantities are statistically independent, and "
                "independence is precisely the condition that makes pooling unbiased.",
                "Because on a common scale unrelated quantities become exchangeable, so "
                "borrowing information between them is then fully justified.",
            ),
            answer=1,
            explanation=(
                "The improvement is about the noise budget, not shared structure among "
                "the truths. In p dimensions the observed vector overshoots in squared "
                "length by about p sigma-squared no matter what theta is, and shrinking "
                "corrects that length error. Independence and 'exchangeability' are "
                "red herrings: the result needs neither a relationship nor a common "
                "meaning among the coordinates."
            ),
        ),
        Question(
            prompt=(
                "The James-Stein estimator carries the constant p minus 2 in its "
                "shrinkage factor. What is the significance of that particular "
                "constant?"
            ),
            options=(
                "It is a tunable hyperparameter that the analyst sets by "
                "cross-validation to control how aggressively the estimates shrink.",
                "It rescales the estimator so that each coordinate remains individually "
                "unbiased after the common shrinkage is applied.",
                "It is the exact value that makes the risk improvement come out "
                "negative for every theta, and it yields no gain until p is at "
                "least three.",
                "It equals the number of coordinates left over after two degrees of "
                "freedom are spent estimating the shrinkage center and calibrating "
                "the overall noise level.",
            ),
            answer=2,
            explanation=(
                "The p minus 2 is what forces the risk difference to favor shrinkage at "
                "all theta, and it is where the 'three or more' threshold lives: at "
                "p equal to 2 the factor yields no gain, and at p equal to 1 it does "
                "not apply. It is not a free tuning knob, and it does not preserve "
                "per-coordinate unbiasedness, which shrinkage deliberately gives up."
            ),
        ),
        Question(
            prompt=(
                "In high dimensions, why is the plain observed vector X almost always "
                "'too long' relative to the true mean vector theta?"
            ),
            options=(
                "Because independent noise concentrates in the same direction as theta, "
                "coherently adding to its length in a way that compounds across all of "
                "the coordinates as the dimension grows.",
                "Because squared-error loss systematically rewards larger estimates, "
                "biasing the maximum-likelihood solution outward.",
                "Because in many dimensions the noise lands nearly perpendicular to "
                "theta, so by Pythagoras the squared length grows by about p "
                "sigma-squared.",
                "Because the sample mean is a biased estimator whose bias points away "
                "from the origin and accumulates with dimension.",
            ),
            answer=2,
            explanation=(
                "Two generic high-dimensional directions are nearly orthogonal, so the "
                "noise adds to theta at close to a right angle and the squared length "
                "picks up the noise's own squared length, about p sigma-squared. The "
                "sample mean is unbiased, and squared error does not reward large "
                "estimates; the overshoot is a geometric fact about lengths, not a bias."
            ),
        ),
        Question(
            prompt=(
                "A colleague uses James-Stein to estimate 30 quantities, then reports "
                "the shrunken estimate of one particular quantity as if it were the "
                "best possible estimate of that quantity alone. What is the problem?"
            ),
            options=(
                "There is none, since dominance in total risk implies dominance in "
                "every coordinate once at least three are estimated together.",
                "The guarantee is about summed risk, so that single estimate may "
                "actually be worse than its plain sample mean.",
                "The estimate is invalid because James-Stein requires the reported "
                "quantity to share a prior with the other twenty-nine quantities.",
                "The problem is only that the shrinkage center was chosen from the data "
                "rather than fixed in advance, which voids the guarantee entirely.",
            ),
            answer=1,
            explanation=(
                "Total-risk dominance says nothing about any single coordinate; one can "
                "be pulled away from a genuinely far-from-center truth to help the sum. "
                "Dominance does not descend to each coordinate, no shared prior is "
                "required, and estimating the center from the data is standard and does "
                "not by itself void the result."
            ),
        ),
    ),
    "penalties-and-priors": (
        Question(
            prompt=(
                "Ridge and lasso start from the same least-squares fit and add a "
                "penalty on coefficient size. Holding the penalty strength fixed at "
                "some positive value, what is the essential difference in the fits "
                "they return?"
            ),
            options=(
                "Ridge keeps every coefficient nonzero but smaller, while lasso can "
                "drive some coefficients exactly to zero, yielding a sparse model.",
                "Ridge sets weak coefficients exactly to zero, while lasso shrinks "
                "every coefficient by the same fixed fraction toward zero.",
                "Both zero out weak coefficients, but ridge selects fewer of them "
                "because squaring penalizes small coefficients more heavily.",
                "Ridge leaves the coefficients unchanged and only rescales the "
                "intercept, while lasso rescales all of the slopes at once.",
            ),
            answer=0,
            explanation=(
                "The squared L2 penalty has zero slope at the origin, so it never "
                "pins a coefficient exactly at zero; the L1 penalty has a constant "
                "slope right up to zero, strong enough to hold weak coefficients "
                "there. That is why lasso does variable selection and ridge does not."
            ),
        ),
        Question(
            prompt=(
                "In the budget picture, the fit is where the elliptical residual "
                "contours first touch the region of allowed coefficients. Why does "
                "this make lasso sparse but not ridge?"
            ),
            options=(
                "The L1 region is a diamond with corners on the axes that an "
                "expanding ellipse tends to strike first, and a corner puts a "
                "coefficient at zero; the round L2 ball is met off-axis.",
                "The L1 region is larger than the L2 region, so an expanding ellipse "
                "reaches its boundary sooner and clips whichever single coefficient it "
                "happens to meet first on the way to the least-squares point.",
                "The L2 ball has flat faces aligned with the axes, so the ellipse "
                "meets it exactly on an axis and zeros that coefficient out.",
                "The residual contours are circular for lasso and elliptical for "
                "ridge, so only the lasso case can be tangent along a coordinate.",
            ),
            answer=0,
            explanation=(
                "Sparsity comes from the geometry of the constraint region, not from "
                "the data: the diamond's corners sit on the axes and catch the "
                "ellipse there. The residual contours are the same shape in both "
                "cases; only the region differs."
            ),
        ),
        Question(
            prompt=(
                "A penalized regression is exactly a MAP estimate. Under the "
                "standard Gaussian-error likelihood, which prior on the coefficients "
                "reproduces the ridge penalty, and which reproduces the lasso?"
            ),
            options=(
                "A Gaussian prior gives ridge and a Laplace prior gives lasso, "
                "because the negative log of each prior is the corresponding penalty.",
                "A Laplace prior gives ridge and a Gaussian prior gives lasso, "
                "because the heavier tails of the Laplace enforce smooth shrinkage.",
                "A uniform prior gives ridge and a Gaussian prior gives lasso, since "
                "only a bounded prior can force coefficients to exactly zero.",
                "A Gaussian prior gives both, with ridge using its mean and lasso "
                "using its mode as the point estimate reported.",
            ),
            answer=0,
            explanation=(
                "Taking minus the log of a zero-mean Gaussian density yields a sum of "
                "squares; minus the log of a Laplace density yields a sum of absolute "
                "values. The penalty strength maps to the prior width: a tighter "
                "prior means heavier shrinkage."
            ),
        ),
        Question(
            prompt=(
                "You run lasso on data with several strongly correlated predictors. "
                "It keeps one of them and zeros the rest. What is the safest reading "
                "of that result?"
            ),
            options=(
                "Lasso's choice among correlated predictors is unstable, so the "
                "selected one is one plausible story that can flip with a new sample, "
                "not proof the others have no effect.",
                "The zeroed predictors have been shown to carry no signal, since "
                "lasso only removes a variable once its true coefficient is zero.",
                "The kept predictor is guaranteed to be the one most strongly "
                "correlated with the response, because lasso ranks the predictors by "
                "their marginal correlation and keeps only the strongest one.",
                "Correlation among predictors makes lasso keep all of them, so any "
                "zeros you see must come from a bug in the optimizer.",
            ),
            answer=0,
            explanation=(
                "Among collinear predictors the L1 penalty tends to keep one almost "
                "arbitrarily and drop the rest, and which one survives is sample-"
                "dependent. This instability is exactly where ridge's habit of "
                "sharing weight across the cluster is an advantage."
            ),
        ),
        Question(
            prompt=(
                "Full Bayesian inference with a Laplace prior gives a posterior over "
                "the coefficients. How does its behavior at zero compare to the "
                "lasso's exact zeros?"
            ),
            options=(
                "The posterior mean is essentially never exactly zero, so lasso's "
                "exact zeros are a property of reporting the posterior mode, not of "
                "the Bayesian model itself.",
                "The posterior mean lands on exactly zero for the weak coefficients, "
                "so full Bayesian inference with a Laplace prior reproduces lasso's "
                "sparsity directly, with no separate point estimate needed.",
                "The posterior has no mode at zero, so the Laplace prior cannot "
                "produce sparsity under any point estimate you might report.",
                "The posterior mean and mode coincide for a Laplace prior, so mean "
                "and MAP give identical exact zeros.",
            ),
            answer=0,
            explanation=(
                "The smooth posterior places mass on both sides of zero, so its mean "
                "misses the axis; only the mode can sit exactly at zero. Lasso is MAP "
                "estimation, and its sparsity is an artifact of keeping the peak "
                "rather than the whole distribution."
            ),
        ),
        Question(
            prompt=(
                "When the true signal is spread thinly across many correlated "
                "predictors, ridge often predicts better than lasso. Why?"
            ),
            options=(
                "Forcing most coefficients to exactly zero discards real if faint "
                "structure, whereas ridge keeps every predictor and shares the weight "
                "across the correlated cluster.",
                "Ridge has lower bias than lasso in every setting, so it always wins "
                "on prediction once the predictors are correlated.",
                "Lasso cannot fit correlated predictors at all, so it returns the "
                "least-squares solution and overfits the noise.",
                "Ridge automatically selects the single best predictor from each "
                "correlated cluster and discards the others, giving a simpler and more "
                "accurate model than lasso does in this dense setting.",
            ),
            answer=0,
            explanation=(
                "When the truth is dense, sparsity throws away signal; ridge's smooth "
                "shrinkage keeps all the small effects and stabilizes correlated "
                "ones. When the truth is genuinely sparse, the tradeoff reverses and "
                "lasso's selection helps. Neither dominates."
            ),
        ),
    ),
    "choosing-the-penalty": (
        Question(
            prompt="Why can training error never be used to choose the penalty λ?",
            options=(
                "It falls monotonically as λ weakens, so it always crowns λ = 0, the most overfit model in the family.",
                "It is too expensive to evaluate at many candidate values of λ without holding out folds.",
                "It has the wrong units, measuring squared error where the penalty is stated in absolute terms.",
                "It equals the cross-validation error exactly, so it adds no information beyond what CV already gives.",
            ),
            answer=0,
            explanation="Weakening the penalty lets the fit bend harder toward the data, so training error only ever decreases as λ falls, bottoming out at λ = 0. It measures effort, not generalization. The gap between training error and held-out error is precisely the overfitting that training error cannot see.",
        ),
        Question(
            prompt="In k-fold cross-validation, what is each observation's contribution to CV(λ) computed from?",
            options=(
                "A model fit on every fold, including the one containing that observation, to use all the data.",
                "A model fit on the folds other than the one containing it, so the point is predicted unseen.",
                "The average of k separate models each fit on a single fold and scored on that same fold.",
                "A model fit on the whole dataset, then re-scored k times with different random seeds.",
            ),
            answer=1,
            explanation="Each point is scored by the model trained on the other k-1 folds, so its prediction is genuinely out-of-sample. Rotating the held-out fold predicts every point exactly once. This is what makes CV(λ) an estimate of generalization error rather than a restatement of training error.",
        ),
        Question(
            prompt="For ridge regression, the effective degrees of freedom equal the sum over the design's singular values of d_j^2 / (d_j^2 + λ). As λ grows from 0 to infinity, this quantity does what?",
            options=(
                "Stays fixed at the parameter count p, since the number of coefficients never changes.",
                "Jumps down by whole integers as coefficients are set exactly to zero one at a time.",
                "Slides continuously from p down to 0, passing through non-integer values in between.",
                "Rises from 0 up to p, because a larger penalty forces more directions to be estimated.",
            ),
            answer=2,
            explanation="Each term is a dimmer switch: near 1 when a direction's scale dwarfs λ, near 0 when λ dwarfs it. The sum starts at p (all terms 1) and decays smoothly to 0, so complexity becomes a continuous dial. Unlike the lasso, ridge never sets a coefficient exactly to zero; it fades them fractionally.",
        ),
        Question(
            prompt="What does the one-standard-error rule prescribe?",
            options=(
                "Pick the λ whose CV error is exactly one standard error below the overall minimum.",
                "Widen the folds until the standard error of the CV curve shrinks below one unit of loss.",
                "Take the smallest λ whose training error is within one standard error of the CV minimum.",
                "Take the largest λ whose CV error is still within one standard error of the minimum.",
            ),
            answer=3,
            explanation="It steps toward more regularization: among all λ within one fold-to-fold standard error of the best CV score, choose the largest, giving the simplest model that is statistically indistinguishable from the best. The reasoning is that differences smaller than the curve's own noise are not worth chasing.",
        ),
        Question(
            prompt="You standardize all features and select variables using the full dataset, then run cross-validation to tune λ. What is wrong?",
            options=(
                "Nothing, as long as the same standardization is reused unchanged inside every training fold.",
                "The preprocessing peeked at the held-out folds, so CV leaks information and reads optimistically.",
                "Standardizing changes the units of λ, so its selected value no longer matches the unscaled model.",
                "Variable selection should follow tuning, because λ determines how many variables to keep.",
            ),
            answer=1,
            explanation="Any step that looks at the whole dataset before the split lets the held-out folds influence the fit, so the CV score is no longer an honest out-of-sample estimate. Preprocessing must happen inside each fold. And once λ itself is tuned by CV, that score is optimistic too, so a final untouched test set is needed to judge the tuned model.",
        ),
        Question(
            prompt="Compared with five- or ten-fold CV, what is the characteristic drawback of leave-one-out cross-validation?",
            options=(
                "Its training sets are far too small, so every fitted model is badly biased toward underfitting.",
                "It cannot be applied to linear smoothers, since no closed-form held-out error exists for them.",
                "Its near-identical training sets make the fold scores highly correlated, inflating the estimate's variance.",
                "It systematically prefers larger λ, because each fit sees almost the entire dataset at once.",
            ),
            answer=2,
            explanation="Leave-one-out has low bias (training sets are nearly the full data) but its n folds overlap almost completely, so their scores are strongly correlated and the averaged estimate can have high variance. Five- or ten-fold CV trades a little bias for folds different enough to keep variance in check. For linear smoothers a closed form does exist, via the hat matrix diagonal.",
        ),
    ),
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
