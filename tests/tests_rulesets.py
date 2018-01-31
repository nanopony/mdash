import json
import os

import pytest

from rutypograph import get_default_environment, Typograph
from rutypograph.environment import ExtraStyles
from rutypograph.rule import Rule



def test_extra_style():
    settings = get_default_environment()
    settings.extra_style = ExtraStyles.AS_CLASS
    assert Typograph.process("8 905 555-55-55", settings) == "<span class=\"nowrap\">8 905 555-55-55</span>"
    settings.extra_style = ExtraStyles.INLINE
    assert Typograph.process("8 905 555-55-55",
                             settings) == "<span style=\"word-spacing:nowrap;\">8 905 555-55-55</span>"


def test_all_rules():
    """
    All rules must compile without an exeption
    Also, execute "doctests" for each Rule, if defined
    """
    from rutypograph.rulesets import ALL_RULES
    settings = get_default_environment()
    for rule in ALL_RULES:
        assert isinstance(rule, Rule)
        for input_text, expected in rule.doctests:
            assert rule.apply(input_text, settings) == expected


with open(os.path.join(os.path.split(__file__)[0], 'fixtures', 'tests_utf8.json'), 'r') as inputfile:
    cases = json.load(inputfile)


@pytest.mark.parametrize("test_def", cases)
def test_old_tests(test_def):
    """
    Old testbase, will be generating lots of errors, since not all the features are ported
    :param test_def:
    :return:
    """
    settings = get_default_environment()
    assert Typograph.process(test_def['text'], settings, mangle_ampresand=False) == test_def['result']
