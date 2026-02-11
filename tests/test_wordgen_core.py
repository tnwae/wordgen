import json
from pathlib import Path

import wordgen


def test_run_reaches_target_count(keregafa_data_path: Path) -> None:
    wb = wordgen.WordBuilder(str(keregafa_data_path))

    counter = {"i": 0}

    def fake_make_word(*_args, **_kwargs):
        counter["i"] += 1
        wb.results.add(f"w{counter['i']}")

    wb.make_word = fake_make_word  # type: ignore[method-assign]
    wb.run(count=4, template=None, length=1, type="noun", transcribe=False)

    assert len(wb.results) == 4


def test_make_word_with_transcription_branch(keregafa_data_path: Path) -> None:
    wb = wordgen.WordBuilder(str(keregafa_data_path))

    wb.conlang_data.compile_syllable_class = lambda _ch: "a"  # type: ignore[method-assign]
    wb.conlang_data.transcription = {"a": "A"}
    wb.conlang_data.transcribe = lambda s: s.upper()  # type: ignore[method-assign]

    wb.make_word(syllable_count=1, template="X", type="noun", transcribe=True)

    assert "A" in wb.results


def test_make_word_invalid_template_exits(keregafa_data_path: Path) -> None:
    wb = wordgen.WordBuilder(str(keregafa_data_path))

    try:
        wb.make_word(syllable_count=1, template="?", type="noun", transcribe=False)
        assert False, "Expected SystemExit when template contains unknown class"
    except SystemExit:
        pass


def test_main_noninteractive_json_output(capsys) -> None:
    wordgen.main(
        p_language="keregafa",
        p_count=1,
        p_template="V",
        p_transcribe=False,
        p_word_length=1,
        p_format="json",
        p_type="noun",
        p_interactive=False,
    )

    out = capsys.readouterr().out.strip()
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
