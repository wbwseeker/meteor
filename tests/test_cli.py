import pytest
from typer.testing import CliRunner

from meteor.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_files(tmp_path):
    """Create temporary test files with German sentences."""
    hyp_file = tmp_path / "hypotheses.txt"
    ref_file = tmp_path / "references.txt"

    hyp_file.write_text(
        "Die Katze sitzt auf dem Dach.\n" "Das ist ein Test.\n",
        encoding="utf-8",
    )

    ref_file.write_text(
        "Auf dem Dach sitzt die Katze.\n" "Das ist ein Test.\n",
        encoding="utf-8",
    )

    return hyp_file, ref_file


def test_cli_basic(runner, test_files):
    """Test basic CLI functionality with valid input files."""
    hyp_file, ref_file = test_files

    result = runner.invoke(
        app,
        [
            "--hypotheses",
            str(hyp_file),
            "--references",
            str(ref_file),
            "--language",
            "german",
        ],
    )

    if result.exit_code != 0:
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
    assert result.exit_code == 0
    assert "METEOR macro average:" in result.stdout
    assert "0." in result.stdout  # Should contain a decimal number


def test_cli_short_options(runner, test_files):
    """Test CLI with short option flags."""
    hyp_file, ref_file = test_files

    result = runner.invoke(
        app,
        ["-h", str(hyp_file), "-r", str(ref_file), "-l", "german"],
    )

    assert result.exit_code == 0
    assert "METEOR macro average:" in result.stdout


def test_cli_english(runner, tmp_path):
    """Test CLI with English language option."""
    hyp_file = tmp_path / "hyp_en.txt"
    ref_file = tmp_path / "ref_en.txt"

    hyp_file.write_text("The cat is sleeping.\n", encoding="utf-8")
    ref_file.write_text("The cat sleeps.\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["-h", str(hyp_file), "-r", str(ref_file), "-l", "english"],
    )

    assert result.exit_code == 0
    assert "METEOR macro average:" in result.stdout


def test_cli_missing_file(runner, tmp_path):
    """Test CLI with non-existent input file."""
    ref_file = tmp_path / "references.txt"
    ref_file.write_text("Test sentence.\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "-h",
            str(tmp_path / "nonexistent.txt"),
            "-r",
            str(ref_file),
            "-l",
            "german",
        ],
    )

    assert result.exit_code != 0


def test_cli_unequal_length_files(runner, tmp_path):
    """Test CLI with files of different lengths."""
    hyp_file = tmp_path / "hypotheses.txt"
    ref_file = tmp_path / "references.txt"

    hyp_file.write_text("Sentence one.\n", encoding="utf-8")
    ref_file.write_text("Sentence one.\nSentence two.\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["-h", str(hyp_file), "-r", str(ref_file), "-l", "german"],
    )

    assert result.exit_code == 1
    assert "Error: Input files must be of same length" in result.stdout


def test_cli_empty_lines_ignored(runner, tmp_path):
    """Test that empty lines in input files are ignored."""
    hyp_file = tmp_path / "hypotheses.txt"
    ref_file = tmp_path / "references.txt"

    hyp_file.write_text("Sentence one.\n\n\nSentence two.\n", encoding="utf-8")
    ref_file.write_text("Sentence one.\n\nSentence two.\n\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["-h", str(hyp_file), "-r", str(ref_file), "-l", "german"],
    )

    assert result.exit_code == 0
    assert "METEOR macro average:" in result.stdout
