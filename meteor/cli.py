from pathlib import Path

import typer

from meteor import IdentityStage
from meteor import Language
from meteor import StemmingStage
from meteor import meteor_macro_avg


def cli(
    hypotheses_file: Path = typer.Option(
        ...,
        "-h",
        "--hypotheses",
        help="utf-8 encoded file with system output, one sentence per line",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    references_file: Path = typer.Option(
        ...,
        "-r",
        "--references",
        help="utf-8 encoded file with translation references, one sentence per line",  # noqa
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
    language: Language = typer.Option(
        Language.german,
        "-l",
        "--language",
        help="The language to run meteor for. Controls tokenization and stemming.",  # noqa
        show_default=True,
        case_sensitive=False,
    ),
):
    """
    Computes the METEOR score for the given sentence pairs
    and returns the macro average.

    Input files must be of same length and contain one sentence per line.
    Assumes UTF-8 encoding.
    """

    with hypotheses_file.open(encoding="utf-8") as infile:
        hypotheses = [line.strip() for line in infile if line.strip()]

    with references_file.open(encoding="utf-8") as infile:
        references = [line.strip() for line in infile if line.strip()]

    if len(hypotheses) != len(references):
        typer.echo("Error: Input files must be of same length.")
        exit(1)

    stages = [
        IdentityStage(1.0),
        StemmingStage(0.6, language),
    ]

    macro_avg = meteor_macro_avg(hypotheses, references, stages, language)
    typer.echo(f"METEOR macro average: {round(macro_avg, 3)}")


def main():
    typer.run(cli)
