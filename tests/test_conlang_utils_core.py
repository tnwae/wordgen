from pathlib import Path

import conlang_utils as cu


def test_tokenize_and_detokenize_roundtrip(keregafa_data_path: Path) -> None:
    cd = cu.ConlangData(str(keregafa_data_path))

    tokens = cd.tokenize_word("nga")
    assert tokens == ["ng", "a"]
    assert cd.detokenize_word(tokens) == "nga"


def test_vowel_consonant_and_class_lookup(keregafa_data_path: Path) -> None:
    cd = cu.ConlangData(str(keregafa_data_path))

    assert cd.is_vowel("a") is True
    assert cd.is_consonant("k") is True
    assert cd.get_char_class("a", generic=True) == "V"
    assert cd.get_char_class("k", generic=True) == "C"


def test_basic_inflection_helpers(keregafa_data_path: Path) -> None:
    cd = cu.ConlangData(str(keregafa_data_path))
    word = ["k", "a", "g", "e"]

    assert cd.append_last_vowel(word) == ["k", "a", "g", "e", "e"]
    assert cd.append_last_consonant(word) == ["k", "a", "g", "e", "g"]
    assert cd.delete_last_char(word) == ["k", "a", "g"]
    assert cd.do_nothing_for_inflection(word) == word


def test_compile_syllable_class_known_and_unknown(keregafa_data_path: Path) -> None:
    cd = cu.ConlangData(str(keregafa_data_path))

    value = cd.compile_syllable_class("I")
    assert value in {"V", "CV"}

    try:
        cd.compile_syllable_class("?")
        assert False, "Expected KeyError for unknown syllable class"
    except KeyError:
        pass
