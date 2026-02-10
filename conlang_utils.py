#!/usr/bin/env python3
"""
Conlang utility class.  Includes a variety of helper functions for working with
constructed languages as they are defined in various JSON rule tables.

The ConlangData class is the main export of this module; it provides storage
and utility functions for working with constructed languages and the words that
they contain.  The name of the class is a slight misnomer as it does far more than
merely serving as a container for data; it also provides methods for acting upon
the data thus stored.

The input JSON rule table format is documented in the file LanguageRulesTable.md
in the root of the project repository.

:author: William Ellison <waellison@gmail.com>
:license: WTFPL
"""

import sys
import json
import re
import unicodedata
import itertools
from random import random
from typing import List, Union
import numpy as np


class _Trie:
    """
    A trie data structure for storing a list of words.
    """

    def __init__(self):
        self.children = dict()
        self.is_end_of_word = False

    def insert(self, word: str) -> None:
        """
        Insert a word into the trie.

        :param word: The word to insert.
        :return: None
        """
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _Trie()
            node = node.children[ch]
        node.is_end_of_word = True


class ConlangData:
    """
    Storage class for constructed language data.
    """

    def __init__(self, ruletab_filename: str) -> None:
        """
        Create a new storage class.

        :param ruletab_filename: The filename of the rule table as `${LANG}.json`.
        """
        self.rule_table = ruletab_filename
        try:
            with open(self.rule_table) as fp:
                raw = json.load(fp)
                self.basic_attributes = raw["basicAttributes"]
                self.consonant_freqtab = raw["consonantFrequencies"]
                self.vowel_freqtab = raw["vowelFrequencies"]
                self.phoneme_classes = raw["phonemeClasses"]
                self.word_types = raw["wordTypes"]
                self.syllable_types = raw["syllableClasses"]
                self.voicing_rules = raw.get("voicingRules", None)
                self.replacement_rules = raw.get("replacementRules", None)
                self.harmony_rules = raw.get("harmonyRules", None)
                self.tunings = raw.get("tuning", None)
                self.suffix_rules = raw.get("suffixRules", None)
                self.prefix_rules = raw.get("prefixRules", None)
                self.transcription = raw.get("transcriptionRules", None)
        except KeyError as ex:
            sys.stderr.write(f"missing required configuration key {ex}")
            sys.stderr.write(
                "please refer to example.json and the readme for details")
            sys.exit(1)

        consonants = [ltr for ltr in self.consonant_freqtab.keys()]
        vowels = [ltr for ltr in self.vowel_freqtab.keys()]
        self.phonemes = vowels + consonants

        self.token_trie = _Trie()
        for phoneme in self.phonemes:
            self.token_trie.insert(phoneme)

    def harmonize(self, word: List[str], nucleus_vowel: str) -> List[str]:
        """
        Impose vowel harmony rules upon the passed word.

        :param word: The word to harmonize.
        :return: The word with harmony rules applied.
        """
        nucleus_vowel_class = None
        if not self.harmony_rules or not nucleus_vowel:
            return word
        else:
            harmonized_word = word
            vowel_classes = self.harmony_rules["vowelClasses"]
            for klass, vowels in vowel_classes.items():
                if nucleus_vowel in vowels:
                    nucleus_vowel_class = klass

            if not nucleus_vowel_class:
                raise Exception(
                    f"nucleus vowel {nucleus_vowel} not in any vowel class\n(potential classes are [{vowel_classes.keys()}])"
                )
            counterparts = self.harmony_rules["counterparts"][
                nucleus_vowel_class]
            for i in range(len(word)):
                ch = word[i]
                subst = counterparts.get(ch) or ch
                harmonized_word[i] = subst
            return harmonized_word

    def compile_char(self, ch: str, syllable_index: int, phoneme_index: int,
                     syllable_len: int, syllable_count: int) -> str:
        """
        Compile a character given its class.

        :param ch: The character to compile.
        :param syllable_index: The index of the syllable within the word that
            contains it.
        :param phoneme_index: The index of the phoneme within the syllable that
            contains it.
        :param syllable_len: The length, in phonemes, of the syllable.
        :param syllable_count: The total number of syllables in the word.
        :return: The compiled character.
        """
        freqtab = {}
        vowel = False
        
        if ch == "V" or ch in self.basic_attributes.get("vowelClasses", []):
            freqtab = self.vowel_freqtab
            vowel = True
        elif ch == "C" or ch in self.basic_attributes.get("consonantClasses", []):
            freqtab = self.consonant_freqtab
            vowel = False

        if ch.isupper():
            if ch == "C":
                consonants = list(self.consonant_freqtab.keys())
                phonemes_in_class = consonants
            elif ch == "V":
                vowels = list(self.vowel_freqtab.keys())
                phonemes_in_class = vowels
            else:
                phonemes_in_class = self.phoneme_classes[ch]

            compiled = ""

            while compiled not in phonemes_in_class:
                compiled = np.random.choice(list(freqtab.keys()),
                                            1,
                                            p=list(freqtab.values()))

            retval = compiled[0]

            if vowel:
                lengthen_values = self._get_vowel_length_tunings()

                if lengthen_values and lengthen_values["lengthen"]:
                    lengthenable_vowels = lengthen_values["vowels"]
                    if (not lengthenable_vowels or \
                            compiled[0] in lengthenable_vowels):
                            retval = lengthen_values["lengthenRule"](
                            compiled[0])
            else:
                geminate_values = self._get_gemination_tunings()
                geminatable_consonants = geminate_values.get(
                    "consonants", [])
                can_geminate = geminate_values.get("geminate", False)

                at_last_sound = syllable_index == syllable_count - 1 and \
                                phoneme_index == syllable_len - 1

                at_first_sound = syllable_index == 0 and \
                                    phoneme_index == 0

                geminate_last_sound = at_last_sound and \
                                        geminate_values.get("geminateLastSound", False)

                geminate_first_sound = at_first_sound and \
                                        geminate_values.get("geminateFirstSound", False)

                can_geminate_last_sound = (
                    at_last_sound
                    and geminate_last_sound) or not at_last_sound
                can_geminate_first_sound = (
                    at_first_sound
                    and geminate_first_sound) or not at_first_sound

                if geminatable_consonants:
                    if compiled[0] in geminatable_consonants:
                        phoneme = compiled[0]
                    else:
                        phoneme = None
                else:
                    phoneme = compiled[0]

                # Geminate the consonant if we are allowed to:
                # - If the RNG says we can, and
                # - If the consonant is in the gemination list, and
                # - If the last sound rule is satisfied (either we are not
                #   at the last sound of the word, or we are and we are
                #   allowed to geminate it)
                if phoneme and can_geminate and \
                    (can_geminate_first_sound and can_geminate_last_sound):
                    retval *= 2

            return retval
        else:
            return ch

    def _get_gemination_tunings(self) -> dict:
        """
        Retrieve gemination tunings from the rule table, if they exist.

        :return: The gemination tunings, if they exist, as a dictionary.  An
            empty dict if there are no gemination tunings for this language.
        """
        retval = dict()
        if self.tunings:
            chance = self.tunings.get("geminateConsonantChance", None)
            if chance:
                retval["geminate"] = (chance > random())
                retval["consonants"] = self.tunings.get(
                    "geminatableConsonants", None)
                retval["geminateLastSound"] = self.tunings.get(
                    "geminateLastWordSound", False)
                return retval

        return {}

    def _get_vowel_length_tunings(self) -> Union[dict, None]:
        """
        Retrieve vowel length tunings from the rule table, if they exist.

        :return: The vowel length tunings, if they exist, as a dictionary.  An
            empty dict if there are no vowel length tunings for this language.
        """
        retval = dict()
        lengthen_rules = {
            "macron":
            (lambda ch: unicodedata.normalize("NFC", ch + chr(0x0304))),
            "double": (lambda ch: ch + ch)
        }
        if self.tunings:
            chance = self.tunings.get("lengthenVowelChance", None)
            if chance:
                lengthen_style = self.tunings.get("lengthenOrthography",
                                                  "double")
                retval["lengthen"] = (chance > random())
                retval["vowels"] = self.tunings.get("lengthenableVowels", None)
                retval["lengthenRule"] = lengthen_rules[lengthen_style]
                return retval

        return None

    def _get_reduplicate_tunings(self) -> Union[dict, None]:
        """
        Retrieve reduplication tunings from the rule table, if they exist.

        :return: The reduplication tunings, if they exist, as a dictionary.  An
            empty dict if there are no reduplication tunings for this language.
        """
        retval = dict()
        if self.tunings:
            chance = self.tunings.get("reduplicateChance") or None
            if chance:
                retval["reduplicate"] = (chance > random())
                retval["initialVoice"] = self.tunings.get(
                    "reduplicateWithInitialVoicing") or False
                return retval

        return None

    def reduplicate(self, word: list) -> Union[list, None]:
        """
        Reduplicate the passed word and return the result.

        :param word: The word to reduplicate.
        :return: The reduplicated word as a list of characters, or None if
            reduplication is not to be performed.
        """
        reduplicate_tunings = self._get_reduplicate_tunings()

        if reduplicate_tunings and reduplicate_tunings["reduplicate"] \
                               and len(word) < 6:
            reduplicated = word[:] * 2

            # de/voice the first consonant of the reduplicated root
            # (e.g. tutu => tudu) if the tunings say to do so - this is
            # like Japanese rendaku
            if reduplicate_tunings["initialVoice"]:
                reduplicated[len(word)] = self.voice_consonant(
                    reduplicated[len(word)])
            return reduplicated

        return None

    def is_vowel(self, ch: str) -> bool:
        """
        Determine if the passed character is a vowel.

        :param ch: The character to check.
        :return: True if the character is a vowel, False otherwise.
        """
        vowel_classes = [klass for klass in self.basic_attributes.get("vowelClasses", [])]
        if not vowel_classes:
            vowel_classes = ["V"]
        
        for klass in vowel_classes:
            vowel_class = self.phoneme_classes.get(klass, [])
            if ch in vowel_class:
                return True

        return False                

    def is_consonant(self, ch: str) -> bool:
        """
        Determine if the passed character is a consonant.

        :param ch: The character to check.
        :return: True if the character is a consonant, False otherwise.
        """
        consonant_classes = [klass for klass in self.basic_attributes.get("consonantClasses", [])]
        if not consonant_classes:
            consonant_classes = ["C"]
        
        for klass in consonant_classes:
            if ch in self.phoneme_classes.get(klass, []):
                return True

        return False
    
    def voice_consonant(self, ch: str) -> str:
        """
        Voice a voiceless consonant if it has a voicing counterpart.
        :param ch: The consonant to voice.
        :return: The voiced counterpart of the consonant, or the original
            consonant if it lacks a voicing counterpart.
        """ 
        return self.voicing_rules.get(ch, ch)

    def devoice_consonant(self, ch: str) -> str:
        """
        Devoice a voiced consonant if it has a voiceless counterpart.
        
        :param ch: The consonant to devoice.
        :return: The voiceless counterpart of the consonant, or the original
            consonant if it lacks a voiceless counterpart.
        """
        reversed_voicing = {v: k for k, v in self.voicing_rules.items()}
        return reversed_voicing.get(ch, ch)

    def compile_syllable_class(self, ch: str) -> str:
        """
        Get a randomly selected character for a given character class.

        :param ch: The character class to get a random character for.
        :return: The randomly selected character.
        :raise: KeyError if the character class is not recognized.
        """
        if ch in self.syllable_types.keys():
            freqtab = self.syllable_types[ch]
            compiled = np.random.choice(list(freqtab.keys()),
                                        1,
                                        p=list(freqtab.values()))

            return compiled[0]
        else:
            raise KeyError(ch)

    def tokenize_word(self, word: str) -> List[str]:
        """
        Tokenize a word into its constituent phonemes.

        :param word: The word to tokenize.
        :return: The word as a list of phonemes.
        """
        tokens = []
        n = len(word)
        i = 0

        while i < n:
            node = self.token_trie
            j = i
            last_match = -1
            while j < n and word[j] in node.children:
                node = node.children[word[j]]
                if node.is_end_of_word:
                    last_match = j
                j += 1

            if last_match == -1:
                tokens.append(word[j])
                i += 1

            else:
                tokens.append(word[i:last_match + 1])
                i = last_match + 1

        return tokens

    def detokenize_word(self, word: List[str]) -> str:
        """
        Concatenate a word from its constituent phonemes.

        :param word: The word to concatenate.
        :return: The word as a string.
        """
        return "".join(word)

    def _find_consonants(self, word: List[str]) -> List[str]:
        """
        Find all consonants in a word.

        :param word: The word to find consonants in.
        :return: A list of consonants in the word.
        """
        return [ch for ch in word if not self.is_vowel(ch)]

    def _find_vowels(self, word: List[str]) -> List[str]:
        """
        Find all vowels in a word.

        :param word: The word to find vowels in.
        :return: A list of vowels in the word.
        """
        return [ch for ch in word if self.is_vowel(ch)]

    def _give_last_consonant(self, word: List[str]) -> List[str]:
        """
        Retrieve the last consonant in a word.

        :param word: The word to retrieve the last consonant from.
        :return: The last consonant in the word.
        """
        return [self._find_consonants(word)[-1]]

    def _give_last_vowel(self, word: List[str]) -> List[str]:
        """
        Retrieve the last vowel in a word.

        :param word: The word to retrieve the vowel from.
        :return: The last vowel in the word.
        """
        return [self._find_vowels(word)[-1]]

    def append_last_consonant(self, word: List[str]) -> List[str]:
        """
        Append a word's final consonant to the end of the word.

        :param word: The word to append the consonant to.
        :return: The word with its last consonant appended.
        """
        return word + self._give_last_consonant(word)

    def append_last_vowel(self, word: List[str]) -> List[str]:
        """
        Append a word's final vowel to the end of the word.

        :param word: The word to append the vowel to.
        :return: The word with its last vowel appended.
        """
        return word + self._give_last_vowel(word)

    def delete_last_char(self, word: List[str]) -> List[str]:
        """
        Remove the last character from a word.

        :param word: The word to remove the last character from.
        :return: The word without its last character.
        """
        return word[:-1]

    def do_nothing_for_inflection(self, word: List[str]) -> List[str]:
        return word

    def get_char_class(self, ch: str, generic: bool = False) -> str:
        """
        Get the character class of the passed character.

        :param ch: The character to get the class of.
        :return: The class of the specified character if it is found.
        :raise: KeyError if the the passed character does not refer to any
            specified classes.
        """
        if generic:
            if self.is_vowel(ch):
                return "V"
            elif self.is_consonant(ch):
                return "C"
        else:
            for klass, members in self.phoneme_classes.items():
                if ch in members:
                    return klass
            else:
                raise KeyError(f"invalid character {ch}")

    def transcribe(self, word: str) -> str:
        """
        Transcribe a word into a different writing system as specified in the
        rule table.

        :param word: The word to transcribe.
        :return: The word transcribed into the other writing system.
        """
        retval = word
        for source, dest in self.transcription.items():
            retval = re.sub(source, dest, retval)
        return retval

    def detranscribe(self, word: str) -> str:
        """
        Detranscribe a word from a different writing system as specified in the
        rule table.

        :param word: The word to detranscribe.
        :return: The word in the Latin script.
        """
        retval = word
        for source, dest in self.transcription.items():
            retval = re.sub(dest, source, retval)
        return retval
