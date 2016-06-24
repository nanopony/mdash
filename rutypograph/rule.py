import sys
import re
import base64
import types
import logging

from .text_processors import registered_functions

logger = logging.getLogger(__name__)

# description
# disabled
# pattern list
# cycled ???
# replacement ???

# function - в глобалс (?) в классе (?)

# simple_replace > case_sensitive
import re


def compile_pcre_pattern(pattern, additional_flags=0):
    """
    compiles pcre pattern
    :param self:
    :param pattern:
    :return:
    """
    if pattern[0] != '/':
        return re.compile(pattern, additional_flags)
    modifiers = pattern.split('/').pop()
    b = {'i': re.I, 's': re.S, 'm': re.M, 'u': re.U}
    flags = re.U
    xeval = False
    for i in modifiers:
        if i in b:
            flags |= b[i]
        if i == 'e':
            xeval = True

    flags = flags | additional_flags
    newpattern = pattern[1:-1 - len(modifiers)]
    # newpattern = newpattern.replace('\\' + es, es)
    return re.compile(newpattern, flags)


class Rule:
    def __init__(self):
        self.rule_id = "N/A"
        self.disabled = False
        self.debug = False
        self.description = ""
        pass

    def apply(self, text):
        return text

    def __str__(self):
        return '[%s] %s' % (self.rule_id, self.description)

    def __repr__(self):
        return self.__str__()


class RuleRegex(Rule):
    def __init__(self, pattern, replacement=None, keys=0, replace_сallback=None, cycle=False):
        super().__init__()
        self.compiled_pattern = compile_pcre_pattern(pattern, keys)
        self.replacement = replace_сallback if replace_сallback is not None else replacement
        self.cycle = cycle

    def apply(self, text):
        if self.debug:
            logger.debug('text: %s, pattern: %s' % (text, self.compiled_pattern))
        return self.compiled_pattern.sub(self.replacement, text)


class RuleMultipleRegex(Rule):
    def __init__(self, patterns, replacement=None, keys=0, replace_сallback=None, cycle=False):
        super().__init__()
        self.compiled_patterns = [compile_pcre_pattern(pattern, keys) for pattern in patterns]
        self.replacement = replacement or replace_сallback
        self.cycle = cycle
        self.one_callback = not isinstance(replacement, list)

    def apply(self, text):
        if self.one_callback:
            for pattern in self.compiled_patterns:
                text = pattern.sub(self.replacement, text)
        else:
            for q, pattern in enumerate(self.compiled_patterns):
                text = pattern.sub(self.replacement[q], text)

        return text


class RuleFunction(Rule):
    def __init__(self, fn):
        self.fn = fn
        pass

    def apply(self, text):
        return self.fn(text)


class RuleReplace(RuleRegex):
    def __init__(self, pattern, replacement, icase):
        super().__init__(re.escape(pattern), replacement, re.IGNORECASE if icase else 0)


functions = []


def _ruledef_to_rule(ruledef):
    if ruledef.get('function'):
        fn_name = ruledef.get('function')
        if fn_name in registered_functions:
            return RuleFunction(registered_functions[fn_name])
        logger.warning('Text function %s is not found' % fn_name)
        return Rule()

    if ruledef.get('simple_replace'):
        icase = ruledef.get('case_sensitive', False)
        return RuleReplace(ruledef['pattern'], ruledef['replacement'], icase)

    # preg_replace // preg_replace_callback
    сycle = ruledef.get('case_sensitive', False)
    cls = RuleMultipleRegex if isinstance(ruledef['pattern'], list) else RuleRegex
    if 'replace_callback' in ruledef:
        return cls(ruledef['pattern'], ruledef['replace_callback'], cycle=сycle)
    else:
        return cls(ruledef['pattern'], ruledef['replacement'], cycle=сycle)

    raise ValueError('Can\'t parse ruledef: %s' % ruledef)


def _parse_ruledef(ruledef):
    q = _ruledef_to_rule(ruledef)
    if q is not None:
        q.rule_id = ruledef.get('rule_id', 'N/A')
        q.disabled = ruledef.get('disabled', False)
        q.description = ruledef.get('description', '-')
        q.debug = ruledef.get('debug', False)
    return q


def convert_ruledefs_to_rules(ruledefs):
    s = [_parse_ruledef(ruledef) for ruledef in ruledefs]
    return s
