import re

QUOTE_FIRS_OPEN = '&laquo;'
QUOTE_FIRS_CLOSE = '&raquo;'
QUOTE_CRAWSE_OPEN = '&bdquo;'
QUOTE_CRAWSE_CLOSE = '&ldquo;'
RE_QO = re.compile('&(l|r)aquo;')

DOMAINS = [
    "ru",
    "ру",
    "ком",
    "орг",
    "уа",
    "ua",
    "uk",
    "co",
    "fr",
    "com",
    "net",
    "edu",
    "gov",
    "org",
    "mil",
    "int",
    "info",
    "biz",
    "info",
    "name",
    "pro"
]
