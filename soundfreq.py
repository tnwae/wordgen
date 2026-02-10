"""
Calculate phoneme frequencies from a list of words in a conlang.

Usage: python soundfreq.py -i <input_file> -d <language_data_file> [-p]
    - input_file: A text file with one word per line.
    - language_data_file: A JSON file containing the conlang's phonological rules.
    - -p: Optional flag to output percentages instead of raw counts.

Author: William Ellison <tnwae@pm.me>
License: WTFPLv2 (http://www.wtfpl.net/txt/copying/)
"""

import argparse
import conlang_utils as cu
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser("transcribe")
    parser.add_argument("-i",
                        "--infile",
                        help="input file (one word per line)",
                        type=str,
                        default="text")
    parser.add_argument("-d",
                        "--languagedata",
                        help="language data file (default: keregafa.json)",
                        type=str,
                        default="./keregafa.json")
    parser.add_argument(
        "-p",
        "--percentages",
        help="give percentages of phoneme instead of raw counts",
        action="store_true",
        default=False)

    args = parser.parse_args()
    words = args.infile
    ruletab = args.languagedata
    pct = args.percentages

    cd = cu.ConlangData(ruletab)
    consonants = dict()
    vowels = dict()
    token_count = 0
    total_vowels = 0
    total_consonants = 0

    with open(words, "r") as fh:
        words = fh.readlines()

        for word in words:
            tokens = cd.tokenize_word(word[:-1].lower())

            for token in tokens:
                if cd.is_vowel(token):
                    total_vowels += 1
                    token_count += 1
                    if token not in vowels:
                        vowels[token] = 1
                    else:
                        vowels[token] += 1
                elif cd.is_consonant(token):
                    total_consonants += 1
                    token_count += 1
                    if token not in consonants:
                        consonants[token] = 1
                    else:
                        consonants[token] += 1

    assert (token_count == total_vowels + total_consonants)

    if pct:
        print(
            json.dumps(
                {
                    "phonemeCount": token_count,
                    "vowelCount": total_vowels,
                    "consonantCount": total_consonants,
                    "vowels": {
                        vowel: round(vowels[vowel] / total_vowels, 4)
                        for vowel in vowels
                    },
                    "consonants": {
                        consonant:
                        round(consonants[consonant] / total_consonants, 4)
                        for consonant in consonants
                    }
                },
                indent=4))
    else:
        print(
            json.dumps(
                {
                    "phonemeCount": token_count,
                    "vowelCount": total_vowels,
                    "consonantCount": total_consonants,
                    "vowels": vowels,
                    "consonants": consonants
                },
                indent=4))
