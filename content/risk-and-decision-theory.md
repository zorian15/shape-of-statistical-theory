You have a procedure — an estimator, a classifier, any rule that turns data into a decision — and you want to know whether it is any good *before* you run it on a single dataset. You cannot grade it on the answer, because you do not know the truth. What you can do is average its mistake over all the datasets the truth could have produced. That average is the procedure's risk, and the surprise of this chapter is that risk is not one number but a whole curve over the unknown parameter, so "best" turns out to mean three different things depending on how you feel about that curve.

If you take one idea from this chapter, take this: **a procedure's risk is a curve over the unknown parameter, and because no single rule sits lowest everywhere, calling one "best" forces you to choose an attitude — beat it everywhere, guard the worst case, or bet on a prior.**

## Risk as expected loss

Start by naming the thing you are grading. A **decision rule** $\delta$ is any function from the observed data $X$ to an action — for estimation, $\delta(X)$ is your guess $\hat\theta$; the estimators of Chapters 6 through 9 are all decision rules, and so is a rule that outputs "reject" or "accept." Chapter 10 gave you a **loss function** $L(\theta, a)$ that scores a single action $a$ against the truth $\theta$: squared error $(\theta - a)^2$, absolute error $|\theta - a|$, or 0–1 loss for a decision. The catch is that $\delta(X)$ is random, because $X$ is random, so the loss $L(\theta, \delta(X))$ is a random number you cannot know in advance. The fix is the one move that makes decision theory possible: average the loss over the sampling distribution of the data, the distribution $X$ follows when the parameter equals $\theta$.

That average is the **risk function**:

$$R(\theta, \delta) \;=\; \mathbb{E}_{X \sim p(\cdot \mid \theta)}\big[\,L(\theta, \delta(X))\,\big].$$

Read the subscript carefully, because it is the whole point: the expectation is taken with the truth fixed at $\theta$, over every dataset that value of $\theta$ could generate. So $R(\theta, \delta)$ is a *function of the unknown parameter* — one height for each possible truth. A decision rule does not have *a* risk; it has a risk curve. Under squared-error loss this curve is exactly the mean squared error of Chapter 12, which is why $R(\theta, \delta) = \text{bias}(\theta)^2 + \text{variance}(\theta)$ there — the bias-variance split is the risk curve of one particular loss, read pointwise in $\theta$.

!!! intuition "Intuition"
    Risk is the score a procedure would earn if you replayed the experiment forever at a fixed truth and averaged the mistakes. Since you do not know the truth, you get one such score for every candidate value of it — a curve, not a number — and comparing procedures means comparing whole curves.

Now the comparison. The cleanest thing you can hope for is that one rule's curve sits entirely below another's. Say rule $\delta_A$ has risk no higher than $\delta_B$ at every $\theta$, and strictly lower for at least one $\theta$; then $\delta_A$ **dominates** $\delta_B$, and there is no reason on earth to use $\delta_B$ — you can do at least as well everywhere and better somewhere. A rule that some other rule dominates is called **inadmissible**; a rule that nothing dominates is **admissible**. Admissibility is the floor, not the ceiling: it only says you cannot be beaten *everywhere at once*, which is a bar you should insist on but which does not, by itself, pick a winner.

<figure>
<img src="assets/figures/risk-curves.svg" alt="Risk plotted against the unknown parameter theta for three rules. A flat blue line at height one is the MLE. A red parabola sitting entirely above the blue line is an inflated rule, labeled inadmissible. An amber parabola dips to one quarter at theta equals zero, well below the blue line, then rises and crosses it at theta equals plus and minus the square root of three.">
<figcaption>Risk is a curve, and dominance is a curve sitting weakly below another. The inflated rule (red) is above the MLE everywhere, so it is inadmissible — never use it. The shrinkage rule (amber) beats the MLE near zero but loses in the tails; the curves cross, so neither dominates, and no ordering can call one of them simply "better."</figcaption>
</figure>

The figure shows the trap in miniature. The inflated rule $\delta(x) = 1.3x$ is easy to discard: its curve floats above the MLE's flat line everywhere, so it is inadmissible. But the shrinkage rule $\delta(x) = x/2$ dips *below* the MLE near $\theta = 0$ and rises *above* it in the tails — the curves cross. Neither dominates the other, and this crossing is the normal situation, not a pathology. Most sensible rules are admissible, their curves weaving over and under one another, and admissibility leaves you holding a whole shortlist with no way to rank it.

!!! warning "Common trap"
    "Admissible" does not mean "good," and "inadmissible" does not always mean "bad." An admissible rule can be terrible everywhere — the constant rule $\delta(x) = 7$, which ignores the data entirely, is admissible, because no rule beats it at the single point $\theta = 7$. Admissibility is a purely negative certificate: it rules out being dominated, and nothing more.

!!! probe "A sharper question"
    *If the ordinary estimator has flat, unbeatable-looking risk, surely it is admissible — so why does anyone bother shrinking it?*
    In one dimension the sample mean is indeed admissible, and shrinkage buys only the modest, prior-dependent trade the amber curve shows. The shock, due to Stein, is that in *three or more* dimensions the ordinary estimator becomes **inadmissible**: a single shrinkage rule dominates it, cutting risk at *every* $\theta$ at once, even for parameters with nothing to do with each other. That is not a tie to be broken by taste; it is strict domination, and it is the whole subject of Chapter 13 [@hastie2009].

## Admissibility, minimax, and Bayes risk

When risk curves cross, admissibility cannot rank them, so you need a way to collapse each curve down to a single comparable number. There are exactly two honest ways to summarize a curve you must commit to before knowing where on it you will land: take its *worst* value, or take its *average* value against some weighting. Each yields a criterion, a matching notion of an optimal rule, and — this is the honest part — a different answer, because they encode different attitudes toward the unknown [@wasserman2004; @cox2006].

The cautious attitude summarizes a curve by its peak. The **minimax** rule is the one whose worst-case risk is smallest:

$$\delta_{\text{minimax}} \;=\; \arg\min_{\delta}\;\max_{\theta}\;R(\theta, \delta).$$

You imagine an adversary who, after you pick $\delta$, sets $\theta$ to the value that hurts you most — the **least favorable** value — and you choose the rule that makes that worst case as painless as possible. Minimax buys a guarantee: whatever the truth, your risk is capped at a known level. The price is that you spend all your effort defending against a truth that may be nowhere near reality. A minimax rule often has *flat* risk, exactly level across $\theta$, because the way to shrink the maximum of a curve is usually to stop letting it bulge anywhere — spread the risk evenly so no single point can be exploited.

The betting attitude summarizes a curve by its average against a **prior distribution** $\pi(\theta)$, the Chapter 9 object encoding how plausible you find each value of $\theta$ before the data. Averaging the risk curve against the prior gives one number, the **Bayes risk**:

$$r(\pi, \delta) \;=\; \int R(\theta, \delta)\,\pi(\theta)\,d\theta,$$

and the rule that minimizes it is the **Bayes decision rule** for that prior — also called the Bayes-optimal rule. (This is a different object from "Bayes' rule" the theorem of Chapter 9; the theorem computes a posterior, whereas the Bayes *decision rule* is the action that minimizes expected loss. Same name, unrelated jobs.) The deep fact is that you do not have to search over all rules to find it. Minimizing the average risk is equivalent to minimizing, for each dataset you might see, the **posterior expected loss** — so the Bayes decision rule is: observe the data, form the posterior, and output the action that minimizes expected loss under it. Which action that is depends on the loss you chose in Chapter 10: under squared-error loss it is the **posterior mean**, under absolute-error loss the **posterior median**, and under 0–1 loss the posterior mode. The loss picks the summary of the posterior; the posterior does the rest.

<figure>
<img src="assets/figures/minimax-bayes.svg" alt="Risk versus the unknown parameter theta for two rules, with a prior density drawn low on the same axis. A flat blue line at height one is the MLE, labeled minimax, with its worst case marked at one. A purple parabola is the Bayes rule: it dips to one quarter near theta equals zero, where the shaded prior density is concentrated, then rises and crosses the flat line at plus and minus the square root of three. Two dots mark the crossings.">
<figcaption>Two attitudes toward the same unknown. The minimax rule (blue) keeps its risk flat, so its worst case is as low as possible — a guarantee that holds wherever the truth sits. The Bayes rule (purple) spends its advantage where the prior (shaded) places its mass, dipping far below near the center and paying for it in the tails. Neither is "correct": they answer to different fears.</figcaption>
</figure>

The figure puts the two side by side on the normal-mean problem. The MLE holds its risk flat at one — its worst case is one, and no rule can guarantee lower, so it is minimax. The Bayes rule for a prior centered at zero pulls its risk far down where the prior expects the truth to be, buying a large improvement in the center at the cost of worse-than-minimax risk out in the tails the prior thinks are unlikely. If the truth really is near zero, the Bayes rule wins comfortably; if it is far out, minimax was the safer bet. That is the entire tension of the chapter in one picture.

!!! warning "Common trap"
    There is no rule that minimizes risk at every $\theta$ simultaneously — if there were, decision theory would be a footnote. The moment risk curves cross, "the best rule" is undefined until you say *by which criterion*. Minimax, Bayes, and admissibility are not three routes to one answer; they are three genuinely different answers, and a paper that reports "the optimal estimator" without naming its criterion has quietly smuggled in an attitude toward the unknown.

!!! analogy "Analogy"
    Minimax packs for the worst weather the trip could possibly throw at you; the Bayes rule packs for the forecast. If the forecast is good and holds, the Bayes traveler is lighter and more comfortable the whole way; if a freak storm hits, the minimax traveler is the one who is fine. The analogy leaks where the forecast comes from: a weather forecast is checkable against tomorrow, but a prior is a commitment you make in advance and cannot fully audit — which is exactly why the choice between the two criteria is a choice about temperament, not a fact you can look up.

!!! probe "A sharper question"
    *Isn't minimax just Bayes for a pessimist — and if so, why keep both?*
    The connection is real and beautiful: under broad conditions the minimax rule *is* the Bayes rule for a particular "least favorable" prior, the prior an adversary would choose to make your life hardest. So minimax is not a rival machinery; it is Bayes aimed at the worst possible prior instead of your honest one. You keep both because they encode different commitments: Bayes says "here is what I actually believe," minimax says "I refuse to assume anything and will insure against the worst." Choosing between them is choosing whether you trust your prior more than you fear the tail.

!!! note "Note"
    The three lenses are not fully independent — they lock together at the edges. A Bayes decision rule with respect to a proper prior is, under mild conditions, automatically admissible: if something dominated it, that something would have strictly lower Bayes risk too, contradicting optimality. Admissible rules, in turn, are essentially all Bayes rules or limits of them. So "admissible," "Bayes," and "minimax" are three viewing angles on one geometry, and Stein's inadmissibility result (Chapter 13) is startling precisely because it shows the ordinary estimator falling *outside* that geometry in high dimensions.

Seen this way, decision theory does not hand you an optimal procedure — it hands you a vocabulary for the fact that optimality is plural. Risk turns a rule into a curve over the unknown; admissibility throws out the curves that are beaten everywhere; and minimax versus Bayes are the two disciplined ways to break the ties that remain, one insuring against the worst case, the other betting on a prior. The next chapter takes the single most important tie-break in the book — the choice to accept a little bias for a lot less variance — and shows that it is not a trick but the shape of the risk curve itself.
