from typing import Dict
from typing import List


class ExtraStyles:
    """
    What to do with extra tag
    """
    OFF = 0  # no extra tags
    INLINE = 1  # inline style
    AS_CLASS = 2  # use css classes


class TypographEnvironment:
    """
    Sets which ruleset will be used, and passes options to individual rules
    """

    SUBSTITUTE_START = '\xDE\x00\x01'
    SUBSTITUTE_END = '\xDE\x00\x02'

    def __init__(self, rules: List['Rule'] = None) -> None:
        self.rules = rules
        # rule-specific-options
        self.extra_style = ExtraStyles.OFF  # type: int
        self.convert_html_entities_to_unicode = False  # type: int
        self.substitutes = {}  # type: Dict[str, str]
        self.substitute_counter = 0

    def begin(self):
        self.substitutes.clear()
        self.substitute_counter = 0

    def apply_substitutes(self, text):
        for marker, value in self.substitutes.items():
            text = text.replace(marker, value)
        return text

    def provide_substitute(self, sub):
        """
        return tag that won't be edited by any rule, to replace with original at the final stage
        :param sub:
        :return:
        """
        marker = "%s%s%s" % (self.SUBSTITUTE_START, self.substitute_counter, self.SUBSTITUTE_END)
        self.substitutes[marker] = sub
        self.substitute_counter += 1
        return marker
