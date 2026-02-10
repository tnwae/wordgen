"""
Transcribe or detranscribe a list of words in a conlang.

Usage: python transcribe.py -i <input_file> [-o] [-s] -d <language_data_file>
    - input_file: A text file with one word per line.
    - -o: Optional flag to transcribe to another alphabet (default is detranscribe)
    - -s: Optional flag to sort the output words.
    - language_data_file: A JSON file containing the conlang's phonological rules.

Author: William Ellison <tnwae@pm.me>
License: WTFPLv2 (http://www.wtfpl.net/txt/copying/)
Web: https://github.com/tnwae/conlang-utils
"""

import argparse
import conlang_utils as cu

if __name__ == "__main__":
    parser = argparse.ArgumentParser("transcribe")
    parser.add_argument("-i",
                        "--infile",
                        help="input file (one word per line)",
                        type=str,
                        default="text")
    parser.add_argument("-o",
                        "--other",
                        help="transcribe to other alphabet",
                        action="store_true")
    parser.add_argument("-s",
                        "--sort",
                        help="sort the output",
                        action="store_true")
    parser.add_argument("-d",
                        "--languagedata",
                        help="language data file (default: keregafa.json)",
                        type=str,
                        default="./keregafa.json")

    args = parser.parse_args()
    words = args.infile
    transcribe_mode = args.other
    ruletab = args.languagedata

    cd = cu.ConlangData(ruletab)
    transcribe = cd.transcribe if transcribe_mode else cd.detranscribe
    transcribed = []

    with open(words, "r") as fh:
        for line in fh.readlines():
            transcribed.append(transcribe(line[:-1]))

    if args.sort:
        transcribed.sort()
        
    [print(word) for word in transcribed]
