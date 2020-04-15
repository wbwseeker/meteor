from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from itertools import product
from typing import Any
from typing import List
from typing import Tuple

from mip import BINARY
from mip import Model
from mip import maximize
from mip import xsum
from nltk import SnowballStemmer
from nltk import word_tokenize


class Language(str, Enum):
    german = "german"
    english = "english"


@dataclass
class Token:
    tid: int
    text: str
    stages: List[Any] = field(default_factory=list)


class StageBase(ABC):
    """
    Base class for matching stages. Matching stages produce representations
    for each token that can be used to find matching tokens in the other
    sentence.
    """

    def __init__(self, weight: float, *args, **kwargs):
        self._weight = weight

    @property
    def weight(self) -> float:
        return self._weight

    @abstractmethod
    def process_tokens(self, tokens: List[Token]):
        """
        Append a representation of each token to each token's stages list.
        """

    def validate(self, tokens: List[Token]):
        if len(set(len(token.stages) for token in tokens)) > 1:
            raise AssertionError(
                "Unequal number of stage representations in tokens."
            )


class IdentityStage(StageBase):
    """ Exact matching of tokens """

    def process_tokens(self, tokens: List[Token]):
        for token in tokens:
            token.stages.append(token.text)


class StemmingStage(StageBase):
    """ Use stemming to find tokens with the same stem """

    def __init__(self, weight: float, language: Language, *args, **kwargs):
        super().__init__(weight, *args, **kwargs)
        self._stemmer = SnowballStemmer(
            language=language.value, ignore_stopwords=True
        )

    def process_tokens(self, tokens: List[Token]):
        for token in tokens:
            token.stages.append(self._stemmer.stem(token.text))


def tokenize(text: str, language: Language) -> List[Token]:
    return [
        Token(tid=i, text=token)
        for i, token in enumerate(word_tokenize(text, language=language.value))
    ]


def preprocess(
    stages: List[StageBase], text: str, language: Language
) -> List[Token]:
    """
    Tokenize the given text and apply all given matching stages to each token.
    """
    tokens = tokenize(text, language)
    for stage in stages:
        stage.process_tokens(tokens)
        stage.validate(tokens)
    return tokens


def align(
    hypothesis: List[Token], reference: List[Token], stages: List[StageBase]
) -> List[Tuple[int, int]]:
    """
    Produce an alignment between matching tokens of each sentence.
    If there are multiple possible alignments, the one with the minimum
    number of crossings between matches is chosen. Matches are weighted
    by their stage weight.

    Uses the following binary integer linear program to find the optimal
    alignment:

    variables:
        M(i,j): set of possible matches, defined by the different stages
        C = M(i,j) x M(k,l): set of possible crossings of matches,
                             for each i < k and j > l OR i > k and j < l
        W: weights for each stage

    constraints:
        each token is matched with not more than one other token
            m(i,0) + ... + m(i, j) <= 1
            m(0,j) + ... + m(i, j) <= 1
        there must be as many matches as there are possible matches in the
        sentence with fewer possible matches
            m(0,0) ... m(i,j) == min(hypo_matches, ref_matches)
        if two matches cross each other, the corresponding crossing var is 1
            m(i,j) + m(k,l) - c(i,j,k,l) <= 1

    objective function:
        maximize match scores, minimize crossings
        MAX (SUM w(i,j) * m(i,j) - SUM c(i,j,k,l))

    """

    # compute all possible matches with their best weight over all stages
    match_weights = [
        [float("-inf")] * len(reference) for _ in range(len(hypothesis))
    ]
    for hyptoken, reftoken in product(hypothesis, reference):
        weights = [
            stage.weight
            for i, stage in enumerate(stages)
            if hyptoken.stages[i] == reftoken.stages[i]
        ]
        if weights:
            match_weights[hyptoken.tid][reftoken.tid] = max(weights)

    # create BILP
    model = Model("alignment")
    model.verbose = 0

    # create matching variables for each possible match
    match_vars = {
        (h, r): model.add_var(var_type=BINARY)
        for h in range(len(hypothesis))
        for r in range(len(reference))
        if match_weights[h][r] > float("-inf")
    }

    # create crossing variables for each possible crossing of any two matches
    # add constraint that crossing var will be 1 if both matches are selected
    crossing_vars = []
    for (i, j), (k, l) in product(match_vars.keys(), repeat=2):
        if (i < k and j > l) or (i > k and j < l):
            cvar = model.add_var(var_type=BINARY)
            model += (
                xsum([-1.0 * cvar, match_vars[(i, j)], match_vars[(k, l)]])
                <= 1
            )
            crossing_vars.append(cvar)

    # add uniqueness constraints: each word is matched to one other word
    # words that can't be matched are already excluded
    for h in range(len(hypothesis)):
        matches = [
            match_vars[(h, r)]
            for r in range(len(reference))
            if match_weights[h][r] > float("-inf")
        ]
        if matches:
            model += xsum(matches) <= 1

    for r in range(len(reference)):
        matches = [
            match_vars[(h, r)]
            for h in range(len(hypothesis))
            if match_weights[h][r] > float("-inf")
        ]
        if matches:
            model += xsum(matches) <= 1

    # all words of the sentence with the lower number of possible matches
    # must be matched
    hypo_matches = len(set(h for h, _ in match_vars))
    ref_matches = len(set(r for _, r in match_vars))
    model += xsum(match_vars.values()) == min(hypo_matches, ref_matches)

    # define objective: maximize match scores and minimize crossings
    model.objective = maximize(
        xsum(
            [match_weights[h][r] * match_vars[(h, r)] for h, r in match_vars]
            + [-1.0 * cvar for cvar in crossing_vars]
        )
    )

    model.optimize()

    return [match for match, var in match_vars.items() if var.x >= 0.99]


def count_chunks(alignment: List[Tuple[int, int]]) -> int:
    """
    Find the minimum number of chunks the alignment can be grouped into.
    """
    alignment = sorted(alignment)

    num_chunks = 0
    last_h, last_r = -2, -2
    for (h, r) in alignment:
        if abs(last_h - h) != 1 or abs(last_r - r) != 1:
            num_chunks += 1
        last_h, last_r = (h, r)

    return num_chunks


def meteor(
    hypothesis: str,
    reference: str,
    stages: List[StageBase],
    language: Language,
) -> float:
    """
    Compute meteor score for the given sentence pair
    with the given set of matching stages.
    """

    hypo_tokens = preprocess(stages, hypothesis, language)
    ref_tokens = preprocess(stages, reference, language)

    if len(hypo_tokens) == 0 or len(ref_tokens) == 0:
        if len(hypo_tokens) != len(ref_tokens):
            return 0.0
        return 1.0

    alignment = align(hypo_tokens, ref_tokens, stages)
    num_matches = len(alignment)
    if num_matches == 0:
        return 0.0

    precision = num_matches / float(len(hypo_tokens))
    recall = num_matches / float(len(ref_tokens))
    fscore = (10 * precision * recall) / (recall + 9 * precision)

    num_chunks = count_chunks(alignment)
    penalty = 0.5 * (num_chunks / num_matches) ** 3 if num_chunks > 1 else 0

    score = fscore * (1 - penalty)

    return score


def meteor_macro_avg(
    hypotheses: List[str],
    references: List[str],
    stages: List[StageBase],
    language: Language,
) -> float:
    """
    Apply meteor score to multiple hypothesis-reference pairs
    and return the macro average.
    """
    scores = [
        meteor(hypothesis, reference, stages, language)
        for hypothesis, reference in zip(hypotheses, references)
    ]
    return sum(scores) / len(scores)
