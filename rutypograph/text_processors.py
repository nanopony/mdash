import logging
import re

logger = logging.getLogger(__name__)

QUOTE_FIRS_OPEN = '&laquo;'
QUOTE_FIRS_CLOSE = '&raquo;'
QUOTE_CRAWSE_OPEN = '&bdquo;'
QUOTE_CRAWSE_CLOSE = '&ldquo;'
RE_QO = re.compile('&(l|r)aquo;')


def _build_sub_quotations(text):
    ptr = 0
    quote_stack = []
    depth = 0
    parts = []

    while (ptr < len(text)):
        m = RE_QO.search(text, ptr)
        if m is None:
            break
        st = m.start()
        parts.append(text[ptr:st])

        is_closing = text[st + 1] == 'r'
        if is_closing:
            depth -= 1
            parts.append(QUOTE_FIRS_CLOSE if depth == 0 else QUOTE_CRAWSE_CLOSE)
        else:
            parts.append(QUOTE_FIRS_OPEN if depth == 0 else QUOTE_CRAWSE_OPEN)
            depth += 1
            quote_stack.append(st)
        logger.info('m: %s, depth: %s' % (m.start(), depth))
        if depth < 0:  # broken, broken, broken
            logger.warning('Broken quotes')
            return text

        ptr = m.end()

    if depth > 0:  # broken, broken, broken
        logger.warning('Broken quotes')
        return text
    if len(parts) > 0:
        return "".join(parts)
    else:
        return text


def build_sub_quotations(text):
    """
    Заменяет внутренние кавычки-елочки на лапки
    :param self:
    :return:
    >>> build_sub_quotations("Она добавила: &laquo;И&nbsp;цвет мой самый любимый&nbsp;&mdash; &laquo;эсмеральда&raquo;&raquo;.")
    Она добавила: &laquo;И&nbsp;цвет мой самый любимый&nbsp;&mdash; &bdquo;эсмеральда&ldquo;&raquo;.
    """

    split_code = "\r\n\r\n" if text.find(
            "\r\n") >= 0 else "\n\n"  # Разбиваем по абзацам, иначе кавычка пропущенная в одном тексте сведет с ума процессор

    chunks = [_build_sub_quotations(chunk) for chunk in text.split(split_code)]
    return split_code.join(chunks)


registered_functions = {
    'build_sub_quotations': build_sub_quotations
}


def exec_function(function_name, text):
    if registered_functions in function_name:
        return registered_functions[function_name](text)
    logger.warning('Text function %s is not found' % function_name)
    return text


if __name__ == '__main__':
    print(build_sub_quotations(
            "Она добавила: &laquo;И&nbsp;цвет мой самый любимый&nbsp;&mdash; &laquo;эсмеральда&raquo;&raquo;."
            "&laquo;&raquo; &laquo; &laquo;&raquo; &laquo;&raquo; &raquo;."))
