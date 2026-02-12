import nltk

from meteor.meteor import IdentityStage
from meteor.meteor import Language
from meteor.meteor import StageBase
from meteor.meteor import StemmingStage
from meteor.meteor import meteor
from meteor.meteor import meteor_macro_avg

__all__ = [
    "meteor",
    "meteor_macro_avg",
    "Language",
    "StageBase",
    "IdentityStage",
    "StemmingStage",
]


def _ensure_nltk_data():
    """Download required NLTK data if not present."""
    required_data = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]

    for data_path, download_name in required_data:
        try:
            nltk.data.find(data_path)
        except LookupError:
            nltk.download(download_name, quiet=True)


_ensure_nltk_data()
