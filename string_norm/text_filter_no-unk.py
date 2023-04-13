#!/usr/bin/python3
# -*- coding: utf-8 -*-
# How to run it: ### python3 text_filter.py $my_dir/data/train/text $my_dir/data/train/text_filter

import os, sys
from re import sub

# Perl file which converts digits into their orthographical transcription.
DIGITS_TO_WORDS_FILE_PATH = '/vol/tensusers4/bmolenaar/jasmin_data_prep/string_norm/map_digits_to_words_v2.pl'

if (len(sys.argv) < 3):
    print("You must add two arguments: input file and output file paths")
    sys.exit(-1)
input_file = sys.argv[1]
output_file = sys.argv[2]

TEXT_SEPARATOR = ' '
REPLACE_SYMBOLS = {'.': '', '?': '', '!': '', 'SIL': '', ',': '', '=': '-', "’": "'", '-': ''}  # +lowercase
REPLACE_WORDS = {'xxx': '', 'ggg': ''}
# DELETE_ONLY_BEGIN_END = ["-"]  # We want to keep "\'" 's 't
TEMPORAL_FILE = "tmp"


def map_digits(digits):
    m_text = digits
    if os.path.isfile(DIGITS_TO_WORDS_FILE_PATH):
        os.system(("echo \"" + m_text + "\"| perl " +
                   DIGITS_TO_WORDS_FILE_PATH + " > " + TEMPORAL_FILE))
        m_text = str(open(TEMPORAL_FILE, 'r').read()).replace('\n', '')
    else:
        print("DIGITS_TO_WORDS_FILE not found")
    return m_text


'''
Lowercase word with symbols replaced.
Also deletes any - at the beg/end of the word
'''


def clean_word(m_word):
    m_word = m_word.lower()
    for symbol in REPLACE_SYMBOLS:
        m_word = m_word.replace(symbol, REPLACE_SYMBOLS[symbol])
    # for m_symbol in DELETE_ONLY_BEGIN_END:
    #     if m_word.startswith(m_symbol):
    #         m_word = m_word[1:]
    #     if m_word.endswith(m_symbol):
    #         m_word = m_word[:m_word.rindex(m_symbol)]
    if m_word in REPLACE_WORDS:
        m_word = REPLACE_WORDS[m_word]
    if '*' in m_word:
        m_word = m_word[:m_word.index('*')]
    if '[' in m_word:
        m_word = m_word[:m_word.index('[')]
    if m_word.isdigit():
        m_word = map_digits(m_word)
    else:
        for character in m_word:
            if character.isdigit():
                # print(m_word)
                m_word = m_word[:m_word.index(character)] + map_digits(character)
    return m_word.lower()


def remove_accents_from_lower(raw_text):
    """Removes common accent characters from lowercase strings.
    Our goal is to brute force login mechanisms, and I work primary with
    companies deploying English-language systems. From my experience, user
    accounts tend to be created without special accented characters. This
    function tries to swap those out for standard English alphabet.
    """
    raw_text = sub(u"[àáâãäå]", 'a', raw_text)
    raw_text = sub(u"[èéêë]", 'e', raw_text)
    raw_text = sub(u"[ìíîï]", 'i', raw_text)
    raw_text = sub(u"[òóôõö]", 'o', raw_text)
    raw_text = sub(u"[ùúûü]", 'u', raw_text)
    raw_text = sub(u"[ýÿ]", 'y', raw_text)
    raw_text = sub(u"[ß]", 'ss', raw_text)
    raw_text = sub(u"[ñ]", 'n', raw_text)
    return raw_text


filtered_lines = []
set_symbols = set()
with open(input_file, 'r', encoding='utf-8') as input_text:
    for line in input_text:
        line = line.strip()
        fields = line.split(TEXT_SEPARATOR)
        # id=fields[0]
        utt = fields[0:]
        filtered_utt = []
        for word in utt:
            m_word = remove_accents_from_lower(clean_word(word))
            for i in m_word:
                set_symbols.add(i)
            filtered_utt.append(m_word)
        filtered_lines.append(' '.join(filtered_utt))

# for symbol in sorted(set_symbols):
#     print(symbol,end=' ')
# print()

with open(output_file, 'w', encoding='utf-8') as output_text:
    output_text.write('\n'.join(filtered_lines) + '\n')

if os.path.exists(TEMPORAL_FILE):
    os.remove(TEMPORAL_FILE)
