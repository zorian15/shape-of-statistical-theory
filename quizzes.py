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
