import logging
import re

from lxml import html
from lxml.html import clean

from rutypograph.rulesets import get_default_environment
from .rule import Rule
from .environment import TypographEnvironment

logger = logging.getLogger(__name__)


class Typograph:
    VERBATIM = '\xBE\xEF'
    AUTOLINK_REGEX = re.compile(
        r"""(?i)\b(?P<body>(?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|(?P<host>[a-z0-9.\-]+[.][a-z]{2,4}/))(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")

    @classmethod
    def process_html(cls, text: str, environment: TypographEnvironment = None, encoding: str = 'utf-8',
                     autolink: bool = True) -> str:
        """
        :param text: html text
        :param environment: TypographSettings
        :param encoding: text endocing
        :param autolink: convert all in-text url adress into links
        :return:
        """

        if environment is None:
            environment = get_default_environment()

        node = html.fromstring(text)
        cls._process_node(node, environment)
        if autolink:
            clean.autolink(node, [cls.AUTOLINK_REGEX], avoid_hosts=[])
        text_processed = html.tostring(node, encoding=encoding).decode(encoding)

        return text_processed.replace(cls.VERBATIM, '&')

    @classmethod
    def _process_node(cls, node, environment: TypographEnvironment):
        if node.tail is not None and node.tail != '\n':
            node.tail = cls.process(node.tail, mangle_ampresand=True)

        if node.tag in ['p']:
            content = node.text_content()
            for child in node.getchildren():
                node.remove(child)
            if content is not None:
                node.text = cls.process(content, environment, mangle_ampresand=True)
        elif node.tag in ['div', 'span'] and node.text is not None:
            node.text = cls.process(node.text, environment, mangle_ampresand=True)

        for child in node.getchildren():
            cls._process_node(child, environment)

    @classmethod
    def process(cls, text: str, environment: TypographEnvironment = None, mangle_ampresand: bool = False) -> str:
        """
        Processes text with desired environment
        :param text:
        :param environment:
        :param mangle_ampresand: generally, don't use this argument; if true, mangle & in inner html text so it could be
        used to reassemble tidy html
        :return:
        """
        if environment is None:
            environment = get_default_environment()

        environment.begin()

        for rule in environment.rules:
            assert isinstance(rule, Rule)
            if rule.disabled:
                continue
            text_wet = rule.apply(text, environment)
            if text_wet != text:
                logger.debug("Rule: %s\nDry: %s\nWet: %s", rule, text, text_wet)
            text = text_wet

        if mangle_ampresand:
            return text.replace('&', cls.VERBATIM)

        text = environment.apply_substitutes(text)
        return text
