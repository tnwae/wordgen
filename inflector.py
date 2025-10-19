#!/usr/bin/env python3

import json
import sys
import re
from typing import Tuple, List
import conlang_utils as cu

noun_templates = dict()
noun_inflection_rules = dict()
mood_templates = dict()
tense_templates = dict()
converb_templates = dict()
basic_attributes = dict()
tunings = None
conlang_data = None


class ConlangInflector:
    def __init__(self, ruletab: str, datatab: str):
        self.conlang_data = cu.ConlangData(datatab)

        try:
            with open(ruletab, "r") as fp:
                raw = json.load(fp)
                self.noun_templates = raw["declensions"]
                self.suffixing_rules = raw["suffixRules"]
                self.prefixing_rules = raw["prefixRules"]
                self.tense_templates = raw["tenses"]
                self.basic_attributes = raw["basicAttributes"]
                self.tunings = raw.get("tunings") or None
        except FileNotFoundError as ex:
            print(ex)
            sys.exit(1)

        self.INFLECTION_ACTIONS = {
            "deleteLastChar": self.conlang_data.delete_last_char,
            "appendLastVowel": self.conlang_data.append_last_vowel,
            "appendLastConsonant": self.conlang_data.append_last_consonant,
            "doNothing": self.conlang_data.do_nothing_for_inflection
        }

    def inflect_noun(self, word: str) -> dict:
        inflections = dict()

        # FIXME: Don't assume that noun declensions are applied through
        # suffixes.
        for case_name, suffix in self.noun_templates.items():
            if suffix == "@":
                inflections[case_name] = word
                continue

            inflections[case_name] = self._inflect_suffix(word, suffix)
            
        return inflections

    def _inflect_suffix(self, word: str, suffix: str) -> str:
        if suffix == "@":
            return word
        
        word_tokens = self.conlang_data.tokenize_word(word)
        suffix_tokens = self.conlang_data.tokenize_word(suffix)
        final_token_class = self.conlang_data.get_char_class(word_tokens[-1])
        case_ending_class = self.conlang_data.get_char_class(suffix_tokens[0])

        rule = self.suffixing_rules[final_token_class][case_ending_class]
        root_tokens = self.INFLECTION_ACTIONS[rule](word_tokens)
        final_word = root_tokens + suffix_tokens
        return self.conlang_data.detokenize_word(final_word)

    def _inflect_prefix(self, word: str, prefix: str) -> str:
        if prefix == "@":
            return word

        word_tokens = self.conlang_data.tokenize_word(word)
        prefix_tokens = self.conlang_data.tokenize_word(prefix)
        first_token_class = self.conlang_data.get_char_class(word_tokens[0])
        prefix_ending_class = self.conlang_data.get_char_class(prefix_tokens[-1])

        rule = self.prefixing_rules[prefix_ending_class][first_token_class]
        inflected_tokens = self.INFLECTION_ACTIONS[rule](prefix_tokens)
        final_word = inflected_tokens + word_tokens
        return self.conlang_data.detokenize_word(final_word)

    def inflect_verb(self, word: str) -> dict:
        endings = self.basic_attributes["verbEndings"]
        verb_class = ""

        for ending in endings:
            if re.findall(f"{ending}$", word):
                verb_class = ending
                break
        else:
            raise Exception(f"{word} is not a valid verb")
        
        root = word[:-len(verb_class)]
        tense_rules = {k: v
                       for k, v in self.tense_templates[verb_class].items()
                       if k != "_className"}
        verb_class_name = self.tense_templates[verb_class]["_className"]
        inflection = {"class": verb_class_name,
                      "tenses": {},
                      "moods": {},
                      "converbs": {}}

        # FIXME: Don't assume that tense affixes are suffixes.
        for tense, tense_ending in tense_rules.items():
            inflection["tenses"][tense] = root + tense_ending

        return inflection


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("inflector")
    parser.add_argument("-L",
                        "--language",
                        help="language (default: keregafa)",
                        type=str,
                        default="keregafa")
    parser.add_argument("word", help="word to inflect", type=str)
    parser.add_argument("-t",
                        "--type",
                        help="type of inflection to perform",
                        type=str,
                        default="n")
    args = parser.parse_args()

    ruletab = f"./{args.language}_inflections.json"
    datatab = f"./{args.language}.json"

    ci = ConlangInflector(ruletab, datatab)
    inflectors = {"v": ci.inflect_verb, "n": ci.inflect_noun}

    inflector = inflectors[args.type]
    inflected_word = inflector(args.word)

    print(json.dumps(inflected_word, indent=4))
