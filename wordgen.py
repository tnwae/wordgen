#!/usr/bin/env python3

from typing import Union
import re
import json
import sys
import numpy as np
import conlang_utils as cu


class WordBuilder:
    """
        Word builder for constructed languages.  Works from a user-provided input specification.
    """


    def __init__(self, ruletab: str):
        self._ruletab = ruletab
        self.conlang_data = cu.ConlangData(ruletab)
        self.results = set()

    def run(self,
            count: int,
            template: Union[str, None],
            length: int,
            type: str,
            transcribe: bool = False) -> None:
        """
            Run the word generator.

            :param count: number of words to generate
            :param template: template for generating the word (randomly chosen if None)
            :param length: number of syllables in the generated word
            :param transcribe: if True, transcribe generated words in the specified alternate script
        """

        # Bound the length of the generated word based on the conlang data file
        min_syllables = self.conlang_data.basic_attributes["minWordLength"]
        max_syllables = self.conlang_data.basic_attributes["maxWordLength"]

        # And go!
        while len(self.results) < count:
            if length == 0:
                word_length = np.random.randint(min_syllables,
                                                max_syllables + 1)
            else:
                word_length = length

            self.make_word(word_length, template, type, transcribe)

    def make_word(self,
                  syllable_count: int = 0,
                  template: Union[str, None] = None,
                  type: str = "noun",
                  transcribe: bool = False) -> None:
        """
            Generate a word.

            :param syllable_count: number of syllables in the generated word
            :param template: template for generating the word (randomly chosen if None)
            :param transcribe: if True, transcribe generated words in the specified alternate script
        """

        word_template = ""
        created_word = []
        result = []
        syllables = []

        # choose a template if we didn't pass one in
        if not template:
            word_types = list(self.conlang_data.word_types[type].keys())
            word_type_weights = list(
                self.conlang_data.word_types[type].values())
            word_template = np.random.choice(word_types,
                                             1,
                                             p=word_type_weights)[0]
        else:
            word_template = template

        # parse the word template for the character classes it contains and
        # fail if an unknown character class is part of the template
        try:
            syllables = [
                self.conlang_data.compile_syllable_class(ch)
                for ch in word_template
            ]
        except KeyError as ex:
            print(f"missing character type '{ex}' (template: {word_template})")
            print(f"please check `{self._ruletab}`")
            sys.exit(1)

        # generate the word
        for w_idx, syllable in enumerate(syllables):
            for s_idx, ch in enumerate(list(syllable)):
                created_word.append(
                    self.conlang_data.compile_char(ch, w_idx, s_idx,
                                                   len(syllable),
                                                   len(syllables)))

        # if this language specifies vowel harmony rules, harmonize the
        # vowels in the word accordingly, using the first vowel as the
        # nucleus (like Turkish).
        if self.conlang_data.harmony_rules:
            gen = (letter for letter in created_word
                   if self.conlang_data.is_vowel(letter))
            self.conlang_data.harmonize(created_word, next(gen))

        result.append("".join(created_word))

        # if this language allows reduplication, see if we will reduplicate the
        # word and then add it and its reduplicated from if so
        reduplicated = self.conlang_data.reduplicate(created_word)
        if reduplicated:
            result.append("".join(reduplicated))

        # if there are text-replacement fine tunings (for orthographic
        # considerations, e.g.), apply those now.
        if self.conlang_data.replacement_rules:
            for rule, filters in self.conlang_data.replacement_rules.items():
                for filter, target in filters.items():
                    for i in range(0, len(result)):
                        result[i] = re.sub(filter, target, result[i])

        # transcribe if necessary and then add to the output.
        if self.conlang_data.transcription and transcribe:
            [self.results.add(self.conlang_data.transcribe(w)) for w in result]
        else:
            [self.results.add(w) for w in result]


def main(p_language="keregafa",
         p_count=1,
         p_template=None,
         p_transcribe=False,
         p_word_length=1,
         p_format="text",
         p_type="noun",
         p_interactive=True):

    if p_interactive:
        args = _parse_args()

        language = args.language
        word_count = args.count
        template = args.template
        word_length = args.word_length
        transcribe = args.transcribe
        type = args.type
        format = args.format
    else:
        language = p_language
        word_count = p_count
        template = p_template
        word_length = p_word_length
        transcribe = p_transcribe
        type = p_type
        format = p_format

    wb = WordBuilder(f"./{language}.json")

    wb.run(word_count, template, word_length, type, transcribe)

    if format == "json":
        print(json.dumps(sorted(wb.results)))
    else:
        for word in sorted(wb.results):
            print(word)


def _parse_args():
    import argparse
    parser = argparse.ArgumentParser("wordgen")

    parser_arguments = [
        ("-L", "--language", "language rule file", str, "keregafa"),
        ("-c", "--count", "number of words to generate", int, 1),
        ("-l", "--word-length", "number of syllables per word (0=random)", int, 0),
        ("-f", "--format", "output format (text|json)", str, "text"),
        ("-t", "--type", "word type (noun|verb|adj|adv|part)", str, "noun"),
        ("-T", "--template", "word template (randomly chosen if None)", str, None)
    ]

    for argument in parser_arguments:
        short, long, help_text, arg_type, default = argument
        parser.add_argument(short,
                            long,
                            help=help_text,
                            type=arg_type,
                            default=default)

    parser.add_argument("-x",
                        "--transcribe",
                        default=False,
                        action="store_true")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
