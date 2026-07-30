"""Single source of truth for the book's references.

Chapters cite a work with `[@key]` in their markdown; `build.py` resolves each
key against `REFERENCES`, renders an author-year citation linked to the entry,
and appends a per-chapter References section listing exactly the works that
chapter cites. A citation whose key is missing here fails the build loudly.

Every entry should be verified against the actual paper (arXiv listing, venue
page) before it lands — a wrong citation is worse than no citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9]*$")
ARXIV_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}$")


@dataclass(frozen=True)
class Reference:
    """One cited work.

    `authors` holds one "Lastname, F. M." string per author, in the paper's
    order; a corporate author (e.g. "DeepMind") is a single comma-free string.
    `truncated` marks an author list that is deliberately cut short (papers with
    dozens or hundreds of authors) and renders as "et al.". Exactly one of
    `arxiv` (a bare id like "1706.03762") and `url` may be set; both empty means
    the entry renders with no link.
    """

    key: str
    authors: tuple[str, ...]
    truncated: bool
    year: int
    title: str
    venue: str
    arxiv: str
    url: str

    def __post_init__(self) -> None:
        assert KEY_PATTERN.match(self.key), f"Bad reference key: {self.key!r}."
        assert self.authors, f"Reference '{self.key}' has no authors."
        assert all(a.strip() for a in self.authors), f"Empty author in '{self.key}'."
        assert 1900 < self.year <= 2100, f"Implausible year in '{self.key}'."
        assert self.title and not self.title.endswith(
            "."
        ), f"Title of '{self.key}' must be non-empty and carry no trailing period."
        assert self.venue, f"Reference '{self.key}' has no venue."
        assert not (
            self.arxiv and self.url
        ), f"Reference '{self.key}' sets both arxiv and url; pick one."
        if self.arxiv:
            assert ARXIV_ID_PATTERN.match(
                self.arxiv
            ), f"Bad arXiv id in '{self.key}': {self.arxiv!r}."

    def first_author_family(self) -> str:
        """Return the first author's family name (the part before the comma)."""
        first = self.authors[0]
        return first.split(",")[0].strip() if "," in first else first

    def in_text_label(self) -> str:
        """Return the author-year label, e.g. "Vaswani et al., 2017"."""
        family = self.first_author_family()
        if self.truncated or len(self.authors) >= 3:
            return f"{family} et al., {self.year}"
        if len(self.authors) == 2:
            second = self.authors[1]
            second_family = second.split(",")[0].strip() if "," in second else second
            return f"{family} & {second_family}, {self.year}"
        return f"{family}, {self.year}"

    def link(self) -> str:
        """Return the entry's URL, or "" when it has none."""
        if self.arxiv:
            return f"https://arxiv.org/abs/{self.arxiv}"
        return self.url


# One worked example so a drafter has a pattern to copy. Add verified entries as
# chapters cite them, and delete this one once real references land. Every entry
# must be checked against the actual paper before it ships.
_ENTRIES: tuple[Reference, ...] = (
    Reference(
        key="hastie2009",
        authors=("Hastie, T.", "Tibshirani, R.", "Friedman, J."),
        truncated=False,
        year=2009,
        title="The Elements of Statistical Learning: Data Mining, Inference, and Prediction",
        venue="Springer",
        arxiv="",
        url="https://hastie.su.domains/ElemStatLearn/",
    ),
    Reference(
        key="wasserman2004",
        authors=("Wasserman, L.",),
        truncated=False,
        year=2004,
        title="All of Statistics: A Concise Course in Statistical Inference",
        venue="Springer",
        arxiv="",
        url="https://doi.org/10.1007/978-0-387-21736-9",
    ),
    Reference(
        key="cox2006",
        authors=("Cox, D. R.",),
        truncated=False,
        year=2006,
        title="Principles of Statistical Inference",
        venue="Cambridge University Press",
        arxiv="",
        url="https://doi.org/10.1017/CBO9780511813559",
    ),
    Reference(
        key="diaconis1979",
        authors=("Diaconis, P.", "Ylvisaker, D."),
        truncated=False,
        year=1979,
        title="Conjugate Priors for Exponential Families",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1176344611",
    ),
    Reference(
        key="wainwright2008",
        authors=("Wainwright, M. J.", "Jordan, M. I."),
        truncated=False,
        year=2008,
        title="Graphical Models, Exponential Families, and Variational Inference",
        venue="Foundations and Trends in Machine Learning",
        arxiv="",
        url="https://doi.org/10.1561/2200000001",
    ),
    Reference(
        key="gelman2013",
        authors=(
            "Gelman, A.",
            "Carlin, J. B.",
            "Stern, H. S.",
            "Dunson, D. B.",
            "Vehtari, A.",
            "Rubin, D. B.",
        ),
        truncated=False,
        year=2013,
        title="Bayesian Data Analysis, Third Edition",
        venue="Chapman and Hall/CRC",
        arxiv="",
        url="http://www.stat.columbia.edu/~gelman/book/",
    ),
    Reference(
        key="huber1964",
        authors=("Huber, P. J.",),
        truncated=False,
        year=1964,
        title="Robust Estimation of a Location Parameter",
        venue="The Annals of Mathematical Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aoms/1177703732",
    ),
    Reference(
        key="koenker1978",
        authors=("Koenker, R.", "Bassett, G."),
        truncated=False,
        year=1978,
        title="Regression Quantiles",
        venue="Econometrica",
        arxiv="",
        url="https://doi.org/10.2307/1913643",
    ),
    Reference(
        key="stein1956",
        authors=("Stein, C.",),
        truncated=False,
        year=1956,
        title="Inadmissibility of the Usual Estimator for the Mean of a Multivariate Normal Distribution",
        venue="Proc. Third Berkeley Symposium on Mathematical Statistics and Probability",
        arxiv="",
        url="https://projecteuclid.org/euclid.bsmsp/1200501656",
    ),
    Reference(
        key="jamesstein1961",
        authors=("James, W.", "Stein, C."),
        truncated=False,
        year=1961,
        title="Estimation with Quadratic Loss",
        venue="Proc. Fourth Berkeley Symposium on Mathematical Statistics and Probability",
        arxiv="",
        url="https://projecteuclid.org/euclid.bsmsp/1200512173",
    ),
    Reference(
        key="efron1977",
        authors=("Efron, B.", "Morris, C."),
        truncated=False,
        year=1977,
        title="Stein's Paradox in Statistics",
        venue="Scientific American",
        arxiv="",
        url="https://efron.ckirby.su.domains/other/Article1977.pdf",
    ),
    Reference(
        key="tibshirani1996",
        authors=("Tibshirani, R.",),
        truncated=False,
        year=1996,
        title="Regression Shrinkage and Selection via the Lasso",
        venue="Journal of the Royal Statistical Society: Series B",
        arxiv="",
        url="https://doi.org/10.1111/j.2517-6161.1996.tb02080.x",
    ),
    Reference(
        key="hoerl1970",
        authors=("Hoerl, A. E.", "Kennard, R. W."),
        truncated=False,
        year=1970,
        title="Ridge Regression: Biased Estimation for Nonorthogonal Problems",
        venue="Technometrics",
        arxiv="",
        url="https://doi.org/10.1080/00401706.1970.10488634",
    ),
    Reference(
        key="neyman1933",
        authors=("Neyman, J.", "Pearson, E. S."),
        truncated=False,
        year=1933,
        title="On the Problem of the Most Efficient Tests of Statistical Hypotheses",
        venue="Philosophical Transactions of the Royal Society A",
        arxiv="",
        url="https://doi.org/10.1098/rsta.1933.0009",
    ),
    Reference(
        key="wilks1938",
        authors=("Wilks, S. S.",),
        truncated=False,
        year=1938,
        title="The Large-Sample Distribution of the Likelihood Ratio for Testing Composite Hypotheses",
        venue="The Annals of Mathematical Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aoms/1177732360",
    ),
    Reference(
        key="chernoff1954",
        authors=("Chernoff, H.",),
        truncated=False,
        year=1954,
        title="On the Distribution of the Likelihood Ratio",
        venue="The Annals of Mathematical Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aoms/1177728725",
    ),
    Reference(
        key="wasserstein2016",
        authors=("Wasserstein, R. L.", "Lazar, N. A."),
        truncated=False,
        year=2016,
        title="The ASA Statement on p-Values: Context, Process, and Purpose",
        venue="The American Statistician",
        arxiv="",
        url="https://doi.org/10.1080/00031305.2016.1154108",
    ),
    Reference(
        key="benjamini1995",
        authors=("Benjamini, Y.", "Hochberg, Y."),
        truncated=False,
        year=1995,
        title="Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing",
        venue="Journal of the Royal Statistical Society, Series B",
        arxiv="",
        url="https://doi.org/10.1111/j.2517-6161.1995.tb02031.x",
    ),
    Reference(
        key="ioannidis2005",
        authors=("Ioannidis, J. P. A.",),
        truncated=False,
        year=2005,
        title="Why Most Published Research Findings Are False",
        venue="PLoS Medicine",
        arxiv="",
        url="https://doi.org/10.1371/journal.pmed.0020124",
    ),
    Reference(
        key="gelman2014",
        authors=("Gelman, A.", "Carlin, J."),
        truncated=False,
        year=2014,
        title="Beyond Power Calculations: Assessing Type S (Sign) and Type M (Magnitude) Errors",
        venue="Perspectives on Psychological Science",
        arxiv="",
        url="https://doi.org/10.1177/1745691614551642",
    ),
    Reference(
        key="benjamin2018",
        authors=("Benjamin, D. J.",),
        truncated=True,
        year=2018,
        title="Redefine Statistical Significance",
        venue="Nature Human Behaviour",
        arxiv="",
        url="https://doi.org/10.1038/s41562-017-0189-z",
    ),
    Reference(
        key="amrhein2019",
        authors=("Amrhein, V.", "Greenland, S.", "McShane, B."),
        truncated=True,
        year=2019,
        title="Scientists Rise Up Against Statistical Significance",
        venue="Nature",
        arxiv="",
        url="https://doi.org/10.1038/d41586-019-00857-9",
    ),
    Reference(
        key="neyman1937",
        authors=("Neyman, J.",),
        truncated=False,
        year=1937,
        title="Outline of a Theory of Statistical Estimation Based on the Classical Theory of Probability",
        venue="Philosophical Transactions of the Royal Society A",
        arxiv="",
        url="https://doi.org/10.1098/rsta.1937.0005",
    ),
    Reference(
        key="casella2002",
        authors=("Casella, G.", "Berger, R. L."),
        truncated=False,
        year=2002,
        title="Statistical Inference, Second Edition",
        venue="Duxbury Press",
        arxiv="",
        url="https://www.cengage.com/c/statistical-inference-2e-casella-berger/9780534243128/",
    ),
    Reference(
        key="lecam1953",
        authors=("Le Cam, L.",),
        truncated=False,
        year=1953,
        title="On some asymptotic properties of maximum likelihood estimates and related Bayes' estimates",
        venue="University of California Publications in Statistics",
        arxiv="",
        url="https://openlibrary.org/books/OL205555M/On_some_asymptotic_properties_of_maximum_likelihood_estimates_and_related_Bayes'_estimates",
    ),
    Reference(
        key="hajek1970",
        authors=("Hájek, J.",),
        truncated=False,
        year=1970,
        title="A characterization of limiting distributions of regular estimates",
        venue="Zeitschrift für Wahrscheinlichkeitstheorie und verwandte Gebiete",
        arxiv="",
        url="https://doi.org/10.1007/BF00533669",
    ),
    Reference(
        key="hajek1972",
        authors=("Hájek, J.",),
        truncated=False,
        year=1972,
        title="Local asymptotic minimax and admissibility in estimation",
        venue="Proceedings of the Sixth Berkeley Symposium on Mathematical Statistics and Probability",
        arxiv="",
        url="https://projecteuclid.org/ebooks/berkeley-symposium-on-mathematical-statistics-and-probability/Proceedings-of-the-Sixth-Berkeley-Symposium-on-Mathematical-Statistics-and/chapter/Local-Asymptotic-Minimax-and-Admissibility-in-Estimation/bsmsp/1200514092",
    ),
    Reference(
        key="white1982",
        authors=("White, H.",),
        truncated=False,
        year=1982,
        title="Maximum likelihood estimation of misspecified models",
        venue="Econometrica",
        arxiv="",
        url="https://doi.org/10.2307/1912526",
    ),
    Reference(
        key="vandervaart1998",
        authors=("van der Vaart, A. W.",),
        truncated=False,
        year=1998,
        title="Asymptotic Statistics",
        venue="Cambridge University Press",
        arxiv="",
        url="https://doi.org/10.1017/CBO9780511802256",
    ),
    Reference(
        key="efron1979",
        authors=("Efron, B.",),
        truncated=False,
        year=1979,
        title="Bootstrap Methods: Another Look at the Jackknife",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1176344552",
    ),
    Reference(
        key="efron1987",
        authors=("Efron, B.",),
        truncated=False,
        year=1987,
        title="Better Bootstrap Confidence Intervals",
        venue="Journal of the American Statistical Association",
        arxiv="",
        url="https://doi.org/10.1080/01621459.1987.10478410",
    ),
    Reference(
        key="singh1981",
        authors=("Singh, K.",),
        truncated=False,
        year=1981,
        title="On the Asymptotic Accuracy of Efron's Bootstrap",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1176345636",
    ),
    Reference(
        key="bickel1981",
        authors=("Bickel, P. J.", "Freedman, D. A."),
        truncated=False,
        year=1981,
        title="Some Asymptotic Theory for the Bootstrap",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1176345637",
    ),
    Reference(
        key="kunsch1989",
        authors=("Künsch, H. R.",),
        truncated=False,
        year=1989,
        title="The Jackknife and the Bootstrap for General Stationary Observations",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1176347265",
    ),
    Reference(
        key="bickel1997",
        authors=("Bickel, P. J.", "Götze, F.", "van Zwet, W. R."),
        truncated=False,
        year=1997,
        title="Resampling Fewer Than n Observations: Gains, Losses, and Remedies for Losses",
        venue="Statistica Sinica",
        arxiv="",
        url="https://www3.stat.sinica.edu.tw/statistica/oldpdf/A7n11.pdf",
    ),
    Reference(
        key="marchenko1967",
        authors=("Marchenko, V. A.", "Pastur, L. A."),
        truncated=False,
        year=1967,
        title="Distribution of Eigenvalues for Some Sets of Random Matrices",
        venue="Mathematics of the USSR-Sbornik",
        arxiv="",
        url="https://doi.org/10.1070/SM1967v001n04ABEH001994",
    ),
    Reference(
        key="johnstone2001",
        authors=("Johnstone, I. M.",),
        truncated=False,
        year=2001,
        title="On the Distribution of the Largest Eigenvalue in Principal Components Analysis",
        venue="The Annals of Statistics",
        arxiv="",
        url="https://doi.org/10.1214/aos/1009210544",
    ),
    Reference(
        key="bickel2009",
        authors=("Bickel, P. J.", "Ritov, Y.", "Tsybakov, A. B."),
        truncated=False,
        year=2009,
        title="Simultaneous Analysis of Lasso and Dantzig Selector",
        venue="The Annals of Statistics",
        arxiv="0801.1095",
        url="",
    ),
    Reference(
        key="belkin2019",
        authors=("Belkin, M.", "Hsu, D.", "Ma, S.", "Mandal, S."),
        truncated=False,
        year=2019,
        title="Reconciling Modern Machine-Learning Practice and the Classical Bias–Variance Trade-Off",
        venue="Proceedings of the National Academy of Sciences",
        arxiv="1812.11118",
        url="",
    ),
    Reference(
        key="bartlett2020",
        authors=("Bartlett, P. L.", "Long, P. M.", "Lugosi, G.", "Tsigler, A."),
        truncated=False,
        year=2020,
        title="Benign Overfitting in Linear Regression",
        venue="Proceedings of the National Academy of Sciences",
        arxiv="1906.11300",
        url="",
    ),
    Reference(
        key="hastie2022",
        authors=("Hastie, T.", "Montanari, A.", "Rosset, S.", "Tibshirani, R. J."),
        truncated=False,
        year=2022,
        title="Surprises in High-Dimensional Ridgeless Least Squares Interpolation",
        venue="The Annals of Statistics",
        arxiv="1903.08560",
        url="",
    ),
)


def _build_index(entries: tuple[Reference, ...]) -> dict[str, Reference]:
    """Index entries by key, failing loudly on duplicates."""
    index: dict[str, Reference] = {}
    for entry in entries:
        assert entry.key not in index, f"Duplicate reference key: {entry.key}."
        index[entry.key] = entry
    return index


REFERENCES: dict[str, Reference] = _build_index(_ENTRIES)
