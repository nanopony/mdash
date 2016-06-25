import re
from lxml import html
from lxml.html import clean
import logging

from .rule import convert_ruledefs_to_rules, Rule
from .ruledefs import ALL_RULES

logger = logging.getLogger(__name__)


class Typograph:
    PRESET_NORULES = 0
    PRESET_DEFAULT = 1
    PRESET_ALLRULES = 42
    VERBATIM = '\xBE\xEF'
    AUTOLINK_REGEX = re.compile(r"""(?i)\b(?P<body>(?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|(?P<host>[a-z0-9.\-]+[.][a-z]{2,4}/))(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")


    def __init__(self, preset=None):
        if preset is None:
            preset = self.PRESET_DEFAULT
        logger.info('Loading preset %s' % preset)
        self.rules = self.populate_rules(preset)
        logger.info('%s rules loaded' % len(self.rules))

    def populate_rules(self, preset):
        if preset == self.PRESET_NORULES:
            return []
        s = []
        for ruledef in ALL_RULES:
            s += convert_ruledefs_to_rules(ruledef)
        return s

    def process_html(self, text, encoding='utf-8', autolink = True):
        s = html.fromstring(text)
        self._process_node(s)
        if autolink:
            clean.autolink(s, [self.AUTOLINK_REGEX], avoid_hosts=[])
        s = html.tostring(s, encoding=encoding).decode(encoding)

        return s.replace(self.VERBATIM, '&')

    def _process_node(self, node):
        if node.tail is not None and node.tail != '\n':
            print(node.tail)
            node.tail = self.process(node.tail, html_verbatim=True)

        if node.tag in ['p']:
            content = node.text_content()
            for c in node.getchildren():
                node.remove(c)
            if content is not None:
                node.text = self.process(content, html_verbatim=True)
        elif node.tag in ['div', 'span'] and node.text is not None:
            node.text = self.process(node.text, html_verbatim=True)


        for s in node.getchildren():
            self._process_node(s)

    def process(self, text, html_verbatim=False):
        for rule in self.rules:
            logger.info('Applying %s' % rule)
            assert isinstance(rule, Rule)
            if rule.disabled:
                continue
            text = rule.apply(text)

            # logger.info('After processing ' + text)
        if html_verbatim:
            return text.replace('&', self.VERBATIM)
        return text
