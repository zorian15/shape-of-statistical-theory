You have met a parade of named distributions by now — normal, Bernoulli, Poisson, exponential, gamma, beta — and it can feel like a zoo you are asked to memorize, each animal with its own formula, its own mean, its own quirks. The load-bearing surprise of this chapter is that most of them are the *same* animal wearing different coats. They share one algebraic skeleton, the **exponential family**, and once you can see it, three things that otherwise look like separate strokes of luck line up as one fact read three ways: the data has a natural summary you can keep and throw the rest away, a Bayesian prior updates without leaving its own family, and the mean drops out of a single derivative.

This is a "why does this keep appearing" chapter, not a catalog. The aim is to show you the shared form, watch a couple of familiar distributions fall into it, and then say plainly what the form buys — and, just as usefully, where it stops.

## One form behind many faces

A family of distributions belongs to the *exponential family* if you can write its density (or, for discrete data, its mass function) in one particular shape. Introduced in words: the data $x$ enters through a fixed summary, that summary is multiplied by a repackaged version of the parameter, the whole product sits inside a single exponential, and a normalizer out front keeps it a valid probability. Written out:

$$p(x \mid \theta) = h(x)\,\exp\!\big(\eta(\theta)\cdot T(x) - A(\theta)\big).$$

Read it one piece at a time, because every piece has a job:

- $h(x)$ is the **base measure** — the part of the shape that does not move as $\theta$ changes. It carries whatever is true of $x$ regardless of the parameter (for counts, the $1/x!$; for many families, just $1$).
- $T(x)$ is the **sufficient statistic** — the *only* feature of $x$ that the parameter ever touches. Everything the family cares about in a data point is squeezed into this one function.
- $\eta(\theta)$ is the **natural parameter** — the parameter rewritten into the coordinate in which it multiplies $T(x)$ *linearly*. This repackaging is the whole trick: in the right coordinate the parameter and the data meet in a plain dot product.
- $A(\theta)$ is the **log-partition function** — the logarithm of whatever normalizing constant makes the density integrate to one, $A(\theta) = \log \int h(x)\,e^{\eta(\theta)\cdot T(x)}\,dx$. It is fully determined by the other three pieces, and, as the next section shows, it quietly stores the family's moments.

The entire content of the definition is that last exponent: $x$ shows up only through $T(x)$, and it does so linearly in $\eta$. Nothing else about $x$ is allowed to interact with the parameter.

Make it concrete with the humblest distribution there is. A **Bernoulli** coin with success probability $p$ has mass function $p(x\mid p) = p^{x}(1-p)^{1-x}$ for $x \in \{0,1\}$. Take the logarithm and regroup:

$$p(x \mid p) = \exp\!\Big(x\,\log\tfrac{p}{1-p} + \log(1-p)\Big).$$

Line it up against the template: $h(x)=1$, the sufficient statistic is $T(x)=x$, the natural parameter is $\eta = \log\frac{p}{1-p}$ — the **log-odds** — and $A = -\log(1-p) = \log(1+e^{\eta})$. The natural coordinate of a coin flip turns out to be its log-odds, which is exactly the quantity logistic regression models linearly. The **Poisson** falls in the same way: $p(x\mid\lambda)=\frac{\lambda^{x}e^{-\lambda}}{x!} = \frac{1}{x!}\exp(x\log\lambda - \lambda)$, so $h(x)=1/x!$, $T(x)=x$, $\eta=\log\lambda$, and $A=\lambda=e^{\eta}$.

<figure>
<img src="assets/figures/exponential-family-umbrella.svg" alt="A diagram. A header box holds the exponential-family formula p(x given theta) = h(x) exp(eta(theta) T(x) minus A(theta)). Ribs hang down to six labelled chips: Bernoulli with T(x)=x, Poisson with T(x)=x, Exponential with T(x)=x, Normal with T(x)=(x, x squared), Gamma with T(x)=(x, ln x), Beta with T(x)=(ln x, ln(1 minus x)). A separate dashed strip at the bottom holds Uniform on zero to theta and Cauchy, marked as outside the family.">
<figcaption>One skeleton, many coats. The familiar distributions differ only in what you plug in for h, T, and η — the sufficient statistic T(x) is the fingerprint. The dashed strip previews the last section: not everything fits, and the reasons are specific.</figcaption>
</figure>

!!! analogy "Analogy"
    The form is a coat rack, not a coat. $h$, $T$, $\eta$, and $A$ are the hooks; hang different functions on them and out comes the normal, the Poisson, the gamma. The analogy leaks where the hooks are not free: $A$ is forced by the other three (it is whatever normalizes them), so you cannot dress the rack arbitrarily. Choose $h$, $T$, $\eta$ and the normalizer is already decided.

!!! probe "A sharper question"
    *Why should one algebraic form be shared by something as different as coin flips and waiting times?* Because the form is precisely what you get when you commit to constraining *only* the average of some feature $T(x)$ and nothing else. Among all distributions with a prescribed value of $\mathbb{E}[T(X)]$, the one that assumes the least beyond that — the maximum-entropy distribution — has exactly this exponential shape, with $\eta$ playing the role of the constraint's price. Coins and waiting times look unrelated, but "fix the expected count" and "fix the expected wait" are the same kind of single-moment constraint, so they land on the same skeleton.

!!! note "Note"
    $T(x)$ need not be a single number. The normal with *both* mean and variance unknown is a two-parameter exponential family with vector statistic $T(x)=(x,\,x^{2})$: to pin down a Gaussian you keep the sum and the sum of squares. The gamma keeps $(x,\log x)$; the beta keeps $(\log x, \log(1-x))$. The dot product $\eta\cdot T$ just becomes a sum over coordinates.

## What the structure buys you

The form is not bookkeeping for its own sake. Three of the most useful facts in the subject fall straight out of it, and each is a preview of a chapter to come.

**A sufficient statistic falls out for free.** Suppose you draw an independent, identically distributed sample $x_1,\dots,x_n$ from an exponential family. Multiply the densities and the exponents simply add:

$$p(x_1,\dots,x_n \mid \theta) = \Big(\textstyle\prod_i h(x_i)\Big)\,\exp\!\Big(\eta(\theta)\cdot \textstyle\sum_i T(x_i) - n\,A(\theta)\Big).$$

Stare at where $\theta$ appears: only alongside the single quantity $\sum_i T(x_i)$. Once you know that sum (and $n$), the parameter cannot tell your actual dataset apart from any other dataset with the same sum. That is what it means for a statistic to be **sufficient** — it carries everything the sample knows about $\theta$, so you may keep it and discard the raw data with no loss. For a coin you keep the number of heads; for a Poisson stream, the grand total; the order and the individual values are irrelevant. And crucially, the summary's *size does not grow with $n$*: a million coin flips still compress to one count. Chapter 7 makes sufficiency precise through the factorization theorem, and the exponential form is the cleanest place it ever appears — the factorization is already staring at you in the equation above.

<figure>
<img src="assets/figures/sufficient-statistic.svg" alt="A diagram. On the left, a vertical stack of data chips labelled x-one, x-two, x-three, a vertical dots row, and x-n. Arrows from every chip converge into a single box on the right that reads T(x) equals the sum over i of T(x-i), with the notes that it carries all of theta's information and its size never grows with n.">
<figcaption>The whole sample funnels into one summary. Because the parameter meets the data only through Σ T(xᵢ), that fixed-size sum is all you need to keep — a preview of sufficiency (Chapter 7). Adding data updates the sum; it never enlarges what you store.</figcaption>
</figure>

**Priors update without leaving the family.** Turn to the Bayesian picture (Chapter 9), where you place a distribution on $\theta$ before seeing data and update it after. For an exponential family there is a matched family of priors — the **conjugate priors** — engineered so the posterior lands right back in the same family; the update just adjusts a couple of numbers rather than reshaping the whole distribution [@diaconis1979]. A Beta prior on a coin's $p$, met with Bernoulli data, gives a Beta posterior: you add your heads and tails to the prior's two counts and you are done. A Gamma prior on a Poisson rate stays Gamma. This is not a coincidence you get to be grateful for distribution by distribution; it is a structural consequence of the linear-in-$\eta$ exponent, which is why conjugacy and the exponential family are usually taught in the same breath.

**Moments and the MLE come from differentiating $A$.** The log-partition function looks like dead weight, but its derivatives are the moments of $T$. In the natural coordinate,

$$\frac{\partial A}{\partial \eta} = \mathbb{E}_\theta[T(X)], \qquad \frac{\partial^2 A}{\partial \eta^2} = \operatorname{Var}_\theta[T(X)].$$

The mean of the sufficient statistic is *one derivative* of the normalizer, and its variance is the second — a duality between the log-partition function and the family's cumulants that organizes a surprising amount of modern inference [@wainwright2008]. It also hands you maximum likelihood almost for free (Chapter 8): differentiate the sample log-likelihood, set it to zero, and the equation you get is $\mathbb{E}_\theta[T(X)] = \frac{1}{n}\sum_i T(x_i)$. The maximum-likelihood estimate is whatever parameter makes the *model's* average of $T$ equal the *data's* average of $T$. Fit becomes moment-matching, and it is the sufficient statistic that both sides are matching on.

!!! intuition "Intuition"
    The exponential form threads one needle through three rooms. The sufficient statistic $T$ is what the *data* reduces to, what a *prior* conjugates against, and what the *fit* matches in expectation. Sufficiency, conjugacy, and maximum likelihood are not three lucky properties of nice distributions; they are one property — the parameter touching the data only through a linear $T$ — seen from three doorways.

## Where the family ends

The exponential form is a wide net, but it is not the whole ocean, and the two most instructive misses tell you exactly what the structure was buying. Both break a single-line summary of the family: the parameter must touch the data *only* through $\eta\cdot T(x)$, on a support that does not itself depend on $\theta$.

The first classic outsider is the **uniform distribution on $[0,\theta]$**, with density $p(x\mid\theta)=\frac{1}{\theta}\mathbf{1}\{0\le x\le\theta\}$. The trouble is the indicator: the *set where the density is positive* slides as $\theta$ moves. You cannot fold a moving support into the template, because $h(x)$ is required to be a fixed function of $x$ alone and $A(\theta)$ a fixed function of $\theta$ alone — neither can encode "positive only up to $\theta$." Whenever the support depends on the parameter, the family is not exponential, full stop. This is the single most common way a distribution that otherwise looks tame falls outside.

<figure>
<img src="assets/figures/outside-the-family.svg" alt="Two side-by-side plots. The left plot shows three uniform densities on zero to theta for theta = one, 1.6, and 2.6 as flat rectangles of decreasing height whose right edges slide rightward, annotated that the support edge moves with theta. The right plot overlays a normal density and a Cauchy density over minus six to six; the Cauchy has a lower peak and visibly heavier tails, annotated that it has no moment-generating function.">
<figcaption>Two ways to fall out of the family. Left: the uniform's support edge moves with θ, which no fixed h(x) can encode. Right: the Cauchy's tails are too heavy for a moment-generating function to exist, so the tidy A-derivative machinery has nothing to compute.</figcaption>
</figure>

The second outsider keeps a fixed support but breaks the exponent a different way. The **Cauchy distribution**, $p(x\mid\theta)=\frac{1}{\pi\,(1+(x-\theta)^{2})}$, is a location family on all of the real line, so its support is fixed — yet it is not exponential family. Its tails are too heavy: it has no moment-generating function and not even a finite mean, so the "differentiate $A$ to get moments" machinery has nothing to grab. The practical shadow of this is stark. A Cauchy sample has *no* fixed-size sufficient statistic; to summarize where its center sits you essentially need the whole ordered sample, and the sample mean of Cauchy data is no more accurate than a single observation. Everything the previous section promised quietly fails, because the promise was made *to* the exponential family.

!!! warning "Common trap"
    "It has a low-dimensional sufficient statistic" is *not* the same as "it is exponential family." The uniform on $[0,\theta]$ is the counterexample: the maximum $\max_i x_i$ is a perfectly good one-number sufficient statistic, yet the family is not exponential. What the exponential family uniquely guarantees is a fixed-dimension sufficient statistic *together with* a support that does not move — the classical Pitman–Koopman–Darmois result says that, among families with fixed support, essentially only the exponential ones give you a sufficient statistic whose dimension stays put as the sample grows. Fixed support is doing real work in that sentence; drop it, as the uniform does, and the guarantee no longer applies.

!!! probe "A sharper question"
    *If the uniform on $[0,\theta]$ has a clean sufficient statistic anyway, what have I actually lost by leaving the exponential family?* You lose the package deal. Sufficiency you can sometimes still get by hand, as with the maximum. What you forfeit is that sufficiency, conjugacy, and moment-matching estimation all arrive together and behave smoothly. Off the family you are back to case-by-case work: the maximum-likelihood estimate of $\theta$ for the uniform is $\max_i x_i$, which is biased and has a non-normal, edge-of-support distribution — a reminder that the comfortable large-sample story of Chapter 8 is a story the exponential family tells particularly well, not a universal law.

Seen this way, the exponential family is less a list to memorize than a explanation for why the list is short. The distributions you keep meeting are the ones that constrain a few averages and nothing more, and that single design decision is what makes them summarizable, updatable, and fittable at once. When you next meet a distribution that resists all three, check its support and check its tails — one of them will usually have stepped outside the form.
