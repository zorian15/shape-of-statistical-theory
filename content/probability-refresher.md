This appendix collects, in one scannable place, exactly the probability the chapters lean on — the load-bearing definitions, identities, inequalities, and limit results, stated compactly and cross-referenced to the chapters that develop them.
It assumes you have had a first probability course and that Part I has already built distributions, expectation, and the limit theorems in depth; nothing here re-teaches those, it reminds you of the facts and points back.
Treat it as a cheat-sheet, not a chapter: each entry is the fact you reach for, with a pointer to where the reasoning lives.

## Distributions, conditioning, and independence

Probability begins with a *sample space* $\Omega$ — the set of every outcome an experiment could produce — and *events*, the subsets of $\Omega$ you can assign a probability to.
A probability $\mathbb{P}$ obeys the three *probability axioms* (Kolmogorov's): $\mathbb{P}(A) \ge 0$ for every event, $\mathbb{P}(\Omega) = 1$, and *countable additivity* — for disjoint events the probability of their union is the sum of their probabilities.
Every rule below is derived from these three.

A *random variable* $X$ is a number whose value is uncertain, formally a function from outcomes to the real line; its distribution says where its probability lives.
That distribution has three interchangeable notations, developed fully in random variables and distributions, Chapter 2:

$$F(x) = \mathbb{P}(X \le x), \qquad f(x) = F'(x), \qquad p(x) = \mathbb{P}(X = x).$$

The *cumulative distribution function* (CDF) $F$ always exists, runs from $0$ to $1$, and never decreases.
The *probability density function* (pdf) $f$ is its slope for a continuous $X$, so probability over an interval is area, $\mathbb{P}(a \le X \le b) = \int_a^b f$; the *probability mass function* (pmf) $p$ is the direct probability of each value for a discrete $X$.
A density is a rate, not a probability: $f(x)$ can exceed one, only the area is capped at one.

<figure>
<img src="assets/figures/cdf-pdf.svg" alt="Two stacked panels of one continuous distribution: a bell-shaped density on top with the area left of a point shaded, and the S-shaped CDF below whose height at that point equals the shaded area.">
<figcaption>The two continuous views. The area the density (top) lays down to the left of a point is exactly the height the CDF (bottom) has accumulated there. Reach for F to ask "how much probability by here?" and for f to ask "how dense is it right here?"</figcaption>
</figure>

Track two variables at once and you need the *joint distribution*, which spends the unit of probability over pairs.
From it you recover either variable alone by summing the other away (the *marginal*), or fix one and renormalize (the *conditional*):

$$f_X(x) = \int f(x, y)\,dy, \qquad f_{Y \mid X}(y \mid x) = \frac{f(x, y)}{f_X(x)}.$$

The marginal is the joint's shadow on one axis; the conditional is a renormalized slice through it.
Correlation lives only in the joint and is erased in either shadow — the marginals do not determine the joint.

<figure>
<img src="assets/figures/joint-marginals.svg" alt="A central heatmap of a tilted elliptical joint density of two correlated variables, with the marginal density of one variable drawn above it and the marginal of the other drawn to its right, each a bell curve.">
<figcaption>A joint density and its two marginals. Each marginal is what one variable does with the other summed away — the joint's shadow on an axis. The tilt, the correlation, survives in neither shadow: shadows do not reconstruct the object.</figcaption>
</figure>

Two variables are *independent* when knowing one tells you nothing about the other, which is exactly when every conditional equals the matching marginal and the joint factors:

$$f(x, y) = f_X(x)\, f_Y(y).$$

Data assumed *independent and identically distributed* (i.i.d.) — mutually independent draws sharing one distribution — have a joint density that is the product of the individual densities, which is why the log-likelihood is a sum and the limit theorems fire (Chapter 2).
Conditioning also runs the Bayesian engine through *Bayes' rule*, which reverses the direction of a conditional:

$$\mathbb{P}(A \mid B) = \frac{\mathbb{P}(B \mid A)\, \mathbb{P}(A)}{\mathbb{P}(B)}.$$

!!! warning "Common trap"
    Uncorrelated is weaker than independent. Zero covariance rules out only a *linear* relationship; independence rules out *every* dependence. Uncorrelated-but-dependent variables are easy to build (place mass symmetrically on a ring), so never read "uncorrelated" as "independent."

## Expectation, variance, and useful inequalities

The *expectation* $\mathbb{E}[X]$ is the probability-weighted average of $X$, the balance point of its distribution, developed with the moments in expectation, moments, and their uses, Chapter 3.
Its workhorse property is *linearity*, which holds whether or not the variables are independent:

$$\mathbb{E}[aX + bY] = a\,\mathbb{E}[X] + b\,\mathbb{E}[Y].$$

To average a *function* of $X$ you do not need the distribution of that function — the *law of the unconscious statistician* (LOTUS) integrates $g$ against the distribution you already have:

$$\mathbb{E}[g(X)] = \int g(x)\, f(x)\,dx.$$

*Variance* measures spread, $\operatorname{Var}(X) = \mathbb{E}[(X - \mu)^2] = \mathbb{E}[X^2] - \mu^2$, and *covariance* measures joint movement, $\operatorname{Cov}(X, Y) = \mathbb{E}[(X - \mu_X)(Y - \mu_Y)]$.
Variance is *not* linear: the cross term makes

$$\operatorname{Var}(aX + bY) = a^2 \operatorname{Var}(X) + b^2 \operatorname{Var}(Y) + 2ab\,\operatorname{Cov}(X, Y),$$

so variances add only when the variables are uncorrelated.
The *moment generating function* (MGF) $M_X(t) = \mathbb{E}[e^{tX}]$ is a fingerprint: where it exists near zero it pins the distribution down uniquely, its derivatives at zero return the moments, and it turns sums of independent variables into products (Chapter 3).

<figure>
<img src="assets/figures/moment-shapes.svg" alt="Three small density panels showing how successive moments shape a distribution: the mean sets location, the variance sets width, and the third and fourth moments set skew and tail weight.">
<figcaption>The moments fingerprint a distribution. Mean fixes where it sits, variance how wide, and the higher moments its asymmetry and tail weight — the same information the MGF packages so that matching MGFs means matching distributions.</figcaption>
</figure>

Conditioning has an expectation of its own.
The *conditional expectation* $\mathbb{E}[Y \mid X]$ is the mean of $Y$ within each slice $X = x$, itself a random variable (a function of $X$).
Averaging it back over $X$ recovers the plain mean — the *law of total expectation*, or *tower property* — and the spread decomposes the same way, into within-slice and between-slice pieces, by the *law of total variance*:

$$\mathbb{E}\big[\mathbb{E}[Y \mid X]\big] = \mathbb{E}[Y], \qquad \operatorname{Var}(Y) = \mathbb{E}\big[\operatorname{Var}(Y \mid X)\big] + \operatorname{Var}\big(\mathbb{E}[Y \mid X]\big).$$

Conditional expectation is also the object sufficiency is built on: conditioning on a sufficient statistic loses no information about the parameter (sufficiency and information, Chapter 7).

Three inequalities carry most of the weight in proofs.
*Jensen's inequality* says a convex function and an average do not commute — the function of the mean sits below the mean of the function:

$$g(\mathbb{E}[X]) \le \mathbb{E}[g(X)] \quad (g \text{ convex}).$$

*Markov's inequality* bounds how much mass a nonnegative variable can push into its right tail, and squaring the deviation turns it into *Chebyshev's inequality*, a distribution-free bound on being far from the mean:

$$\mathbb{P}(X \ge a) \le \frac{\mathbb{E}[X]}{a} \quad (X \ge 0), \qquad \mathbb{P}\big(|X - \mu| \ge k\sigma\big) \le \frac{1}{k^2}.$$

<figure>
<img src="assets/figures/chebyshev-bound.svg" alt="A bell density centered at the mean with the two tails beyond two standard deviations on each side shaded. Dashed vertical lines mark mu minus k sigma and mu plus k sigma, and a label notes the Chebyshev ceiling of one over k squared, which is one quarter for k equal to two, well above the small actual tail mass.">
<figcaption>Chebyshev's bound is universal but loose. The shaded mass beyond k standard deviations can be no more than 1/k² for any distribution with a finite variance — here 1/4 at k = 2 — even though a bell keeps only about 5% out there. It buys you a guarantee that needs no knowledge of the shape, which is exactly why the weak law of large numbers falls out of it.</figcaption>
</figure>

!!! intuition "Intuition"
    Chebyshev converts a shrinking variance directly into a shrinking chance of being far off, with no distributional assumption at all. That is the whole mechanism behind the weak law of large numbers: drive $\operatorname{Var}(\bar X_n) = \sigma^2/n$ to zero and the probability of straying from $\mu$ is squeezed to zero with it.

!!! probe "A sharper question"
    *If Chebyshev is so loose — 25% where the truth is 5% — why lean on it?*
    Because it asks almost nothing in return: only a finite variance, no shape, no tail behavior, no independence. That universality is the point. When you know the distribution you can do far better (the central limit theorem gives the sharp normal tail), but when you know only that a variance exists, Chebyshev is often the *only* bound available, and it is enough to prove consistency.

## Convergence and the limit theorems

A sequence of random variables can approach a limit in several inequivalent senses, laid out in full in convergence and the limit theorems, Chapter 5.
Four modes matter here.
*Convergence in probability* ($X_n \xrightarrow{p} X$): for every tolerance $\varepsilon > 0$, $\mathbb{P}(|X_n - X| > \varepsilon) \to 0$.
*Almost sure convergence* ($X_n \xrightarrow{a.s.} X$): the observed path itself converges, $\mathbb{P}(\lim_n X_n = X) = 1$.
*Convergence in mean square*: $\mathbb{E}[(X_n - X)^2] \to 0$, a statement about the average squared gap.
*Convergence in distribution* ($X_n \xrightarrow{d} X$): the CDFs converge, $F_n(x) \to F(x)$ at every continuity point of $F$ — a statement about shape, not location.

The modes are ordered, and the arrows run one way only:

$$X_n \xrightarrow{a.s.} X \ \Longrightarrow\ X_n \xrightarrow{p} X \ \Longrightarrow\ X_n \xrightarrow{d} X, \qquad X_n \xrightarrow{m.s.} X \ \Longrightarrow\ X_n \xrightarrow{p} X.$$

Convergence in probability does *not* imply almost sure convergence, and convergence in distribution implies the rest only when the limit is a constant.

<figure>
<img src="assets/figures/convergence-modes.svg" alt="Three nested rounded boxes: the outermost labelled convergence in distribution and marked weakest, an inner box labelled convergence in probability, and the innermost labelled almost sure convergence and marked strongest, with an arrow pointing outward annotated implies.">
<figcaption>The modes nest, strongest inside weakest. Each inner mode implies every outer one and no reverse arrow holds in general. The law of large numbers lives in the inner two rings; the central limit theorem lives in the outermost.</figcaption>
</figure>

For an i.i.d. sample with mean $\mu$ and finite variance $\sigma^2$, the two limit theorems describe the sample mean $\bar X_n$.
The *law of large numbers* (LLN) says it settles on the truth, $\bar X_n \xrightarrow{p} \mu$ (weak law) or $\bar X_n \xrightarrow{a.s.} \mu$ (strong law).
The *central limit theorem* (CLT) says how it fluctuates on the way, once magnified by $\sqrt{n}$:

$$\sqrt{n}\,(\bar X_n - \mu) \ \xrightarrow{d}\ \mathcal{N}(0, \sigma^2), \qquad \text{equivalently} \quad \bar X_n \approx \mathcal{N}\!\Big(\mu, \tfrac{\sigma^2}{n}\Big).$$

The source distribution vanishes from the right-hand side: only the mean and variance survive, which is why the spread $\sigma/\sqrt{n}$ — the *standard error* — is the margin you attach to an average.

<figure>
<img src="assets/figures/lln-settling.svg" alt="Running sample means for three independent streams plotted against a logarithmic sample size axis, all funneling toward a dashed line at the true mean while a shaded band around it narrows like one over the square root of n.">
<figcaption>The law of large numbers in one picture. Three running averages start scattered and lock onto the true mean as n grows, their fluctuations squeezed like 1/√n — the very rate the central limit theorem then makes exact.</figcaption>
</figure>

<figure class="widget" data-widget="clt">
<figcaption>Figure A.3. The central limit theorem in action: averages of a skewed source pull into the bell as the sample size grows.</figcaption>
</figure>

Two tools let you carry these limits through transformations.
The *continuous mapping theorem* says a continuous $g$ preserves convergence: if $X_n \to X$ (in probability or in distribution), then $g(X_n) \to g(X)$ in the same mode.
*Slutsky's theorem* handles a converging-in-distribution term combined with one that converges to a constant: if $X_n \xrightarrow{d} X$ and $Y_n \xrightarrow{p} c$, then $X_n + Y_n \xrightarrow{d} X + c$ and $X_n Y_n \xrightarrow{d} cX$ (and $X_n / Y_n \xrightarrow{d} X/c$ for $c \ne 0$).
Slutsky is what lets you replace an unknown $\sigma$ by a consistent estimate inside a CLT statement without disturbing the limit.

The *delta method* pushes the CLT through a smooth transformation.
If $\sqrt{n}\,(\hat\theta_n - \theta) \xrightarrow{d} \mathcal{N}(0, \sigma^2)$ and $g$ is differentiable with $g'(\theta) \ne 0$, then

$$\sqrt{n}\,\big(g(\hat\theta_n) - g(\theta)\big) \ \xrightarrow{d}\ \mathcal{N}\big(0,\ g'(\theta)^2\, \sigma^2\big).$$

The one-line idea: linearize $g$ by its tangent at $\theta$, so $g(\hat\theta_n) - g(\theta) \approx g'(\theta)\,(\hat\theta_n - \theta)$, and a linear image of an asymptotically normal quantity is asymptotically normal with the slope squared into the variance.
These three results are the machinery behind the asymptotic normality of estimators and their standard errors (asymptotic efficiency, Chapter 19), and behind the resampling approximations of the bootstrap, Chapter 20.

!!! intuition "Intuition"
    The delta method is the CLT seen through a magnifying lens of curvature: near $\theta$ the function $g$ looks like its tangent line, and a straight-line transformation only rescales a bell by its slope. A steep $g$ stretches the noise (a large $g'(\theta)^2$), a flat one compresses it, and a stationary point ($g'(\theta) = 0$) breaks the first-order method entirely.
