import permuter


def test_make_word_uses_requested_syllable_count(monkeypatch) -> None:
    monkeypatch.setattr(permuter, "make_syllable", lambda: "ka")

    assert permuter.make_word(3) == "kakaka"


def test_times_calls_function_count_times() -> None:
    counter = {"n": 0}

    def bump() -> int:
        counter["n"] += 1
        return counter["n"]

    values = permuter.times(bump, count=4)
    assert values == [1, 2, 3, 4]
