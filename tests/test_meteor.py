from typing import List

import pytest

from meteor import IdentityStage
from meteor import StemmingStage
from meteor import meteor
from meteor.meteor import StageBase
from meteor.meteor import Token
from meteor.meteor import align
from meteor.meteor import count_chunks
from meteor.meteor import preprocess


@pytest.fixture
def stages():
    return [IdentityStage(1.0), StemmingStage(0.6, "german")]


@pytest.mark.parametrize(
    "hypothesis, reference, alignment",
    [
        (
            "Die Katze sitzt auf dem Dach.",
            "Auf dem Dach sitzt die Katze.",
            [(0, 4), (1, 5), (2, 3), (3, 0), (4, 1), (5, 2), (6, 6)],
        ),
        # test stemming
        ("Frauen Frau", "Frau Frau", [(0, 0), (1, 1)]),
        ("Frau Frauen", "Frau Frau", [(0, 0), (1, 1)]),
        # test with matching gaps
        ("Frau Mann", "Frau Frau", [(0, 0)]),
        # no matching at all
        ("Haus Kind", "Frau Mann", []),
        # empty input
        ("", "Frau Mann", []),
    ],
)
def test_alignment(stages, hypothesis, reference, alignment):
    hypo_tokens = preprocess(stages, hypothesis)
    ref_tokens = preprocess(stages, reference)

    assert align(hypo_tokens, ref_tokens, stages) == alignment


@pytest.mark.parametrize(
    "alignment, expected_chunks",
    [
        ([(0, 4), (1, 5), (2, 3), (3, 0), (4, 1), (5, 2), (6, 6)], 4),
        ([(0, 0), (1, 1)], 1),
        ([(0, 0)], 1),
        ([], 0),
    ],
)
def test_count_chunks(alignment, expected_chunks):
    assert count_chunks(alignment) == expected_chunks


def test_stage_validation():
    class BrokenStage(StageBase):
        def process_tokens(self, tokens: List[Token]):
            for i, token in enumerate(tokens):
                if i % 2:
                    token.stages.append(token.text)

    with pytest.raises(AssertionError):
        preprocess([BrokenStage(1.0)], "Die Katze sitzt auf dem Dach.")


@pytest.mark.parametrize(
    "hypothesis, reference, expected_score",
    [
        (
            "Die Katze sitzt auf dem Dach.",
            "Die Katze sitzt auf dem Dach.",
            1.0,
        ),
        (
            "Die Katze sitzt auf dem Dach.",
            "Auf dem Dach sitzt die Katze.",
            0.91,
        ),
        ("Frau Frauen", "Frau Frau", 1.0),
        ("", "Haus Kind", 0.0),
        ("", "", 1.0),
    ],
)
def test_meteor(stages, hypothesis, reference, expected_score):
    score = meteor(hypothesis, reference, stages=stages)
    assert round(score, 2) == expected_score
