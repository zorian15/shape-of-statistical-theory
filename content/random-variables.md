Before you can estimate anything, judge a procedure, or trade bias against variance, you need a language for uncertainty — and that language is the *distribution*. A distribution is not a formula to memorize; it is a bookkeeping device that answers one question in every possible form: **where does the probability live?** This chapter takes the objects you have already met once — the CDF, the density, the mass function — and shows they are a single thing seen from three angles. Then it asks how distributions combine when you have more than one number to track, and pins down what independence actually buys you.

If you take one idea from this chapter, take this: **a distribution assigns a total budget of one unit of probability across the outcomes, and every tool — CDF, density, mass function, marginal, conditional — is just a different way of reading off how that budget is spent.**

## One object, three views

Start with the thing itself. A *random variable* is a number whose value is uncertain — formally, a function from outcomes to the real line, but for our purposes just "a measurement you have not made yet." Its *distribution* is the full account of how likely each value, or range of values, is. That account is the object; the CDF, density, and mass function are three notations for it, each natural in different terrain.

The one notation that always exists is the *cumulative distribution function* (CDF), written $F(x) = \mathbb{P}(X \le x)$: the probability that the variable lands at or below $x$. It sweeps a gate from $-\infty$ rightward and reports how much probability it has swept past. Because you are accumulating a budget of total size one, $F$ starts at $0$, ends at $1$, and never decreases — those three properties are not just features of the CDF, they *are* what it means to be a distribution. Every distribution has a CDF, whether the variable is continuous, discrete, or a mix of both. It is the universal view.

The other two views are derivatives of this one, in both senses. When $X$ is continuous, its *probability density function* (pdf) $f(x)$ is the *rate* at which the CDF climbs: $f(x) = F'(x)$, so that probability over an interval is the area underneath, $\mathbb{P}(a \le X \le b) = \int_a^b f(x)\,dx$. When $X$ is discrete — it can only land on a countable set of values — its *probability mass function* (pmf) $p(x) = \mathbb{P}(X = x)$ places a lump of probability directly on each value, and the CDF becomes a staircase that jumps by $p(x)$ at each one. Density smears the budget; mass stacks it in piles. Same budget, different bookkeeping.

<figure>
<img src="assets/figures/cdf-pdf.svg" alt="Two stacked panels showing the same continuous distribution. The top panel is a smooth bell-shaped density on the interval zero to one, peaking above the height of one, with the area to the left of a marked point x-nought shaded. The bottom panel is the corresponding S-shaped cumulative distribution function, rising from zero to one, with a dot at x-nought whose height equals the shaded area above, connected by dashed guide lines.">
<figcaption>One distribution, two views. The shaded area under the density (top) is exactly the height of the CDF (bottom) at the same point — the CDF accumulates what the density lays down. Notice the density peaks above 1: a density is a rate, not a probability, so its value is not capped.</figcaption>
</figure>

!!! intuition "Intuition"
    The CDF is the running total; the density (or mass) is the increment. Ask "how much probability by here?" and you want $F$; ask "how concentrated is it right here?" and you want $f$ or $p$. Neither is more fundamental — they are the odometer and the speedometer of the same trip.

!!! warning "Common trap"
    A density value $f(x)$ is **not** a probability. It is a probability *per unit of $x$* — a rate — and rates can exceed one. A distribution tightly concentrated on a narrow interval has a tall density there; the figure's density crests above $1.5$. What is bounded by one is the *area*, $\int f\,dx = 1$, never the height. The moment you read $f(x)$ as "the chance of $x$" you will mispredict, because for a continuous variable the chance of any single exact value is zero.

!!! probe "A sharper question"
    *If the probability of any exact value is zero for a continuous variable, in what sense does the density carry information at all?*
    In the sense of *comparisons and intervals*. The density says where probability is dense versus sparse: a region where $f$ is twice as high holds twice as much probability per unit width, so a small interval there is twice as likely. You never consume a density at a point; you integrate it over a set. The point value is a limit — probability of a shrinking window divided by the window's width — and it is that ratio, not any single-point chance, that the density reports.

Why keep three notations for one object? Because each makes a different calculation transparent. The CDF is what you want for "the probability of exceeding a threshold" or for defining quantiles (invert $F$). The density is what you integrate to get expectations (Chapter 3) and what you differentiate a likelihood from (Chapter 8). The pmf is the honest description when outcomes are genuinely discrete — counts, categories, successes — where writing a density would be a category error. Fluency is knowing which view collapses your problem to one line.

## Joint, marginal, conditional

One variable is rarely the whole story. The moment you track two quantities together — a person's height and weight, a stock's price today and tomorrow — you need the *joint distribution*, which spends the unit budget of probability over *pairs* $(x, y)$ rather than single values. In the continuous case it is a joint density $f(x, y)$, a landscape over the plane whose total volume is one; probability of a region is the volume sitting above it. Everything from one variable generalizes: the joint CDF is $F(x, y) = \mathbb{P}(X \le x, Y \le y)$, and for discrete pairs a joint pmf puts lumps on grid points.

From the joint you can always recover the behavior of one variable alone by *summing out* the other. The *marginal distribution* of $X$ is what you get by collapsing the joint along the $Y$ axis — integrating $y$ away, $f_X(x) = \int f(x, y)\,dy$ — which is exactly projecting the probability landscape onto the $x$ axis and reading off its shadow. The name is literal: imagine the joint pmf as a table, and the row and column sums written in the *margins* are the marginals. Marginalizing answers "forget $Y$; what does $X$ do?"

<figure>
<img src="assets/figures/joint-marginals.svg" alt="A central square heatmap showing a tilted elliptical joint density of two correlated variables X and Y, darker where probability is denser. Above the square sits the marginal density of X as a bell curve aligned to the horizontal axis; to the right sits the marginal density of Y as a bell curve aligned to the vertical axis. The marginals are the shadows the joint casts onto each axis.">
<figcaption>A joint density (center) and its two marginals (top and right). Each marginal is the shadow the joint casts on one axis — all of that variable's behavior with the other summed away. The tilt of the joint is correlation, and it is invisible in either shadow: the marginals cannot tell you the joint.</figcaption>
</figure>

The reverse move is *conditioning*. The *conditional distribution* of $Y$ given that $X$ took a specific value $x$ is what remains once you fix $X = x$ and renormalize: $f_{Y \mid X}(y \mid x) = f(x, y) / f_X(x)$. Geometrically you slice the joint landscape at $X = x$, getting a single ridge, then rescale that slice so its area is one again — because within the world where $X = x$, probability must still sum to a full unit. Conditioning is how new information updates a distribution, and it is the engine of the entire Bayesian view (Chapter 9): a posterior is just a conditional distribution of the unknown given the data.

!!! analogy "Analogy"
    A joint distribution is a topographic map of a mountain range; probability is elevation. The *marginal* of $X$ is the range's silhouette seen from the south — every east-west detail flattened into one skyline. The *conditional* given $X = x$ is the cross-section you get by slicing the range along one north-south line and looking at that wall face-on. The analogy leaks in the rescaling: a real cross-section keeps its literal height, but a conditional density is *renormalized* so its own area is one, because it is a fresh distribution over $Y$, not a raw slice.

These three operations are the complete grammar of combining distributions, and *independence* is the special case that makes the grammar collapse. Two variables are *independent* when knowing one tells you nothing about the other — when every conditional equals the corresponding marginal, $f_{Y \mid X}(y \mid x) = f_Y(y)$ for all $x$. Substitute that into the definition of conditioning and you get the fact that does all the work:

$$f(x, y) = f_X(x)\, f_Y(y).$$

Independence means the joint *factors* into its marginals. That is what independence buys you: the shadows determine the whole. In general the marginals badly under-determine the joint — the figure's tilt, the correlation, lives only in the joint and is erased in either shadow — but under independence there is no extra information to lose, and the two one-dimensional descriptions multiply back to the full two-dimensional one.

!!! intuition "Intuition"
    Independence turns a hard high-dimensional object into a product of easy low-dimensional ones. A joint distribution over $n$ variables is, in general, an $n$-dimensional landscape you cannot hope to write down. If the variables are independent, it is just $n$ separate one-dimensional distributions multiplied together — the curse of dimensionality dodged by assumption.

!!! note "Note"
    Independence is strictly stronger than "uncorrelated." Zero correlation only says the joint has no *linear* tilt; independence says the joint has *no* structure beyond its marginals at all. You can build variables that are uncorrelated yet fiercely dependent (put probability on a symmetric ring, and $X$ constrains $|Y|$ while their correlation is exactly zero). Correlation is one number; independence is a statement about the entire joint density.

!!! probe "A sharper question"
    *Why does the factorization of independence matter so much in practice — isn't it just a tidy formula?*
    Because it is the assumption that makes likelihoods tractable and the limit theorems fire. When you assume your data points are *independent and identically distributed* (i.i.d.), the joint density of the whole sample is the *product* of the individual densities, so the log-likelihood is a *sum* — the form maximum likelihood needs (Chapter 8) and the form the law of large numbers and central limit theorem require (Chapter 5). This same factor-into-a-product move reappears with a twist as the factorization theorem for sufficiency (Chapter 7). Independence is not a tidy formula; it is the hinge the rest of the book swings on.

With distributions in hand as the language, the next chapter asks what you can *summarize* about one: expectation, variance, and the moments that fingerprint a distribution (Chapter 3). Everything downstream — estimators, risk, the bias-variance tradeoff (Chapter 12) — is built on the account of where probability lives that you have just set up.
