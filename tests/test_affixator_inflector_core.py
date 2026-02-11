import json
from pathlib import Path

from affixator import ConlangAffixator
from inflector import ConlangInflector


def test_affixator_noun_and_verb_paths(
    keregafa_affixes_path: Path,
    keregafa_data_path: Path,
    keregafa_inflections_path: Path,
) -> None:
    aff = ConlangAffixator(
        str(keregafa_affixes_path),
        str(keregafa_data_path),
        str(keregafa_inflections_path),
    )

    noun_forms = aff.affixate("kage")
    assert "nominative" in noun_forms
    assert "001 N-N dual number" in noun_forms

    verb_forms = aff.affixate("kagi")
    assert "present" in verb_forms
    assert "009 V-V repetition" in verb_forms


def test_inflector_noun_and_verb_paths_with_minimal_rules(
    tmp_path: Path,
    keregafa_data_path: Path,
) -> None:
    rules = {
        "declensions": {"nominative": "@", "accusative": "le"},
        "suffixRules": {
            "U": {"L": "doNothing", "U": "appendLastConsonant"},
            "L": {"L": "appendLastVowel", "U": "doNothing"},
        },
        "prefixRules": {
            "U": {"L": "doNothing", "U": "deleteLastChar"},
            "L": {"L": "deleteLastChar", "U": "doNothing"},
        },
        "tenses": {
            "i": {
                "_className": "all verbs",
                "present": "ki",
                "future": "he",
            }
        },
        "basicAttributes": {"verbEndings": ["i"]},
    }

    rules_file = tmp_path / "inflections.json"
    rules_file.write_text(json.dumps(rules), encoding="utf-8")

    inf = ConlangInflector(str(rules_file), str(keregafa_data_path))

    noun = inf.inflect_noun("kage")
    assert noun["nominative"] == "kage"
    assert noun["accusative"] == "kagele"

    verb = inf.inflect_verb("kagi")
    assert verb["class"] == "all verbs"
    assert verb["tenses"]["present"] == "kagki"


def test_inflector_rejects_nonverb_with_minimal_rules(
    tmp_path: Path,
    keregafa_data_path: Path,
) -> None:
    rules = {
        "declensions": {"nominative": "@"},
        "suffixRules": {"U": {"U": "doNothing"}},
        "prefixRules": {"U": {"U": "doNothing"}},
        "tenses": {"i": {"_className": "all verbs", "present": "ki"}},
        "basicAttributes": {"verbEndings": ["i"]},
    }

    rules_file = tmp_path / "inflections.json"
    rules_file.write_text(json.dumps(rules), encoding="utf-8")

    inf = ConlangInflector(str(rules_file), str(keregafa_data_path))

    try:
        inf.inflect_verb("kage")
        assert False, "Expected exception for non-verb input"
    except Exception as ex:
        assert "not a valid verb" in str(ex)
