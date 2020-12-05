#!/usr/bin/env python3

from engcommon.randomword import get_random_phrase
from engcommon.randomword import get_random_phrase_probability


def test_get_random_phrase(**kwargs):
    assert len(get_random_phrase().split("-")) == 3


def test_get_random_phrase_probability(**kwargs):
    assert isinstance(get_random_phrase_probability(), float)
