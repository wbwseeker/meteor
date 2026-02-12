import pytest

from meteor import IdentityStage
from meteor import StemmingStage
from meteor import meteor
from meteor.meteor import Language
from meteor.meteor import StageBase
from meteor.meteor import Token
from meteor.meteor import align
from meteor.meteor import compute_cliques
from meteor.meteor import count_chunks
from meteor.meteor import meteor_macro_avg
from meteor.meteor import preprocess


@pytest.fixture
def stages():
    return [IdentityStage(1.0), StemmingStage(0.6, Language.german)]


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
    hypo_tokens = preprocess(stages, hypothesis, Language.german)
    ref_tokens = preprocess(stages, reference, Language.german)

    assert align(hypo_tokens, ref_tokens, stages) == alignment


@pytest.mark.parametrize(
    "matches, cliques",
    [
        (
            [(0, 0), (1, 0), (2, 1), (2, 2)],
            [[(0, 0), (1, 0)], [(2, 1), (2, 2)]],
        ),
        (
            [(0, 1), (0, 3), (1, 0), (1, 2), (2, 1), (2, 3), (3, 0), (3, 2)],
            [
                [(0, 1), (0, 3), (2, 1), (2, 3)],
                [(1, 0), (1, 2), (3, 0), (3, 2)],
            ],
        ),
        (
            [
                (0, 1),
                (0, 3),
                (1, 0),
                (1, 2),
                (1, 4),
                (2, 1),
                (2, 3),
                (3, 0),
                (3, 2),
                (3, 4),
                (4, 1),
                (4, 3),
            ],
            [
                [(0, 1), (0, 3), (2, 1), (2, 3), (4, 1), (4, 3)],
                [(1, 0), (1, 2), (1, 4), (3, 0), (3, 2), (3, 4)],
            ],
        ),
    ],
)
def test_compute_cliques(matches, cliques):
    assert compute_cliques(matches) == cliques


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
        def process_tokens(self, tokens: list[Token]):
            for i, token in enumerate(tokens):
                if i % 2:
                    token.stages.append(token.text)

    with pytest.raises(AssertionError):
        preprocess(
            [BrokenStage(1.0)],
            "Die Katze sitzt auf dem Dach.",
            Language.german,
        )


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
        ("Haus", "Kind", 0.0),
        ("", "Haus Kind", 0.0),
        ("", "", 1.0),
    ],
)
def test_meteor(stages, hypothesis, reference, expected_score):
    score = meteor(hypothesis, reference, stages, Language.german)
    assert round(score, 2) == expected_score


def test_english():
    stages = [IdentityStage(1.0), StemmingStage(0.6, Language.english)]
    score = meteor("action", "actionable", stages, Language.english)
    assert score == 1.0


def test_meteor_macro_avg(stages):
    hypotheses = [
        "Die Katze sitzt auf dem Dach",
        "Die Katze sitzt auf dem Dach",
    ]
    references = [
        "Die Katze sitzt auf dem Dach",
        "Die Katze sitzt in der Badewanne",
    ]

    assert (
        meteor_macro_avg(hypotheses, references, stages, Language.german)
        == 0.75
    )
