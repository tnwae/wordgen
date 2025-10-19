#!/usr/bin/env python3

import json
import sys
import re
from typing import Dict
import conlang_utils as cu


class ConlangAffixator:

    def __init__(self,
                 affix_ruletab: str,
                 datatab: str,
                 inflection_ruletab: str):
        """Create a new affixator object.

        :param affix_ruletab: The affix rule table, named
        `${LANG}_affixes.json`

        :param datatab: The data table, named `${LANG}.json`

        :param inflection_ruletab: The inflection rule table, named
            `${LANG}_inflections.json`

        """
        self.conlang_data = cu.ConlangData(datatab)

        try:
            with open(affix_ruletab, "r") as fp:
                raw = json.load(fp)
                self.suffixing_rules = raw["suffixRules"]
                self.prefixing_rules = raw["prefixRules"]
                self.affixes = raw["affixes"]
                self.basic_attributes = raw["basicAttributes"]
                self.tunings = raw.get("tunings") or None
        except FileNotFoundError as ex:
            print(ex)
            sys.exit(1)

        try:
            with open(inflection_ruletab, "r") as fp:
                raw = json.load(fp)
                self.tense_templates = raw["conjugationTable"]
                self.basic_attributes.update(raw["basicAttributes"])
        except FileNotFoundError as ex:
            print(ex)
            sys.exit(1)

        self.INFLECTION_ACTIONS = {
            "deleteLastChar": self.conlang_data.delete_last_char,
            "appendLastVowel": self.conlang_data.append_last_vowel,
            "appendLastConsonant": self.conlang_data.append_last_consonant,
            "doNothing": self.conlang_data.do_nothing_for_inflection
        }

    def _inflect_suffix(self, word: str, suffix: str) -> str:
        """
        Add a suffix to a word.

        :param word: The word to add the suffix to.
        :param suffix: The suffix to add.
        :return: The inflected word.
        """
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
        """
        Add a prefix to a word.

        :param word: The word to add the prefix to.
        :param prefix: The prefix to add.
        :return: The inflected word.
        """
        if prefix == "@":
            return word

        word_tokens = self.conlang_data.tokenize_word(word)
        prefix_tokens = self.conlang_data.tokenize_word(prefix)
        first_token_class = self.conlang_data.get_char_class(word_tokens[0])
        prefix_ending_class = self.conlang_data.get_char_class(
            prefix_tokens[-1])

        rule = self.prefixing_rules[prefix_ending_class][first_token_class]
        inflected_tokens = self.INFLECTION_ACTIONS[rule](prefix_tokens)
        final_word = inflected_tokens + word_tokens
        return self.conlang_data.detokenize_word(final_word)

    def affixate(self, word: str) -> Dict[str, str]:
        """
        Generate the inflected forms of a word.

        :param word: The word to inflect.
        :return: A dictionary of inflected forms keyed on the name of the form.
        """
        result = {}
        verb_endings = self.basic_attributes["verbEndings"]
        verb_inflection = None
        verb_class = None
        word_is_verb = False

        if self.tunings:
            verb_inflection = self.tunings.get("applySuffixToVerbForm", None)

        for verb_ending in verb_endings:
            if re.findall(f"{verb_ending}$", word):
                verb_class = verb_ending
                word_is_verb = True
                break

        for affix, rules in self.affixes.items():
            name = affix
            affixed_word = None
            affix_applies_to_verb = False
            affix_applies_to_noun = False
            word_receives_affix = False
            prefix = rules.get("prefix", None)
            suffix = rules.get("suffix", None)

            # If the verb class is set and the affix has a required verb
            # inflection, this implies that the affix is only applicable to
            # verbs.  Likewise, if the rule name for the affix includes "V-V"
            # (verb-verb derivation), "V-Adj" (verb-adjective derivation), or
            # "V-N" (verb-noun derivation), then the rule should apply to verbs.
            affix_applies_to_verb = any(["V-V" in name, "V-Adj" in name, "V-N" in name])
            affix_applies_to_noun = any(["N-V" in name, "N-N" in name])

            if affix_applies_to_verb and word_is_verb and prefix and not suffix:
                affixed_word = word
                word_receives_affix = True
            elif affix_applies_to_verb and word_is_verb and suffix:
                affixed_word = word[:-len(verb_class)] + \
                               self.tense_templates[verb_class][verb_inflection]
                word_receives_affix = True
            elif (not affix_applies_to_verb) and (not word_is_verb):
                affixed_word = word
                word_receives_affix = True

            if affixed_word and word_receives_affix:
                if prefix:
                    affixed_word = self._inflect_prefix(affixed_word, prefix)
                if suffix:
                    affixed_word = self._inflect_suffix(affixed_word, suffix)

                result[name] = affixed_word

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("affixator")
    parser.add_argument("-L",
                        "--language",
                        help="language (default: keregafa)",
                        type=str,
                        default="keregafa")
    parser.add_argument("word", help="word to inflect", type=str)
    parser.add_argument("-R",
                        "--raw-output",
                        help="output raw words",
                        action='store_true')
    args = parser.parse_args()

    affixes_ruletab = f"./{args.language}_affixes.json"
    conlang_datatab = f"./{args.language}.json"
    inflection_ruletab = f"./{args.language}_inflections.json"

    ci = ConlangAffixator(affixes_ruletab, conlang_datatab, inflection_ruletab)
    inflected_words = ci.affixate(args.word)

    if args.raw_output:
        for _, word in inflected_words.items():
            print(word)
    else:
        print(json.dumps(inflected_words, indent=4))
