import pytest

from meteor import IdentityStage
from meteor import Language
from meteor import StemmingStage
from meteor import meteor


@pytest.fixture
def english_stages():
    return [IdentityStage(1.0), StemmingStage(0.6, Language.english)]


@pytest.mark.parametrize(
    "hypothesis, reference, expected_score",
    [
        # https://github.com/wbwseeker/meteor/issues/2
        (
            (
                "The patient was admitted due to type 2 diabetes mellitus, and"
                " began to receive subcutaneous injection of liraglutide "
                "injection (0.6 mg/day) at 9: 00 on 09-Jun-2020."
            ),
            (
                "The patient was admitted to hospital for type 2 diabetes "
                "mellitus, and liraglutide injection (0.6 mg/day) was "
                "administered subcutaneously at 9 o 'clock on June 9th, 2020."
            ),
            0.67,
        ),
    ],
)
def test_meteor(english_stages, hypothesis, reference, expected_score):
    score = meteor(hypothesis, reference, english_stages, Language.english)
    assert round(score, 2) == expected_score
