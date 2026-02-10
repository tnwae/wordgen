"""
Generate random words based on a simple syllable structure.
By default, generates 1000 words with 1-5 syllables each.

Usage: python permuter.py
Author: William Ellison <tnwae@pm.me>
License: WTFPLv2 (http://www.wtfpl.net/txt/copying/)
Web: https://github.com/tnwae/conlang-utils
"""

import random

vowels = ['a', 'e', 'i', 'o', 'u']
consonants = [
    '', 'b', 'd', 'f', 'g', 'h', 'l', 'j', 'k', 'm', 'n', 'p', 's', 't', 'ts',
    'w', 'z'
]


def make_syllable() -> str:
    vowel = vowels[random.randint(0, len(vowels) - 1)]
    consonant = consonants[random.randint(0, len(consonants) - 1)]
    return f"{consonant}{vowel}"


def make_word(syllable_count: int = 3) -> str:
    return "".join([make_syllable() for i in range(syllable_count)])


def times(func, *params, count: int):
    return [func() for i in range(count)]


def main():
    words = set()

    while len(words) < 1000:
        word = make_word(random.randint(1, 5))
        words.add(word)

    for word in sorted(list(words)):
        print(word)


if __name__ == "__main__":
    main()
