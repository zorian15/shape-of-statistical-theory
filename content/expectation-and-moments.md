A distribution is a whole cloud of possibilities, but most of the time you want to reason about it with a single number — its center, its spread, its lopsidedness. This chapter is about how to extract those numbers, starting with the most important one. Expectation is the probability-weighted average of a random variable: every possible value pulls on the answer in proportion to how likely it is. Almost everything else in the book — bias, variance, risk, the law of large numbers — is expectation wearing a different hat.

If you take one idea from this chapter, take this: **expectation is a linear operator, and that linearity holds whether or not the pieces are independent.** It is the quiet workhorse that makes hard problems fall apart into easy ones.

## Expectation, and the one property that runs everything

The *expectation* (or *expected value*, or *mean*) of a random variable $X$ is what you get by averaging its values, each weighted by its probability. For a discrete variable it is a sum, and for a continuous one an integral, but it is the same idea both times:

$$\mathbb{E}[X] = \sum_x x\,p(x) \qquad\text{or}\qquad \mathbb{E}[X] = \int x\,f(x)\,dx,$$

where $p$ is the mass function and $f$ the density from Chapter 2. The name "expected value" is a little misleading — it need not be a value $X$ ever takes. A fair die has $\mathbb{E}[X] = 3.5$, which you will never roll. It is the long-run average, the number the sample mean settles toward as you collect more data (that convergence is the law of large numbers, Chapter 5).

!!! analogy "Analogy"
    Think of the distribution as a set of weights placed along a rod, each value a position and each probability the mass sitting there. The expectation is the *balance point* — the spot where the rod would sit level on a fulcrum. This is exactly right, and it is why a long tail on one side drags the mean toward it. The analogy leaks in two places worth remembering: the balance point can sit where there is no mass at all (nothing lives at 3.5 on the die), and a rod with an infinitely heavy far tail has no balance point — a foreshadowing of the trap below.

<figure>
<img src="assets/figures/center-of-mass.svg" alt="A distribution drawn as vertical bars of different heights standing on a horizontal rod, with a triangular fulcrum placed under the rod at the mean. The bars are tallest on the left and trail off to the right in a long low tail; the fulcrum sits to the right of the tallest bar, pulled that way by the tail. A dashed line marks the mean, and a separate short tick marks the median to its left.">
<figcaption>Expectation is the balance point of the distribution's mass. The long right tail carries little probability but a lot of leverage, so it drags the mean to the right of the median and of the most likely value. "Center" here means center of mass, not most typical.</figcaption>
</figure>

The property that makes expectation indispensable is *linearity*. Scaling and shifting pass straight through, and — this is the surprising part — the expectation of a sum is the sum of the expectations, always:

$$\mathbb{E}[aX + bY] = a\,\mathbb{E}[X] + b\,\mathbb{E}[Y].$$

*Linearity of expectation* asks nothing of $X$ and $Y$. They can be wildly dependent, even deterministic functions of each other, and the identity still holds exactly. This is what makes it a workhorse: to find the expected value of a complicated sum, you never have to understand how the pieces interact — you break the sum into parts, average each part alone, and add.

The classic demonstration is the hat-check problem. Handed back $n$ hats at random, how many people expect to get their own? Let $X_i$ be $1$ if person $i$ gets their own hat and $0$ otherwise. These indicators are tangled together — if the first $n-1$ people have their hats, the last one must too — so their joint behavior is a mess. But you never touch it. Each person has one chance in $n$ of a match, so $\mathbb{E}[X_i] = 1/n$, and

$$\mathbb{E}\Big[\textstyle\sum_i X_i\Big] = \sum_i \mathbb{E}[X_i] = n \cdot \tfrac{1}{n} = 1,$$

no matter how large $n$ is. On average, exactly one person gets their hat. Computing this from the distribution of the total would be painful; linearity makes it a line.

!!! intuition "Intuition"
    Expectation is an *integral*, and integrals are linear — they add up. Whether two quantities move together changes their joint distribution, but the expectation of each one alone reads only off its own margin, so summing expectations never asks the two margins to talk.

!!! probe "A sharper question"
    *If dependence breaks the product rule — $\mathbb{E}[XY] \neq \mathbb{E}[X]\,\mathbb{E}[Y]$ when $X$ and $Y$ are correlated — why does it spare the sum rule?*
    Because the two rules read different things off the joint distribution. The expectation of a **sum** only needs each variable's marginal distribution, and the marginals are unaffected by how the variables are coupled. The expectation of a **product** genuinely probes the joint distribution — it asks how the two move together — so correlation shifts it. Independence is the extra ingredient that makes the product factor; the sum never needed it. This is why variance, which involves a square, is *not* linear across dependent variables, while the mean is.

!!! warning "Common trap"
    A distribution need not have a mean at all. The Cauchy distribution — the bell-shaped curve you get as the ratio of two independent standard normals — has tails so heavy that $\int x\,f(x)\,dx$ does not converge, so $\mathbb{E}[X]$ simply does not exist. This is not a technicality: sample means of Cauchy data never settle down, so the law of large numbers fails outright (Chapter 5). Before you write $\mathbb{E}[X]$, you are quietly assuming the balance point exists. For heavy-tailed data it may not, and reaching for the mean anyway is a real mistake.

## Moments: the shape past the center

The mean locates a distribution but says nothing about its shape. To capture shape, you average not $X$ but its *powers* — and those averages are the *moments*. The $k$-th moment is $\mathbb{E}[X^k]$; more useful for shape are the *central moments*, which measure powers of the deviation from the mean, $\mathbb{E}[(X - \mu)^k]$, where $\mu = \mathbb{E}[X]$. Each higher power tells you something the lower ones cannot.

The second central moment is the *variance (of a distribution)*, the average squared distance from the mean:

$$\operatorname{Var}(X) = \mathbb{E}\big[(X - \mu)^2\big].$$

Its square root, the *standard deviation*, restores the original units and is the honest measure of spread. (This is the population version of the estimator variance from the bias–variance decomposition, Chapter 12 — same formula, applied to a distribution rather than to a $\hat\theta$.) Squaring is what costs linearity: $\operatorname{Var}(X+Y) = \operatorname{Var}(X) + \operatorname{Var}(Y)$ only when $X$ and $Y$ are uncorrelated, because the cross term $2\,\mathbb{E}[(X-\mu_X)(Y-\mu_Y)]$ — the covariance — survives otherwise.

The third and fourth central moments, once standardized by dividing out the scale, name two features of shape you can see by eye. *Skewness* is the standardized third central moment; it measures asymmetry, and its sign tells you which tail is longer — positive for a long right tail, zero for anything symmetric. *Kurtosis* is the standardized fourth central moment; it measures how much of the variance comes from rare, extreme deviations, so it reads *tail weight*. The normal distribution has kurtosis $3$, and people often subtract that off to define *excess kurtosis*, so that positive means heavier-tailed than a normal and negative means lighter.

<figure>
<img src="assets/figures/moment-shapes.svg" alt="Three side-by-side panels, each overlaying two probability density curves. The first panel, labeled variance, shows two symmetric bell curves with the same center but one much narrower and taller than the other. The second panel, labeled skewness, shows a symmetric bell and a right-leaning humped curve with a long tail to the right, both sharing the same mean marked by a vertical line. The third panel, labeled kurtosis, shows two curves with the same center and spread, but one has a sharper peak and fatter tails than the other.">
<figcaption>Three distributions can share a mean and still differ in shape. Variance controls spread, skewness controls which way the distribution leans, and kurtosis controls how much weight sits in the tails. Each higher moment captures a feature the lower ones are blind to.</figcaption>
</figure>

!!! intuition "Intuition"
    Read the moments in order as a zoom-out. The first fixes *where* the distribution sits, the second *how wide*, the third *which way it leans*, the fourth *how fat its tails are*. Each answers a question the previous ones left open.

!!! note "Note"
    Moments do not always pin a distribution down. There are genuinely different distributions — the lognormal and certain perturbations of it are the standard example — that share *every* moment, all infinitely many, yet are not the same distribution. So knowing all the moments is not, in general, the same as knowing the law. This is the "moment problem," and it is exactly the gap the next section's tool closes when it exists.

## The moment generating function: a distribution's fingerprint

Instead of computing moments one at a time, you can pack all of them into a single function. The *moment generating function* (MGF) of $X$ is the expected value of $e^{tX}$, viewed as a function of the auxiliary variable $t$:

$$M_X(t) = \mathbb{E}\big[e^{tX}\big].$$

The name is literal. Expand $e^{tX}$ as its power series and take expectations term by term, and the moments fall out as the coefficients — equivalently, differentiate $M_X$ at $t = 0$ and the $k$-th derivative is the $k$-th moment, $M_X^{(k)}(0) = \mathbb{E}[X^k]$. One function, differentiated repeatedly at the origin, *generates* the entire sequence of moments.

The MGF earns its keep through two properties. First, **when it exists in an interval around $t = 0$, it determines the distribution uniquely** — no two different distributions share an MGF on such an interval. That makes it a *fingerprint*: recognize the MGF and you have identified the law, no matter how it was described to you. Second, and this is where it turns labor into arithmetic, **the MGF of a sum of independent variables is the product of their MGFs**:

$$M_{X+Y}(t) = M_X(t)\,M_Y(t) \qquad (X, Y \text{ independent}).$$

<figure>
<img src="assets/figures/mgf-convolution.svg" alt="A diagram with two horizontal lanes. The top lane, labeled densities, shows a box for the law of X and a box for the law of Y joined by a convolution symbol, with an arrow leading to a box for the law of X plus Y; this arrow is tagged as requiring an integral and marked hard. The bottom lane, labeled moment generating functions, shows a box for the MGF of X and a box for the MGF of Y joined by a multiplication sign, with an arrow to a box for the MGF of X plus Y, tagged as just a product and marked easy. Dashed vertical arrows connect each density box to the MGF box below it, labeled as the same law in two languages.">
<figcaption>Why the MGF is worth the detour. Adding independent variables convolves their densities — an integral that is painful to do directly. Transform to MGFs and the same operation becomes plain multiplication; transform back and you have the answer. The fingerprint property guarantees the round trip is unambiguous.</figcaption>
</figure>

To see why the second property matters, recall what adding independent variables does to their densities: it *convolves* them, an integral that smears one distribution across the other. Convolutions are genuinely unpleasant to compute. The MGF converts that convolution into ordinary multiplication, so you can find the distribution of a sum by multiplying two functions and then recognizing the fingerprint of the result. This is how you prove, in a line each, that the sum of independent normals is normal, the sum of independent Poissons is Poisson, and the sum of independent gammas with a common rate is gamma: multiply the MGFs and read off the answer.

!!! probe "A sharper question"
    *You keep saying "when it exists" — when doesn't it, and what do you do then?*
    The MGF is an average of $e^{tX}$, which explodes if the tails of $X$ are heavy, so $M_X(t)$ is finite near $t = 0$ only when the tails decay at least exponentially. The Cauchy distribution from the last section has no MGF anywhere but at the origin; the lognormal has none for any positive $t$. The fix is the *characteristic function*, $\mathbb{E}[e^{itX}]$ with an imaginary exponent, which replaces the runaway $e^{tX}$ with a bounded oscillation $e^{itX}$ of magnitude one. It therefore exists for *every* distribution while keeping both magic properties — it uniquely determines the law and turns sums into products. The MGF is the friendlier tool when it exists; the characteristic function is the one that always does, and it is the machine behind the central limit theorem (Chapter 5).

!!! warning "Common trap"
    A finite mean and variance do not guarantee an MGF. A distribution can have every moment finite and still have no moment generating function — the lognormal is the standard cautionary case, since its moments grow fast enough that the series defining $M_X(t)$ diverges for all $t > 0$. "Has all its moments" is strictly weaker than "has an MGF," which is why the uniqueness guarantee is stated for the MGF (or characteristic function), not for the moment sequence.

Expectation and its moments are the vocabulary the rest of the book speaks in. Estimators are judged by the mean and variance of their sampling distributions (Chapter 6), risk is an expectation of loss (Chapter 11), and the exponential family of Chapter 4 is organized precisely around the moment structure the MGF exposes. Learn to see a distribution through its first few moments, and you will have the summary that most of statistics actually operates on.
