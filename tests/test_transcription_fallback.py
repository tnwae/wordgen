from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import conlang_utils as cu


def test_transcribe_and_detranscribe_are_noops_without_transcription_rules() -> None:
    data_file = Path(__file__).resolve().parents[1] / "keregafa.json"
    conlang_data = cu.ConlangData(str(data_file))

    assert conlang_data.transcription is None
    assert conlang_data.transcribe("aba") == "aba"
    assert conlang_data.detranscribe("aba") == "aba"


def test_transcribe_cli_preserves_last_char_without_trailing_newline(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    words_file = tmp_path / "words.txt"
    words_file.write_text("aba", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "transcribe.py"),
            "-i",
            str(words_file),
            "-d",
            str(repo_root / "keregafa.json"),
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(repo_root),
    )

    assert result.stdout.strip() == "aba"
