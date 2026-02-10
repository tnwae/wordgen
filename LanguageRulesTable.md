Language Rules Table - Description
==================================

The language rules table is meant to describe the component parts of a constructed language in terms of its phonology and morphology.  It is designed in a modular fashion so that you can fully describe the way in which your language builds words.  The file is stored in JavaScript Object Notation ("JSON").

If you are unfamiliar with JSON, I recommend [this tutorial](https://jsonutils.org/blog/complete-json-guide-for-beginners.html).

If you are unfamiliar with the principles of linguistics mentioned in this documentation, I recommend the course [24.917](https://ocw.mit.edu/courses/24-917-conlangs-how-to-construct-a-language-fall-2018/) at MIT OCW or the text _Linguistics: an Introduction_ by Donna Jo Napoli (Oxford University Press), among other introductory resources on linguistics.



Basic Attributes (`basicAttributes`)
------------------------------------

minWordLength
: the minimum length of a generated word (in syllables)

maxWordLength
: the maximum length of a generated word (in syllables)

langName
: the name of the language

langAuthor
: the author of the language

langAuthorEmail
: the email address corresponding to `langAuthor`

langWebsite
: link to a website containing information about the language

configVersion
: the version of the configuration file (not currently used, set to 1)

vowelClasses
: a list of phoneme classes considered to be vowels (defaults to only `V`)

consonantClasses
: a list of phoneme classes considered to be consonants (defaults to only `C`)



Consonant Frequency Table (`consonantFrequencies`)
--------------------------------------------------

This is a series of key/value pairs where each pair represents a consonant phoneme in the language and its relative frequency.  The sum of all frequencies must sum to 1.

As an example, consider the below simple frequency table:

```json
"consonantFreqencies": {
    "p": 0.25,
    "m": 0.25,
    "t": 0.25,
    "k": 0.25
}
```

In this frequency table, the phonemes _k_, _m_, _p_, and _t_ are equiprobable.



Vowel Frequency Table (`vowelFrequencies`)
------------------------------------------

Like `consonantFrequencies`, this is a series of key-value pairs representing vowel phonemes in the language and their relative frequencies.  As with consonants, the sum of vowel frequencies must sum to 1.

As an example, consider the below simple consonant frequency table:

```json
"vowelFrequencies": {
    "a": 0.5,
    "o": 0.5
}
```

In this frequency table, the vowels _a_ and _o_ are equiprobable.



Voicing Rules (`voicingRules`)
------------------------------

These is a series of key-value pairs representing voicing rules for your language's consonants.  It is keyed on the voiceless consonant and maps it to the voiceless counterpart.  Handling the reverse relationship is done in software.

Examples from the configuration file:

```json
"voicingRules": {
    "k": "g",
    "t": "d",
    "p": "b",
    "s": "z",
    "f": "v"
}
```



Phoneme Classes (`phonemeClasses`)
----------------------------------

You may define multiple phoneme classes that are used when specifying syllable shapes.  In the basic case, you need one class called `V` for vowels and one class called `C` for consonants.  Each phoneme class maps to an array of phonemes belonging to that class.

```json
"phonemeClasses": {
    "V": ["a", "o"],
    "C": ["p", "t", "k", "m"]
}
```

You can use the phoneme classes to specify, among other things, permissible constituents for consonant clusters and diphthongs (if you do not just define your diphthtongs as regular vowels).  This allows you to specify your language's sonority hierarchy and thus at least one layer of your phonotactics.  (For one example, you could have a class `L` for liquid consonants, allowing clusters like `dr` (drive), `cl` (clear), and `sw` (swim) like in English.)

**Important Caveats**

- Class names must consist of one single capital letter.

- Phoneme classes __must__ be disjoint (i.e., a phoneme cannot belong to two classes simultaneously)



Syllable Classes (`syllableClasses`)
------------------------------------

Each syllable type defined in this segment of the configuration file specifies a set of syllable shapes that is permissible for that syllable class.  You may define a syllable shape using bare phonemes and phoneme classes.  Bare phonemes are specified using lowercase letters, while phoneme classes are specified using uppercase letters.

Each syllable shape within a given class is given a probability of occurring in the random output.  The probabilities must sum to 1 for each syllable class.

As an example, consider the syllable class definitions from my language Keregafa:

```json
"syllableClasses": {
    "I": {
        "V": 0.25,
        "CV": 0.75
    },
    "M": {
        "CV": 1
    },
    "F": {
        "CV": 0.6,
        "CVC": 0.4
    },
    "V": {
        "bu": 0.3,
        "fu": 0.15,
        "ku": 0.15,
        "mu": 0.1,
        "tsu": 0.3
    },
    "A": {
        "di": 0.6,
        "ni": 0.4
    }
}
```

Initial, medial, and final syllables are given using the `I`, `M`, and `F` syllable classes respectively.  In this example, I am using syllable class `V` to indicate verb endings and syllable class `A` to indicate adjective endings.  If your language uses word prefixes (like Swahili) or suffixes (like many Romance languages) to indicate noun class, you could specify syllable classses for these classes.

**Class names must consist of one capital letter.**



Word Types (`wordTypes`)
------------------------



Replacement Rules (`replacementRules`)
--------------------------------------



Tuning (`tuning`)
-----------------
Wordgen supports several tuning options to further refine the words that are generated.

* `geminateConsonantChance`: The chance that a consonant will be geminated (denoted in the spelling by doubling the consonant, as in Italian or Japanese R&omacr;maji).  Number between 0 and 1 denoting the percentage chance that any given consonant will be geminated.

* `geminatableConsonants`: Consonants that are subject to gemination if `geminateConsonantChance` is nonzero.  Array of consonant phonemes.

* `geminateLastWordSound`: Whether to geminate the final consonant of a word if that is the last sound in the word.  Boolean.

* `lengthenVowelChance`: The chance that a vowel will be lengthened (designated with macrons, like in Hawaiian, or with doubled consonants, like in Finnish).  Number between 0 and 1 denoting the percentage chance that any given vowel will be lengthened.  Wordgen does not currently support overlong vowels (as in Estonian).

* `lengthenableVowels`: Vowels that are subject to lengthening if `lengthenVowelChance` is nonzero.  Array of vowel phonemes.

* `lengthenOrthography`: How to spell lengthened vowels.  String set to `"double"` if doubling is used (e.g., [a:] becomes &lsaquo;aa&rsaquo;) or `"macron"` if macrons are used (e.g., [a:] becomes &amacr;).  Wordgen does not currently support other renderings of lengthened vowels like &lsaquo;o&#x030B;&rsaquo; from Hungarian, but such support would not be difficult to add.

* `reduplicateChance`: The chance that a generated word will be reduplicated in the output.  Reduplication is simply the repetition of a word root, such as in Mandarin <span lang="zh">&#x4eba;&#x4eba;</span> (r&eacute;nr&eacute;n), which forms "everybody" or "all of us" from <span lang="zh">&#x4eba;</span> (r&eacute;n), meaning "person."  Number between 0 and 1 denoting the percentage chance that any given word will be reduplicated.

* `reduplicateWithInitialVoicing`: Whether to alternate voicing of the initial consonant in a reduplicated word.  This is a common manifestation of the phenomenon called <span lang="ja">連濁</lang> _rendaku_ in Japanese, where the initial consonant in compounds receives voicing, such as 紙 (_kami_) becoming _gami_ in the compound 折り紙 (_origami_).  This is common in reduplicated words as well, such as &#x4eba;&#x4eba; (_hitobito_) being composed of &#x4eba; (_hito_) repeated.
