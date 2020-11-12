#!/usr/bin/env python3

"""
This module contains functions for generating random words. This is useful for
creating easily readable unique strings.
"""

import io
import json
import logging
import numpy
import random
import urllib.request

logger = logging.getLogger(__name__)


def get_random_phrase(**kwargs):
    """Get a random dash-separated n-words-length phrase.

    This may be preferable to a random hex string for user
    readability (e.g. log_id).

    Args:
        None

    **kwargs:
        min_length (int): Minimum character length per word.
        max_length (int): Maximum character length per word.
        POS_order (list): Part-of-speech order.

    Returns:
        phrase (str): Random phrase.
    """
    min_length = int(kwargs.setdefault('min_length', 2))
    max_length = int(kwargs.setdefault('max_length', 8))
    POS_order = kwargs.setdefault(
        'POS_order',
        ['adverb', 'adjective', 'noun'],
    )
    words_url = "https://raw.githubusercontent.com/palmdalian/json_wordlist/master/wordlist_nocaps_byPOS.json"
    f = urllib.request.urlopen(words_url)
    words = json.loads(f.read())  # dict keys are part-of-speech (POS)
    good_word_list = []
    while len(POS_order) > 0:
        word = random.choice(words[POS_order[0]])
        word = word.replace(' ', '')
        if len(word) >= min_length:
            if len(word) <= max_length:
                good_word_list.append(word)
                POS_order.pop(0)
    phrase = "-".join(good_word_list)
    return phrase

def get_random_phrase_probability(**kwargs):
    """Get the probability of a n-words-length phrase being randomly
     selected from word list.

    This is useful to gauge how long to make a random phrase to preserve
    uniqueness of database entries. The smaller the probability, the less
    likely it will be repeated. Compare the order of magnitude of probability
    to the order of magnitude of expected database entries.

    Args:
        None

    **kwargs:
        min_length (int): Minimum character length per word.
        max_length (int): Maximum character length per word.
        POS_order (list): Part-of-speech order.

    Returns:
        prob (float) = Probability of duplicate phrase being selected.
    """
    min_length = int(kwargs.setdefault('min_length', 2))
    max_length = int(kwargs.setdefault('max_length', 8))
    POS_order = kwargs.setdefault(
        'POS_order',
        ['adverb', 'adjective', 'noun'],
    )
    words_url = "https://raw.githubusercontent.com/palmdalian/json_wordlist/master/wordlist_nocaps_byPOS.json"
    f = urllib.request.urlopen(words_url)
    words = json.loads(f.read())  # dict keys are part-of-speech (POS)
    prob = 1.00
    # For each POS, divide prob by frequency of n-char-length word.
    for POS in POS_order:
        len_c = [len(i) for i in words[POS]]
        array_c = numpy.array([[j, len_c.count(j)] for j in set(len_c)])
        min_row = int(numpy.where(array_c[:, 0] == min_length)[0])
        max_row = int(numpy.where(array_c[:, 0] == max_length)[0]) + 1
        num_words = array_c[min_row:max_row, 1].sum()
        prob *= float(1 / num_words)
    return prob
