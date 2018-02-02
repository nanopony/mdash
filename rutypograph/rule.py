import logging
import re
import sys
from typing import Dict, Union, Callable, Match
from typing import List
from typing import Tuple

from .environment import TypographEnvironment

logger = logging.getLogger(__name__)


def compile_pcre_pattern(pattern, additional_flags=0):
    """
    Compiles Perl Compatible Regular Expressions into python (parses /.../keys )
    :param additional_flags:
    :param pattern:
    :return:
    """
    try:
        if pattern[0] != '/':
            return re.compile(pattern, additional_flags)

        parts = pattern.split('/')
        modifiers = parts[-1]
        newpattern = pattern[1:-1 - len(modifiers)]
        flags_lut = {'i': re.I, 's': re.S, 'm': re.M, 'u': re.U}
        flags = re.U

        for i in modifiers:
            if i in flags_lut:
                flags |= flags_lut[i]

        flags |= additional_flags
        return re.compile(newpattern, flags)
    except Exception as e:
        raise type(e)(str(e) + "\nFailed pattern: %s, %s" % (pattern, newpattern)) \
            .with_traceback(sys.exc_info()[2])


class Rule: # pylint: disable=too-few-public-methods
    """
    Base class for a rule of text conversion
    """

    def __init__(self) -> None:
        self.rule_id = "N/A"
        self.disabled = False
        self.debug = False
        self.description = ""
        self.doctests = []  # type: List[Tuple[str, str]]

    def apply(self, text: str, environment: TypographEnvironment) -> str:
        """
        apply specific rule to text with environment
        :param text:
        :param environment:
        :return:
        """
        return text

    def __str__(self):
        return '[%s] %s' % (self.rule_id, self.description)

    def __repr__(self):
        return self.__str__()


class RuleRegex(Rule): # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self, patterns: Union[List[str], str],
                 replacements: List[Union[str, Callable[[Match[str], TypographEnvironment], str]]] = None,
                 pcre_keys=0, cycled=False) -> None:
        """
        Set of Regex rules of text transformation
        :param patterns: Search pattern
        :param replacements: Replace pattern
        :param pcre_keys: PCRE-compatible regex keys
        :param cycled: Run multiple passes until the string is unchanged
        """
        super().__init__()
        if not isinstance(patterns, list):
            patterns = [patterns]

        if not isinstance(replacements, list):
            replacements = [replacements]

        self.compiled_patterns = [compile_pcre_pattern(pattern, pcre_keys) for pattern in patterns]
        if len(replacements) == 1:
            self.replacements = replacements * len(patterns)
        elif len(replacements) == len(patterns):
            self.replacements = replacements
        else:
            raise ValueError("Number of patterns and replacements dont match!")

        self.cycled = cycled

    def apply(self, text: str, environment: TypographEnvironment) -> str:

        for pattern, replacement in zip(self.compiled_patterns, self.replacements):
            while True:
                text_dry = text
                if callable(replacement):
                    text_wet = pattern.sub(lambda match: replacement(match, environment), text_dry)  # pylint: disable=cell-var-from-loop
                else:
                    text_wet = pattern.sub(replacement, text_dry)

                logger.debug("pattern: %s || dry: %s || result: %s", pattern, text_dry , text_wet)

                text = text_wet

                if not self.cycled:
                    break

                if text_dry == text:
                    break


        return text


class RuleFunction(Rule): # pylint: disable=too-few-public-methods
    """
    Rule for pass text through function
    """

    def __init__(self, fn) -> None:
        super().__init__()
        self.fn = fn

    def apply(self, text: str, environment: TypographEnvironment) -> str:
        return self.fn(text, environment)


class RuleReplace(RuleRegex): # pylint: disable=too-few-public-methods
    """
    simple replace rule
    """

    def __init__(self, pattern, replacement, icase) -> None:
        """

        :param pattern: search pattern
        :param replacement: replacement pattern
        :param icase: ignore case
        """
        super().__init__(re.escape(pattern), replacement, re.IGNORECASE if icase else 0)


def _ruledef_to_rule(ruledef) -> Rule:
    fn = ruledef.get('function', None)
    if fn is not None:
        # @todo check signature
        return RuleFunction(fn)
    elif ruledef.get('simple_replace'):
        icase = ruledef.get('case_sensitive', False)
        return RuleReplace(ruledef['pattern'], ruledef['replacement'], icase)

    cycled = ruledef.get('cycled', False)
    return RuleRegex(ruledef['pattern'], ruledef['replacement'], cycled=cycled)


def _parse_ruledef(ruledef) -> Rule:
    """
    :param ruledef: dict, in a format comatible with mdash's own definitions
    :return: Rule
    """
    rule = _ruledef_to_rule(ruledef)
    if rule is not None:
        rule.rule_id = ruledef.get('rule_id', 'N/A')
        rule.disabled = ruledef.get('disabled', False)
        rule.description = ruledef.get('description', '-')
        rule.debug = ruledef.get('debug', False)
        rule.doctests = ruledef.get('doctests', [])
    return rule


def convert_ruledefs_to_rules(ruledefs: List[Dict]) -> List[Rule]:
    rules = [_parse_ruledef(ruledef) for ruledef in ruledefs]
    return rules
