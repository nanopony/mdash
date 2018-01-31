"""
    Helpers that are used in rules
"""
import html
import ipaddress
import logging

from .consts import QUOTE_CRAWSE_CLOSE, QUOTE_FIRS_CLOSE, QUOTE_CRAWSE_OPEN, RE_QO, QUOTE_FIRS_OPEN
from .environment import TypographEnvironment, ExtraStyles

logger = logging.getLogger(__name__)


def make_tag(content, tag_name, environment: TypographEnvironment, class_name=None) -> str:
    if environment.extra_style == ExtraStyles.OFF:
        return content
    if class_name is None:
        class_or_style = ""
    else:
        if environment.extra_style == ExtraStyles.INLINE and class_name in CSS_CLASSES:
            class_or_style = " style=\"%s\"" % CSS_CLASSES[class_name]
        else:
            class_or_style = " class=\"%s\"" % class_name

    return environment.provide_substitute(
        "<%s%s>" % (tag_name, class_or_style)) + content + environment.provide_substitute("</%s>" % (tag_name))


def wrap_in_nowrap(text, environment: TypographEnvironment):
    """
    Оборачивает в типографский NOWRAP
    :param text:
    :return:
    """
    return make_tag(text, 'span', environment, 'nowrap')


def wrap_in_typo_sub(text, environment: TypographEnvironment):
    """
    Оборачивает в типографский SUB
    :param text:
    :return:
    """
    return make_tag(make_tag(text, 'small', environment), 'sub', environment)


def wrap_in_typo_sup(text, environment: TypographEnvironment):
    """
    Оборачивает в типографский SUP
    :param css_class:
    :param text:
    :return:
    """
    return make_tag(make_tag(text, 'small', environment), 'sup', environment)


def util_split_number(num, environment: TypographEnvironment):
    """
    Разбивает номер на блоки по 3 цифры с &thinsp; между ними
    :param num:
    :return:
    """
    repl = ""
    for i in range(len(num), -1, -3):
        if i - 3 >= 0:
            repl = ("&thinsp;" if i > 3 else "") + num[i - 3:i] + repl
        else:
            repl = num[0:i] + repl
    return repl


def utils_nowrap_ip_address(input_string, environment: TypographEnvironment):
    """
    Оборачивает ip в nowrap, если это IPv4
    :param input_string:
    :param input_string:
    :return:
    """
    try:
        tmp = ipaddress.ip_address(input_string)
        return wrap_in_nowrap(input_string, environment)
    except ValueError:
        return input_string


CSS_CLASSES = {
    "nowrap"          : "word-spacing:nowrap;",
    "oa_obracket_sp_s": "margin-right:0.3em;",
    "oa_obracket_sp_b": "margin-left:-0.3em;",
    "oa_obracket_nl_b": "margin-left:-0.3em;",
    "oa_comma_b"      : "margin-right:-0.2em;",
    "oa_comma_e"      : "margin-left:0.2em;",
    "oa_oquote_nl"    : "margin-left:-0.44em;",
    "oa_oqoute_sp_s"  : "margin-right:0.44em;",
    "oa_oqoute_sp_q"  : "margin-left:-0.44em;"
}


def _build_sub_quotations(text):
    ptr = 0
    quote_stack = []
    depth = 0
    parts = []

    while ptr < len(text):
        match = RE_QO.search(text, ptr)
        if match is None:
            break
        start_position = match.start()
        parts.append(text[ptr:start_position])

        is_closing = text[start_position + 1] == 'r'
        if is_closing:
            depth -= 1
            parts.append(QUOTE_FIRS_CLOSE if depth == 0 else QUOTE_CRAWSE_CLOSE)
        else:
            parts.append(QUOTE_FIRS_OPEN if depth == 0 else QUOTE_CRAWSE_OPEN)
            depth += 1
            quote_stack.append(start_position)
        logger.info('match: %s, depth: %s, parts: %s', match, depth, parts)
        if depth < 0:  # broken, broken, broken
            logger.warning('Broken quotes')
            return text

        ptr = match.end()

    if depth > 0:  # broken, broken, broken
        logger.warning('Broken quotes')
        return text

    if ptr < len(text):
        parts.append(text[ptr:])

    if len(parts) > 0:
        return "".join(parts)
    else:
        return text


def util_oaquote_extra(text: str, environment):
    """
    Оптическое выравнивание кавычки
    :param text:
    :param environment:
    :return:
    """
    # @todo
    return text


def util_to_unicode(text: str, environment):
    if environment.convert_html_entities_to_unicode:
        return html.unescape(text)


def build_sub_quotations(text: str, environment):
    """
    Заменяет внутренние кавычки-елочки на лапки
    :param text:
    :param text:
    :return:
    >>> build_sub_quotations("Она добавила: &laquo;И&nbsp;цвет мой самый любимый&nbsp;&mdash; &laquo;эсмеральда&raquo;&raquo;.")
    Она добавила: &laquo;И&nbsp;цвет мой самый любимый&nbsp;&mdash; &bdquo;эсмеральда&ldquo;&raquo;.
    """

    # Разбиваем по абзацам, иначе кавычка пропущенная в одном тексте сведет с ума процессор

    split_code = "\r\n\r\n" if text.find(
        "\r\n") >= 0 else "\n\n"

    chunks = [_build_sub_quotations(chunk) for chunk in text.split(split_code)]
    return split_code.join(chunks)
