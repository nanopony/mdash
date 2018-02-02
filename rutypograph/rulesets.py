# pragma pylint: disable=line-too-long
# pragma pylint: disable=bad-continuation
import re

from .consts import QUOTE_FIRS_OPEN, QUOTE_FIRS_CLOSE, DOMAINS
from .environment import TypographEnvironment
from .rule import convert_ruledefs_to_rules
from .rule_utilities import util_split_number, wrap_in_nowrap, wrap_in_typo_sup, utils_nowrap_ip_address, \
    wrap_in_typo_sub, build_sub_quotations, make_tag, util_oaquote_extra, util_to_unicode

BASIC_CLEANUP = convert_ruledefs_to_rules([
    {
        "rule_id"    : "space_tabs_norm",
        "description": "Удаление лишних пробельных символов и табуляций",
        "pattern"    : "\s+",
        "replacement": " ",
        "doctests"   : [("А  в этом тексте  у меня    залип пробел.", "А в этом тексте у меня залип пробел.")]
    },
    {
        "rule_id"    : "repeated_words",
        "description": "Удаление повторяющихся слов",
        "pattern"    : r"/\b([^\W\d_\s]+)\s+\1\b/i",
        "replacement": r"\1",
        "doctests"   : [("При при проверке текста обнаружились обнаружились повторяющиеся слова слова. Слова убраны. Цифры (3 3 4 4 5 5 5) не поломаны.",
                         "При проверке текста обнаружились повторяющиеся слова. Слова убраны. Цифры (3 3 4 4 5 5 5) не поломаны.")]
    },
    {
        "rule_id"    : "punkt_space",
        "description": "Правка плохих запятых с проблеом",
        "pattern"    :
            [
                "\s*(,|\.|!|\?)",
            ],

        "replacement":
            [
                r"\1",
            ],
        "doctests"   : [("Тест , он такой !", "Тест, он такой!")]
    },
])

RULEDEF_QUOTES = convert_ruledefs_to_rules([
    {
        "rule_id"    : "quot_normalization",
        "description": "Нормализация кавычки",
        "pattern"    : "/&quot;/s",
        "replacement": "\""
    },
    {
        "rule_id"    : "quotes_outside_a",
        "description": "Кавычки вне тэга <a>",
        "pattern"    : "/(\\<%%\\_\\_[^\\>]+\\>)\\\"(.+?)\\\"(\\<\\/%%\\_\\_[^\\>]+\\>)/s",
        "replacement": "\"\\1\\2\\3\""
    },
    {
        "rule_id"    : "open_quote",
        "description": "Открывающая кавычка",
        "pattern"    : "/(^|\\(|\\s|\\>|-)((\\\"|\\\\\")+)(\\S+)/iue",
        "replacement": lambda m, s: m.group(1) + QUOTE_FIRS_OPEN * (m.group(2).count("\"")) + m.group(4)
    },
    {
        "rule_id"    : "close_quote",
        "description": "Закрывающая кавычка",
        "pattern"    : "/([a-zа-яё0-9]|\\.|\\&hellip\\;|\\!|\\?|\\>|\\)|\\:|\\+|\\%|\\@|\\#|\\$|\\*)((\\\"|\\\\\")+)(\\.|\\&hellip\\;|\\;|\\:|\\?|\\!|\\,|\\s|\\)|\\<\\/|\\<|$)/uie",
        "replacement": lambda m, s: m.group(1) + QUOTE_FIRS_CLOSE * (m.group(2).count("\"")) + m.group(4)
    },
    {
        "rule_id"    : "close_quote_adv",
        "description": "Закрывающая кавычка особые случаи",
        "pattern"    : [
            "/([a-zа-яё0-9]|\\.|\\&hellip\\;|\\!|\\?|\\>|\\)|\\:|\\+|\\%|\\@|\\#|\\$|\\*)((\\\"|\\\\\"|\\&laquo\\;)+)(\\<[^\\>]+\\>)(\\.|\\&hellip\\;|\\;|\\:|\\?|\\!|\\,|\\)|\\<\\/|$| )/uie",
            "/([a-zа-яё0-9]|\\.|\\&hellip\\;|\\!|\\?|\\>|\\)|\\:|\\+|\\%|\\@|\\#|\\$|\\*)(\\s+)((\\\"|\\\\\")+)(\\s+)(\\.|\\&hellip\\;|\\;|\\:|\\?|\\!|\\,|\\)|\\<\\/|$| )/uie",
            "/\\>(\\&laquo\\;)\\.($|\\s|\\<)/ui",
            "/\\>(\\&laquo\\;),($|\\s|\\<|\\S)/ui",
            "/\\>(\\&laquo\\;):($|\\s|\\<|\\S)/ui",
            "/\\>(\\&laquo\\;);($|\\s|\\<|\\S)/ui",
            "/\\>(\\&laquo\\;)\\)($|\\s|\\<|\\S)/ui",
            "/((\\\"|\\\\\")+)$/uie"
        ],
        "replacement": [
            lambda m, s: m.group(1) + QUOTE_FIRS_CLOSE * (
                m.group(2).count("\"") + m.group(2).count("&laquo;")) + m.group(4) + m.group(5),
            lambda m, s: m.group(1) + m.group(2) + QUOTE_FIRS_CLOSE * (
                m.group(3).count("\"") + m.group(3).count("&laquo;")) + m.group(5) + m.group(6),
            ">&raquo;.\\2",
            ">&raquo;,\\2",
            ">&raquo;:\\2",
            ">&raquo;;\\2",
            ">&raquo;)\\2",
            lambda m, s: QUOTE_FIRS_CLOSE * (m.group(1).count("\""))
        ]
    },
    {
        "rule_id"    : "open_quote_adv",
        "description": "Открывающая кавычка особые случаи",
        "pattern"    : "/(^|\\(|\\s|\\>)(\\\"|\\\\\")(\\s)(\\S+)/iue",
        "replacement": lambda m, s: m.group(1) + QUOTE_FIRS_OPEN + m.group(4)
    },
    {
        "rule_id"    : "close_quote_adv_2",
        "description": "Закрывающая кавычка последний шанс",
        "pattern"    : "/(\\S)((\\\"|\\\\\")+)(\\.|\\&hellip\\;|\\;|\\:|\\?|\\!|\\,|\\s|\\)|\\<\\/|\\<|$)/uie",
        "replacement": lambda m, s: m.group(1) + QUOTE_FIRS_CLOSE * (m.group(2).count("\"")) + m.group(4)
    },
    {
        "rule_id"    : "quotation",
        "description": "Внутренние кавычки-лапки и дюймы",
        "function"   : build_sub_quotations
    }
])

RULEDEF_ETC = convert_ruledefs_to_rules([
    {
        "rule_id"    : "acute_accent",
        "description": "Акцент",
        "pattern"    : "/(у|е|ы|а|о|э|я|и|ю|ё)\\`(\\w)/i",
        "replacement": "\\1&#769;\\2"
    },
    {
        "rule_id"    : "word_sup",
        "description": "Надстрочный текст после символа ^",
        "pattern"    : "/((\\s|\\&nbsp\\;|^)+)\\^([a-zа-яё0-9\\.\\:\\,\\-]+)(\\s|\\&nbsp\\;|$|\\.$)/ieu",
        "replacement": lambda m, s: "" + wrap_in_typo_sup(m.group(3), s) + m.group(4)
    },
    {
        "rule_id"    : "century_period",
        "description": "Тире между диапозоном веков",
        "pattern"    : "/(\\040|\\t|\\&nbsp\\;|^)([XIV]{1,5})(-|\\&mdash\\;)([XIV]{1,5})(( |\\&nbsp\\;)?(в\\.в\\.|вв\\.|вв|в\\.|в))/eu",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + "&mdash;" + m.group(4) + " вв.", s)
    },
    {
        "rule_id"    : "time_interval",
        "description": "Тире и отмена переноса между диапозоном времени",
        "pattern"    : "/([^\\d\\>]|^)([\\d]{1,2}\\:[\\d]{2})(-|\\&mdash\\;|\\&minus\\;)([\\d]{1,2}\\:[\\d]{2})([^\\d\\<]|$)/eui",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + "&mdash;" + m.group(4), s) + m.group(5)
    },
    {
        "rule_id"    : "split_number_to_triads",
        "description": "Разбиение числа на триады",
        "pattern"    : "/([^a-zA-Z0-9<\\)]|^)([0-9]{5,})([^a-zA-Z>\\(]|$)/eu",
        "replacement": lambda m, s: m.group(1) + util_split_number(m.group(2).replace(" ", "&thinsp;"), s) + m.group(3)
    },

    {
        "rule_id"    : "to_unicode",
        "description": "Заменить HTML спецсимволы на юникод",
        "function"   : util_to_unicode
    },
    # {
    #     "rule_id": "expand_no_nbsp_in_nobr",
    #     "description": "Удаление nbsp в nobr/nowrap тэгах",
    #     "function": "remove_nbsp"
    # },
    # {
    #     "rule_id": "nobr_to_nbsp",
    #     "description": "Преобразование nobr в nbsp",
    #     "disabled": True,
    #     "function": "nobr_to_nbsp"
    # }
])

RULEDEF_OPTS = convert_ruledefs_to_rules([
    {
        "rule_id"    : "oa_oquote",
        "description": "Оптическое выравнивание открывающей кавычки",
        "pattern"    : [
            "/([a-zа-яё\\-]{3,})(\\040|\\&nbsp\\;|\\t)(\\&laquo\\;)/uie",
            "/(\\n|\\r|^)(\\&laquo\\;)/ei"
        ],
        "replacement": [
            lambda m, s: m.group(1) + make_tag(m.group(2), "span", s, "oa_oqoute_sp_s") + make_tag(m.group(3),
                                                                                                   "span", s,
                                                                                                   "oa_oqoute_sp_q"),
            lambda m, s: m.group(1) + make_tag(m.group(2), "span", s, "oa_oquote_nl")
        ]
    },
    {
        "rule_id"    : "oa_oquote_extra",
        "description": "Оптическое выравнивание кавычки",
        "function"   : util_oaquote_extra
    },
    {
        "rule_id"    : "oa_obracket_coma",
        "description": "Оптическое выравнивание для пунктуации (скобка)",
        "pattern"    : [
            "/(\\040|\\&nbsp\\;|\\t)\\(/ei",
            "/(\\n|\\r|^)\\(/ei"
        ],
        "replacement": [
            lambda m, s: make_tag(m.group(1), "span", s, 'oa_obracket_sp_s') + make_tag("(", "span", s,
                                                                                        'oa_obracket_sp_b'),
            lambda m, s: m.group(1) + make_tag("(", "span", s, 'oa_obracket_nl_b')
        ]
    }
])

RULEDEF_DATES = convert_ruledefs_to_rules([
    {
        "rule_id"    : "years",
        "description": "Установка тире и пробельных символов в периодах дат",
        "pattern"    : "/(с|по|период|середины|начала|начало|конца|конец|половины|в|между|\\([cс]\\)|\\&copy\\;)(\\s+|\\&nbsp\\;)([\\d]{4})(-|\\&mdash\\;|\\&minus\\;)([\\d]{4})(( |\\&nbsp\\;)?(г\\.г\\.|гг\\.|гг|г\\.|г)([^а-яёa-z]))?/eui",
        "replacement": lambda m, s: m.group(1) + m.group(2) + ((m.group(3) + m.group(4) + m.group(5) if int(
            m.group(3)) >= int(m.group(5)) else  m.group(3) + "&mdash;" + m.group(5))) + (
                                        ("&nbsp;гг." if (m.group(6)) else "")) + (m.group(9) if (m.group(9)) else "")
    },
    {
        "rule_id"    : "mdash_month_interval",
        "description": "Расстановка тире и объединение в неразрывные периоды месяцев",
        "disabled"   : True,
        "pattern"    : "/((январ|феврал|сентябр|октябр|ноябр|декабр)([ьяюе]|[её]м)|(апрел|июн|июл)([ьяюе]|ем)|(март|август)([ауе]|ом)?|ма[йяюе]|маем)\\-((январ|феврал|сентябр|октябр|ноябр|декабр)([ьяюе]|[её]м)|(апрел|июн|июл)([ьяюе]|ем)|(март|август)([ауе]|ом)?|ма[йяюе]|маем)/iu",
        "replacement": "\\1&mdash;\\8"
    },
    {
        "rule_id"    : "nbsp_and_dash_month_interval",
        "description": "Расстановка тире и объединение в неразрывные периоды дней",
        "disabled"   : True,
        "pattern"    : "/([^\\>]|^)(\\d+)(\\-|\\&minus\\;|\\&mdash\\;)(\\d+)( |\\&nbsp\\;)(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)([^\\<]|$)/ieu",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(
            m.group(2) + "&mdash;" + m.group(4) + " " + m.group(6), s) + m.group(7)
    },
    {
        "rule_id"    : "nobr_year_in_date",
        "description": "Привязка года к дате",
        "pattern"    : [
            "/(\\s|\\&nbsp\\;)([0-9]{2}\\.[0-9]{2}\\.([0-9]{2})?[0-9]{2})(\\s|\\&nbsp\\;)?г(\\.|\\s|\\&nbsp\\;)/eiu",
            "/(\\s|\\&nbsp\\;)([0-9]{2}\\.[0-9]{2}\\.([0-9]{2})?[0-9]{2})(\\s|\\&nbsp\\;|\\.(\\s|\\&nbsp\\;|$)|$)/eiu"
        ],
        "replacement": [
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + " г.", s) + (
                ("" if m.group(5) == "." else " ")),
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2), s) + m.group(4)
        ]
    },
    {
        "rule_id"    : "space_posle_goda",
        "description": "Пробел после года",
        "pattern"    : "/(^|\\040|\\&nbsp\\;)([0-9]{3,4})(год([ауе]|ом)?)([^a-zа-яё]|$)/ui",
        "replacement": "\\1\\2 \\3\\5"
    },
    {
        "rule_id"    : "nbsp_posle_goda_abbr",
        "description": "Пробел после года",
        "pattern"    : "/(^|\\040|\\&nbsp\\;|\\\"|\\&laquo\\;)([0-9]{3,4})[ ]?(г\\.)([^a-zа-яё]|$)/ui",
        "replacement": "\\1\\2&nbsp;\\3\\4"
    }
])

RULEDEF_NOBR = convert_ruledefs_to_rules([
    {
        "rule_id"    : "super_nbsp",
        "description": "Привязка союзов и предлогов к написанным после словам",
        "pattern"    : "/(\\s|^|\\&(la|bd)quo\\;|\\>|\\(|\\&mdash\\;\\&nbsp\\;)([a-zа-яё]{1,2}\\s+)([a-zа-яё]{1,2}\\s+)?([a-zа-яё0-9\\-]{2,}|[0-9])/ieu",
        "replacement": lambda m, s: m.group(1) + m.group(3).strip() + "&nbsp;" + (
            (m.group(4).strip() + "&nbsp;" if m.group(4)  else  "")) + m.group(5)
    },
    {
        "rule_id"    : "nbsp_in_the_end",
        "description": "Привязка союзов и предлогов к предыдущим словам в случае конца предложения",
        "pattern"    : "/([a-zа-яё0-9\\-]{3,}) ([a-zа-яё]{1,2})\\.( [A-ZА-ЯЁ]|$)/u",
        "replacement": "\\1&nbsp;\\2.\\3"
    },
    {
        "rule_id"    : "phone_builder",
        "description": "Объединение в неразрывные конструкции номеров телефонов",
        "pattern"    : [
            "/([^\\d\\+]|^)([\\+]?[0-9]{1,3})( |\\&nbsp\\;|\\&thinsp\\;)([0-9]{3,4}|\\([0-9]{3,4}\\))( |\\&nbsp\\;|\\&thinsp\\;)([0-9]{2,3})(-|\\&minus\\;)([0-9]{2})(-|\\&minus\\;)([0-9]{2})([^\\d]|$)/e",
            "/([^\\d\\+]|^)([\\+]?[0-9]{1,3})( |\\&nbsp\\;|\\&thinsp\\;)([0-9]{3,4}|[0-9]{3,4})( |\\&nbsp\\;|\\&thinsp\\;)([0-9]{2,3})(-|\\&minus\\;)([0-9]{2})(-|\\&minus\\;)([0-9]{2})([^\\d]|$)/e"
        ],
        "replacement": [
            lambda m, s: m.group(1) + (
                (m.group(2) + " " + m.group(4) + " " + m.group(6) + "-" + m.group(8) + "-" + m.group(
                    10) if (m.group(1) == ">" or m.group(11) == "<")  else wrap_in_nowrap(
                    m.group(2) + " " + m.group(4) + " " + m.group(6) + "-" + m.group(8) + "-" + m.group(
                        10), s))) + m.group(11),
            lambda m, s: m.group(1) + (
                (m.group(2) + " " + m.group(4) + " " + m.group(6) + "-" + m.group(8) + "-" + m.group(
                    10) if (m.group(1) == ">" or m.group(11) == "<")  else wrap_in_nowrap(
                    m.group(2) + " " + m.group(4) + " " + m.group(6) + "-" + m.group(8) + "-" + m.group(
                        10), s))) + m.group(11)
        ]
    },
    {
        "rule_id"    : "phone_builder_v2",
        "description": "Дополнительный формат номеров телефонов",
        "pattern"    : "/([^\\d]|^)\\+\\s?([0-9]{1})\\s?\\(([0-9]{3,4})\\)\\s?(\\d{3})(\\d{2})(\\d{2})([^\\d]|$)/ie",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(
            "+" + m.group(2) + " " + m.group(3) + " " + m.group(4) + "-" + m.group(5) + "-" + m.group(6), s) + m.group(
            7)
    },
    {
        "rule_id"    : "ip_address",
        "description": "Объединение IP-адресов",
        "pattern"    : "/(\\s|\\&nbsp\\;|^)(\\d{0,3}\\.\\d{0,3}\\.\\d{0,3}\\.\\d{0,3})/ie",
        "replacement": lambda m, s: m.group(1) + utils_nowrap_ip_address(m.group(2), s)
    },
    {
        "rule_id"    : "dots_for_surname_abbr",
        "disabled"   : True,
        "description": "Простановка точек к инициалам у фамилии",
        "pattern"    : [
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ])\\.?(\\s|\\&nbsp\\;)?([А-ЯЁ])(\\s|\\&nbsp\\;)([А-ЯЁ][а-яё]+)(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue",
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ][а-яё]+)(\\s|\\&nbsp\\;)([А-ЯЁ])\\.?(\\s|\\&nbsp\\;)?([А-ЯЁ])\\.?(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue"
        ],
        "replacement": [
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + ". " + m.group(4) + ". " + m.group(6), s) + m.group(
                7),
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + " " + m.group(4) + ". " + m.group(6) + ".",
                                                     s) + m.group(
                7)
        ]
    },
    {
        "rule_id"    : "spaces_nobr_in_surname_abbr",
        "description": "Привязка инициалов к фамилиям",
        "pattern"    : [
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ])\\.(\\s|\\&nbsp\\;)?([А-ЯЁ])\\.(\\s|\\&nbsp\\;)?([А-ЯЁ][а-яё]+)(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue",
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ][а-яё]+)(\\s|\\&nbsp\\;)([А-ЯЁ])\\.(\\s|\\&nbsp\\;)?([А-ЯЁ])\\.(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue",
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ])(\\s|\\&nbsp\\;)?([А-ЯЁ])(\\s|\\&nbsp\\;)([А-ЯЁ][а-яё]+)(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue",
            "/(\\s|^|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)([А-ЯЁ][а-яё]+)(\\s|\\&nbsp\\;)([А-ЯЁ])(\\s|\\&nbsp\\;)?([А-ЯЁ])(\\s|$|\\.|\\,|\\;|\\:|\\?|\\!|\\&nbsp\\;)/ue"
        ],
        "replacement": [
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + ". " + m.group(4) + ". " + m.group(6), s) + m.group(
                7),
            lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + " " + m.group(4) + ". " + m.group(6) + ".",
                                                     s) + m.group(
                7),
            lambda m, s: m.group(1) + wrap_in_nowrap(
                m.group(2) + (" " if (m.group(3)) else  "") + m.group(4) + (
                    (" " if (m.group(5)) else  "")) + m.group(6), s) + m.group(7),
            lambda m, s: m.group(1) + wrap_in_nowrap(
                m.group(2) + " " + m.group(4) + (" " if (m.group(5)) else  "") + m.group(6), s) + m.group(7)
        ]
    },
    {
        "rule_id"    : "nbsp_before_particle",
        "description": "Неразрывный пробел перед частицей",
        "pattern"    : "/(\\040|\\t)+(ли|бы|б|же|ж)(\\&nbsp\\;|\\.|\\,|\\:|\\;|\\&hellip\\;|\\?|\\s)/iue",
        "replacement": lambda m, s: "&nbsp;" + m.group(2) + (" " if m.group(3) == "&nbsp;"  else  m.group(3))
    },
    {
        "rule_id"    : "nbsp_v_kak_to",
        "description": "Неразрывный пробел в как то",
        "pattern"    : "/как то\\:/ui",
        "replacement": "как&nbsp;то:"
    },
    {
        "rule_id"    : "nbsp_celcius",
        "description": "Привязка градусов к числу",
        "pattern"    : "/(\\s|^|\\>|\\&nbsp\\;)(\\d+)( |\\&nbsp\\;)?(°|\\&deg\\;)(C|С)(\\s|\\.|\\!|\\?|\\,|$|\\&nbsp\\;|\\;)/iu",
        "replacement": "\\1\\2&nbsp;\\4C\\6"
    },
    {
        "rule_id"    : "hyphen_nowrap_in_small_words",
        "description": "Обрамление пятисимвольных слов разделенных дефисом в неразрывные блоки",
        "disabled"   : True,
        "cycled"     : True,
        "pattern"    : "/(\\&nbsp\\;|\\s|\\>|^)([a-zа-яё]{1}\\-[a-zа-яё]{4}|[a-zа-яё]{2}\\-[a-zа-яё]{3}|[a-zа-яё]{3}\\-[a-zа-яё]{2}|[a-zа-яё]{4}\\-[a-zа-яё]{1}|когда\\-то|кое\\-как|кой\\-кого|вс[её]\\-таки|[а-яё]+\\-(кась|ка|де))(\\s|\\.|\\,|\\!|\\?|\\&nbsp\\;|\\&hellip\\;|$)/uie",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2), s) + m.group(4)
    },
    {
        "rule_id"    : "hyphen_nowrap",
        "description": "Отмена переноса слова с дефисом",
        "disabled"   : True,
        "cycled"     : True,
        "pattern"    : "/(\\&nbsp\\;|\\s|\\>|^)([a-zа-яё]+)((\\-([a-zа-яё]+)){1,2})(\\s|\\.|\\,|\\!|\\?|\\&nbsp\\;|\\&hellip\\;|$)/uie",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + m.group(3), s) + m.group(6)
    }
])

RULEDEF_ABBR = convert_ruledefs_to_rules([
    {
        "rule_id"    : "nobr_abbreviation",
        "description": "Расстановка пробелов перед сокращениями dpi, lpi",
        "pattern"    : "/(\\s+|^|\\>)(\\d+)(\\040|\\t)*(dpi|lpi)([\\s\\;\\.\\?\\!\\:\\(]|$)/i",
        "replacement": "\\1\\2&nbsp;\\4\\5"
    },
    {
        "rule_id"    : "nobr_acronym",
        "description": "Расстановка пробелов перед сокращениями гл., стр., рис., илл., ст., п.",
        "pattern"    : "/(\\s|^|\\>|\\()(гл|стр|рис|илл?|ст|п|с)\\.(\\040|\\t)*(\\d+)(\\&nbsp\\;|\\s|\\.|\\,|\\?|\\!|$)/iu",
        "replacement": "\\1\\2.&nbsp;\\4\\5"
    },
    {
        "rule_id"    : "nobr_sm_im",
        "description": "Расстановка пробелов перед сокращениями см., им.",
        "pattern"    : "/(\\s|^|\\>|\\()(см|им)\\.(\\040|\\t)*([а-яё0-9a-z]+)(\\s|\\.|\\,|\\?|\\!|$)/iu",
        "replacement": "\\1\\2.&nbsp;\\4\\5"
    },
    {
        "rule_id"    : "nobr_locations",
        "description": "Расстановка пробелов в сокращениях г., ул., пер., д.",
        "pattern"    : [
            "/(\\s|^|\\>)(г|ул|пер|просп|пл|бул|наб|пр|ш|туп)\\.(\\040|\\t)*([а-яё0-9a-z]+)(\\s|\\.|\\,|\\?|\\!|$)/iu",
            "/(\\s|^|\\>)(б\\-р|пр\\-кт)(\\040|\\t)*([а-яё0-9a-z]+)(\\s|\\.|\\,|\\?|\\!|$)/iu",
            "/(\\s|^|\\>)(д|кв|эт)\\.(\\040|\\t)*(\\d+)(\\s|\\.|\\,|\\?|\\!|$)/iu"
        ],
        "replacement": [
            "\\1\\2.&nbsp;\\4\\5",
            "\\1\\2&nbsp;\\4\\5",
            "\\1\\2.&nbsp;\\4\\5"
        ]
    },
    {
        "rule_id"    : "nbsp_before_unit",
        "description": "Замена символов и привязка сокращений в размерных величинах: м, см, м2…",
        "pattern"    : [
            "/(\\s|^|\\>|\\&nbsp\\;|\\,)(\\d+)( |\\&nbsp\\;)?(м|мм|см|дм|км|гм|km|dm|cm|mm)(\\s|\\.|\\!|\\?|\\,|$|\\&plusmn\\;|\\;|\\<)/iu",
            "/(\\s|^|\\>|\\&nbsp\\;|\\,)(\\d+)( |\\&nbsp\\;)?(м|мм|см|дм|км|гм|km|dm|cm|mm)([32]|&sup3;|&sup2;)(\\s|\\.|\\!|\\?|\\,|$|\\&plusmn\\;|\\;|\\<)/iue"
        ],
        "replacement": [
            "\\1\\2&nbsp;\\4\\5",
            lambda m, s: m.group(1) + m.group(2) + "&nbsp;" + m.group(4) + (
                ("&sup" + m.group(5) + ";" if m.group(5) == "3" or m.group(5) == "2" else  m.group(5))) + m.group(6)
        ]
    },
    {
        "rule_id"    : "nbsp_before_weight_unit",
        "description": "Замена символов и привязка сокращений в весовых величинах: г, кг, мг…",
        "pattern"    : "/(\\s|^|\\>|\\&nbsp\\;|\\,)(\\d+)( |\\&nbsp\\;)?(г|кг|мг|т)(\\s|\\.|\\!|\\?|\\,|$|\\&nbsp\\;|\\;)/iu",
        "replacement": "\\1\\2&nbsp;\\4\\5"
    },
    {
        "rule_id"    : "nobr_before_unit_volt",
        "description": "Установка пробельных символов в сокращении вольт",
        "pattern"    : "/(\\d+)([вВ]| В)(\\s|\\.|\\!|\\?|\\,|$)/u",
        "replacement": "\\1&nbsp;В\\3"
    },
    {
        "rule_id"    : "ps_pps",
        "description": "Объединение сокращений P.S., P.P.S.",
        "pattern"    : "/(^|\\040|\\t|\\>|\\r|\\n)(p\\.\\040?)(p\\.\\040?)?(s\\.)([^\\<])/ie",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(
            m.group(2).strip() + " " + (m.group(3).strip() + " " if m.group(3)  else  "") + m.group(4), s) + m.group(
            5)
    },
    {
        "rule_id"    : "nobr_vtch_itd_itp",
        "description": "Объединение сокращений и т.д., и т.п., в т.ч.",
        "cycled"     : True,
        "pattern"    : [
            "/(^|\\s|\\&nbsp\\;)и( |\\&nbsp\\;)т\\.?[ ]?д(\\.|$|\\s|\\&nbsp\\;)/ue",
            "/(^|\\s|\\&nbsp\\;)и( |\\&nbsp\\;)т\\.?[ ]?п(\\.|$|\\s|\\&nbsp\\;)/ue",
            "/(^|\\s|\\&nbsp\\;)в( |\\&nbsp\\;)т\\.?[ ]?ч(\\.|$|\\s|\\&nbsp\\;)/ue"
        ],
        "replacement": [
            lambda m, s: m.group(1) + wrap_in_nowrap("и т. д.", s) + (
                (m.group(3) if m.group(3) != "." else  "")),
            lambda m, s: m.group(1) + wrap_in_nowrap("и т. п.", s) + (
                (m.group(3) if m.group(3) != "." else  "")),
            lambda m, s: m.group(1) + wrap_in_nowrap("в т. ч.", s) + (
                (m.group(3) if m.group(3) != "." else  ""))
        ]
    },
    {
        "rule_id"    : "nbsp_te",
        "description": "Обработка т.е.",
        "pattern"    : "/(^|\\s|\\&nbsp\\;)([тТ])\\.?[ ]?е\\./ue",
        "replacement": lambda m, s: m.group(1) + wrap_in_nowrap(m.group(2) + ". е.", s)
    },
    {
        "rule_id"    : "nbsp_money_abbr",
        "description": "Форматирование денежных сокращений (расстановка пробелов и привязка названия валюты к числу)",
        "pattern"    : "/(\\d)((\\040|\\&nbsp\\;)?(тыс|млн|млрд)\\.?(\\040|\\&nbsp\\;)?)?(\\040|\\&nbsp\\;)?(руб\\.|долл\\.|евро|€|&euro;|\\$|у[\\.]? ?е[\\.]?)/ieu",
        "replacement": lambda m, s: m.group(1) + (
            "&nbsp;" + m.group(4) + ("." if m.group(4) == "тыс" else "") if m.group(4) else "") + "&nbsp;" + (
                                        m.group(7) if not re.match("у[\\\\.]? ?е[\\\\.]?", m.group(7),
                                                                   re.I | re.U) else "у.е.")
    },
    {
        "rule_id"    : "nbsp_money_abbr_rev",
        "description": "Привязка валюты к числу спереди",
        "pattern"    : "/(€|&euro;|\\$)\\s?(\\d)/iu",
        "replacement": "\\1&nbsp;\\2"
    },
    {
        "rule_id"    : "nbsp_org_abbr",
        "description": "Привязка сокращений форм собственности к названиям организаций",
        "pattern"    : "/([^a-zA-Zа-яёА-ЯЁ]|^)(ООО|ЗАО|ОАО|НИИ|ПБОЮЛ) ([a-zA-Zа-яёА-ЯЁ]|\\\"|\\&laquo\\;|\\&bdquo\\;|<)/u",
        "replacement": "\\1\\2&nbsp;\\3"
    },
    {
        "rule_id"    : "nobr_gost",
        "description": "Привязка сокращения ГОСТ к номеру",
        "pattern"    : [
            "/(\\040|\\t|\\&nbsp\\;|^)ГОСТ( |\\&nbsp\\;)?(\\d+)((\\-|\\&minus\\;|\\&mdash\\;)(\\d+))?(( |\\&nbsp\\;)(\\-|\\&mdash\\;))?/ieu",
            "/(\\040|\\t|\\&nbsp\\;|^|\\>)ГОСТ( |\\&nbsp\\;)?(\\d+)(\\-|\\&minus\\;|\\&mdash\\;)(\\d+)/ieu"
        ],
        "replacement": [
            lambda m, s: m.group(1) + wrap_in_nowrap(
                "ГОСТ " + m.group(3) + ("&ndash;" + m.group(6) if (m.group(6)) else "") + (
                    (" &mdash;" if (m.group(7)) else "")), s),
            lambda m, s: m.group(1) + "ГОСТ " + m.group(3) + "&ndash;" + m.group(5)
        ]
    }
])

RULEDEF_SPACE = convert_ruledefs_to_rules([
    {
        "rule_id"    : "nobr_twosym_abbr",
        "description": "Неразрывный перед 2х символьной аббревиатурой",
        "pattern"    : "/([a-zA-Zа-яёА-ЯЁ])(\\040|\\t)+([A-ZА-ЯЁ]{2})([\\s\\;\\.\\?\\!\\:\\(\\\"]|\\&(ra|ld)quo\\;|$)/u",
        "replacement": "\\1&nbsp;\\3\\4"
    },
    {
        "rule_id"    : "remove_space_before_punctuationmarks",
        "description": "Удаление пробела перед точкой, запятой, двоеточием, точкой с запятой",
        "pattern"    : "/((\\040|\\t|\\&nbsp\\;)+)([\\,\\:\\.\\;\\?])(\\s+|$)/",
        "replacement": "\\3\\4"
    },
    {
        "rule_id"    : "autospace_after_comma",
        "description": "Пробел после запятой",
        "pattern"    : [
            "/(\\040|\\t|\\&nbsp\\;)\\,([а-яёa-z0-9])/iu",
            "/([^0-9])\\,([а-яёa-z0-9])/iu"
        ],
        "replacement": [
            ", \\2",
            "\\1, \\2"
        ]
    },
    {
        "rule_id"    : "autospace_after_pmarks",
        "description": "Пробел после знаков пунктуации, кроме точки",
        "pattern"    : "/(\\040|\\t|\\&nbsp\\;|^|\\n)([a-zа-яё0-9]+)(\\040|\\t|\\&nbsp\\;)?(\\:|\\)|\\,|\\&hellip\\;|(?:\\!|\\?)+)([а-яёa-z])/iu",
        "replacement": "\\1\\2\\4 \\5"
    },
    {
        "rule_id"    : "autospace_after_dot",
        "description": "Пробел после точки",
        "pattern"    : [
            "/(\\040|\\t|\\&nbsp\\;|^)([a-zа-яё0-9]+)(\\040|\\t|\\&nbsp\\;)?\\.([а-яёa-z]{5,})($|[^a-zа-яё])/iue",
            "/(\\040|\\t|\\&nbsp\\;|^)([a-zа-яё0-9]+)\\.([а-яёa-z]{1,4})($|[^a-zа-яё])/iue"
        ],
        "replacement": [
            lambda m, s: m.group(1) + m.group(2) + "." + ("" if m.group(5) == "."  else  " ") + m.group(4) + m.group(5),
            lambda m, s: m.group(1) + m.group(2) + "." + (
                ("" if (m.group(3)).lower() in DOMAINS else ("" if m.group(4) == "."  else  " "))) + m.group(
                3) + m.group(4)
        ]
    },
    {
        "rule_id"    : "autospace_after_hellips",
        "description": "Пробел после знаков троеточий с вопросительным или восклицательными знаками",
        "pattern"    : "/([\\?\\!]\\.\\.)([а-яёa-z])/iu",
        "replacement": "\\1 \\2"
    },
    {
        "rule_id"    : "many_spaces_to_one",
        "description": "Удаление лишних пробельных символов и табуляций",
        "pattern"    : "/(\\040|\\t)+/",
        "replacement": " "
    },
    {
        "rule_id"    : "clear_percent",
        "description": "Удаление пробела перед символом процента",
        "pattern"    : "/(\\d+)([\\t\\040]+)\\%/",
        "replacement": "\\1%"
    },
    {
        "rule_id"    : "nbsp_before_open_quote",
        "description": "Неразрывный пробел перед открывающей скобкой",
        "pattern"    : "/(^|\\040|\\t|>)([a-zа-яё]{1,2})\\040(\\&laquo\\;|\\&bdquo\\;)/u",
        "replacement": "\\1\\2&nbsp;\\3"
    },
    {
        "rule_id"    : "nbsp_before_month",
        "description": "Неразрывный пробел в датах перед числом и месяцем",
        "pattern"    : "/(\\d)(\\s)+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)([^\\<]|$)/iu",
        "replacement": "\\1&nbsp;\\3\\4"
    },
    {
        "rule_id"    : "spaces_on_end",
        "description": "Удаление пробелов в конце текста",
        "pattern"    : "/ +$/",
        "replacement": "",
        "debug"      : True
    },
    {
        "rule_id"    : "no_space_posle_hellip",
        "description": "Отсутстввие пробела после троеточия после открывающей кавычки",
        "pattern"    : "/(\\&laquo\\;|\\&bdquo\\;)( |\\&nbsp\\;)?\\&hellip\\;( |\\&nbsp\\;)?([a-zа-яё])/ui",
        "replacement": "\\1&hellip;\\4"
    },
    {
        "rule_id"    : "space_posle_goda",
        "description": "Пробел после года",
        "pattern"    : "/(^|\\040|\\&nbsp\\;)([0-9]{3,4})(год([ауе]|ом)?)([^a-zа-яё]|$)/ui",
        "replacement": "\\1\\2 \\3\\5"
    }
])
RULEDEF_NUMBERS = convert_ruledefs_to_rules([
    {
        "rule_id"    : "minus_between_nums",
        "description": "Расстановка знака минус между числами",
        "pattern"    : "/(\\d+)\\-(\\d)/i",
        "replacement": "\\1&minus;\\2"
    },
    {
        "rule_id"    : "minus_in_numbers_range",
        "description": "Расстановка знака минус между диапозоном чисел",
        "pattern"    : "/(^|\\s|\\&nbsp\\;)(\\&minus\\;|\\-)(\\d+)(\\.\\.\\.|\\&hellip\\;)(\\s|\\&nbsp\\;)?(\\+|\\-|\\&minus\\;)?(\\d+)/ie",
        # nopep8
        "replacement": lambda m, s: m.group(1) + "&minus;" + m.group(3) + m.group(4) + m.group(5) + (
            (m.group(6) if m.group(6) == "+" else "&minus;")) + m.group(7)
    },
    {
        "rule_id"    : "auto_times_x",
        "description": "Замена x на символ × в размерных единицах",
        "cycled"     : True,
        "pattern"    : "/([^a-zA-Z><]|^)(|\\&times\\;)(\\d+)(\\040*)(x|х)(\\040*)(\\d+)([^a-zA-Z><]|$)/u",
        "replacement": "\\1\\2\\3&times;\\7\\8"
    },
    {
        "rule_id"    : "numeric_sub",
        "description": "Нижний индекс",
        "pattern"    : "/([a-zа-яё0-9])\\_([\\d]{1,3})([^@а-яёa-z0-9]|$)/ieu",
        "replacement": lambda m, s: m.group(1) + wrap_in_typo_sub(m.group(2), s) + m.group(3)
    },
    {
        "rule_id"    : "numeric_sup",
        "description": "Верхний индекс",
        "pattern"    : "/([a-zа-яё0-9])\\^([\\d]{1,3})([^а-яёa-z0-9]|$)/ieu",
        "replacement": lambda m, s: m.group(1) + wrap_in_typo_sup(m.group(2), s) + m.group(3)
    },
    {
        "rule_id"    : "simple_fraction",
        "description": "Замена дробей 1/2, 1/4, 3/4 на соответствующие символы",
        "pattern"    : [
            "/(^|\\D)1\\/(2|4)(\\D)/",
            "/(^|\\D)3\\/4(\\D)/"
        ],
        "replacement": [
            "\\1&frac1\\2;\\3",
            "\\1&frac34;\\2"
        ]
    },
    {
        "rule_id"    : "math_chars",
        "description": "Математические знаки больше/меньше/плюс минус/неравно",
        "pattern"    : [
            "/!=/",
            "/\\<=/",
            "/([^=]|^)\\>=/",
            "/~=/",
            "/\\+-/"
        ],
        "replacement": [
            "&ne;",
            "&le;",
            "\\1&ge;",
            "&cong;",
            "&plusmn;"
        ]
    },
    {
        "rule_id"    : "thinsp_between_number_triads",
        "description": "Объединение триад чисел полупробелом",
        "pattern"    : "/([0-9]{1,3}( [0-9]{3}){1,})(.|$)/ue",
        "replacement": lambda m, s: (
            (m.group(0) if m.group(3) == "-" else m.group(1).replace(" ", "&thinsp;") + m.group(3)))
    },
    {
        "rule_id"    : "thinsp_between_no_and_number",
        "description": "Пробел между симоволом номера и числом",
        "pattern"    : "/(№|\\&#8470\\;)(\\s|&nbsp;)*(\\d)/iu",
        "replacement": "&#8470;&thinsp;\\3"
    },
    {
        "rule_id"    : "thinsp_between_sect_and_number",
        "description": "Пробел между параграфом и числом",
        "pattern"    : "/(§|\\&sect\\;)(\\s|&nbsp;)*(\\d+|[IVX]+|[a-zа-яё]+)/ui",
        "replacement": "&sect;&thinsp;\\3"
    }
])

RULEDEF_PUNKT = convert_ruledefs_to_rules([
    {
        "rule_id"    : "auto_comma",
        "description": "Расстановка запятых перед а, но",
        "pattern"    : "/([a-zа-яё])(\\s|&nbsp;)(но|а)(\\s|&nbsp;)/iu",
        "replacement": "\\1,\\2\\3\\4"
    },
    {
        "rule_id"    : "punctuation_marks_limit",
        "description": "Лишние восклицательные, вопросительные знаки и точки",
        "pattern"    : "/([\\!\\.\\?]){4,}/",
        "replacement": "\\1\\1\\1"
    },
    {
        "rule_id"    : "punctuation_marks_base_limit",
        "description": "Лишние запятые, двоеточия, точки с запятой",
        "pattern"    : "/([\\,]|[\\:]|[\\;]]){2,}/",
        "replacement": "\\1"
    },
    {
        "rule_id"       : "hellip",
        "description"   : "Замена трех точек на знак многоточия",
        "simple_replace": True,
        "pattern"       : "...",
        "replacement"   : "&hellip;"
    },
    {
        "rule_id"    : "fix_excl_quest_marks",
        "description": "Замена восклицательного и вопросительного знаков местами",
        "pattern"    : "/([a-zа-яё0-9])\\!\\?(\\s|$|\\<)/ui",
        "replacement": "\\1?!\\2"
    },
    {
        "rule_id"    : "fix_pmarks",
        "description": "Замена сдвоенных знаков препинания на одинарные",
        "pattern"    : [
            "/([^\\!\\?])\\.\\./",
            "/([a-zа-яё0-9])(\\!|\\.)(\\!|\\.|\\?)(\\s|$|\\<)/ui",
            "/([a-zа-яё0-9])(\\?)(\\?)(\\s|$|\\<)/ui"
        ],
        "replacement": [
            "\\1.",
            "\\1\\2\\4",
            "\\1\\2\\4"
        ]
    },
    {
        "rule_id"    : "fix_brackets",
        "description": "Лишние пробелы после открывающей скобочки и перед закрывающей",
        "pattern"    : [
            "/(\\()(\\040|\\t)+/",
            "/(\\040|\\t)+(\\))/"
        ],
        "replacement": [
            "\\1",
            "\\2"
        ]
    },
    {
        "rule_id"    : "fix_brackets_space",
        "description": "Пробел перед открывающей скобочкой",
        "pattern"    : "/([a-zа-яё])(\\()/iu",
        "replacement": "\\1 \\2"
    },
    {
        "rule_id"    : "dot_on_end",
        "description": "Точка в конце текста, если её там нет",
        "disabled"   : True,
        "pattern"    : "/([a-zа-яё0-9])(\\040|\\t|\\&nbsp\\;)*$/ui",
        "replacement": "\\1."
    }
])

RULEDEF_SYMBOLS = convert_ruledefs_to_rules([
    {
        "rule_id"    : "tm_replace",
        "description": "Замена (tm) на символ торговой марки",
        "pattern"    : "/([\\040\\t])?\\(tm\\)/i",
        "replacement": "&trade;"
    },
    {
        "rule_id"    : "reg_replace",
        "description": "Замена (R) на символ REG",
        "pattern"    : "/®/i",
        "replacement": "&reg;"
    },
    {
        "rule_id"    : "r_sign_replace",
        "description": "Замена (R) на символ зарегистрированной торговой марки",
        "pattern"    : [
            "/(.|^)\\(r\\)(.|$)/ie"
        ],
        "replacement": [
            lambda m, s: m.group(1) + "&reg;" + m.group(2)
        ]
    },
    {
        "rule_id"    : "copy_replace",
        "description": "Замена (c) на символ копирайт",
        "pattern"    : [
            "/\\((c|с)\\)\\s+/iu",
            "/\\((c|с)\\)($|\\.|,|!|\\?)/iu"
        ],
        "replacement": [
            "&copy;&nbsp;",
            "&copy;\\2"
        ]
    },
    {
        "rule_id"    : "apostrophe",
        "description": "Расстановка правильного апострофа в текстах",
        "pattern"    : "/(\\s|^|\\>|\\&rsquo\\;)([a-zа-яё]{1,})\'([a-zа-яё]+)/ui",
        "replacement": "\\1\\2&rsquo;\\3",
        "cycled"     : True
    },
    {
        "rule_id"    : "degree_f",
        "description": "Градусы по Фаренгейту",
        "pattern"    : "/([0-9]+)F($|\\s|\\.|\\,|\\;|\\:|\\&nbsp\\;|\\?|\\!)/eu",
        "replacement": lambda m, s: "" + wrap_in_nowrap(m.group(1) + " &deg;F", s) + m.group(2)
    },
    {
        "rule_id"       : "euro_symbol",
        "description"   : "Символ евро",
        "simple_replace": True,
        "pattern"       : "€",
        "replacement"   : "&euro;"
    },
    {
        "rule_id"    : "arrows_symbols",
        "description": "Замена стрелок вправо-влево на html коды",
        "pattern"    : [
            "/\\-\\>/",
            "/\\<\\-/",
            "/→/u",
            "/←/u"
        ],
        "replacement": [
            "&rarr;",
            "&larr;",
            "&rarr;",
            "&larr;"
        ]
    }
])

RULEDEF_DASH = convert_ruledefs_to_rules([
    {
        "rule_id"    : "mdash_symbol_to_html_mdash",
        "description": "Замена символа тире на html конструкцию",
        "pattern"    : "/(—|--)/i",
        "replacement": "&mdash;",
    },
    {
        "rule_id"    : "mdash",
        "description": "Тире после кавычек, скобочек, пунктуации",
        "pattern"    : [
            "/([a-zа-яё0-9]+|\\,|\\:|\\)|\\&(ra|ld)quo\\;|\\|\\\"|\\>)(\\040|\\t)(—|\\-|\\&mdash\\;)(\\s|$|\\<)/ui",
            "/(\\,|\\:|\\)|\\\")(—|\\-|\\&mdash\\;)(\\s|$|\\<)/ui"
        ],
        "replacement": [
            "\\1&nbsp;&mdash;\\5",
            "\\1&nbsp;&mdash;\\3"
        ]
    },
    {
        "rule_id"    : "mdash_2",
        "description": "Тире после переноса строки",
        "pattern"    : "/(\\n|\\r|^|\\>)(\\-|\\&mdash\\;)(\\t|\\040)/",
        "replacement": "\\1&mdash;&nbsp;"
    },
    {
        "rule_id"    : "mdash_3",
        "description": "Тире после знаков восклицания, троеточия и прочее",
        "pattern"    : "/(\\.|\\!|\\?|\\&hellip\\;)(\\040|\\t|\\&nbsp\\;)(\\-|\\&mdash\\;)(\\040|\\t|\\&nbsp\\;)/",
        "replacement": "\\1 &mdash;&nbsp;"
    },
    {
        "rule_id"    : "iz_za_pod",
        "description": "Расстановка дефисов между из-за, из-под",
        "pattern"    : "/(\\s|\\&nbsp\\;|\\>|^)(из)(\\040|\\t|\\&nbsp\\;)\\-?(за|под)([\\.\\,\\!\\?\\:\\;]|\\040|\\&nbsp\\;)/uie",
        "replacement": lambda m, s:
        (" " if m.group(1) == "&nbsp;"  else m.group(1)) + m.group(2) + "-" + m.group(4) + (
            (" " if m.group(5) == "&nbsp;" else  m.group(5)))
    },
    {
        "rule_id"    : "to_libo_nibud",
        "description": "Автоматическая простановка дефисов в обезличенных местоимениях и междометиях",
        "cycled"     : True,
        "pattern"    : "/(\\s|^|\\&nbsp\\;|\\>)(кто|кем|когда|зачем|почему|как|что|чем|где|чего|кого)\\-?(\\040|\\t|\\&nbsp\\;)\\-?(то|либо|нибудь)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie",
        "replacement": lambda m, s: (" " if m.group(1) == "&nbsp;"  else  m.group(1)) + m.group(2) + "-" + m.group(
            4) + (" " if m.group(5) == "&nbsp;" else  m.group(5)),
        "doctests"   : [
            ("где то", "где-то"),
            ("Кто то где то когда то как то что то чем то стукнул.",
             "Кто-то где-то когда-то как-то что-то чем-то стукнул."),
        ]
    },
    {
        "rule_id"    : "koe_kak",
        "description": "Кое-как, кой-кого, все-таки",
        "cycled"     : True,
        "pattern"    : [
            "/(\\s|^|\\&nbsp\\;|\\>)(кое)\\-?(\\040|\\t|\\&nbsp\\;)\\-?(как)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie",
            "/(\\s|^|\\&nbsp\\;|\\>)(кой)\\-?(\\040|\\t|\\&nbsp\\;)\\-?(кого)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie",
            "/(\\s|^|\\&nbsp\\;|\\>)(вс[её])\\-?(\\040|\\t|\\&nbsp\\;)\\-?(таки)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie"
        ],
        "replacement": lambda m, s: (" " if m.group(1) == "&nbsp;"  else  m.group(1)) + m.group(2) + "-" + m.group(
            4) + (" " if m.group(5) == "&nbsp;" else  m.group(5))
    },
    {
        "rule_id"    : "ka_de_kas",
        "description": "Расстановка дефисов с частицами ка, де, кась",
        "disabled"   : True,
        "pattern"    : [
            "/(\\s|^|\\&nbsp\\;|\\>)([а-яё]+)(\\040|\\t|\\&nbsp\\;)(ка)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie",
            "/(\\s|^|\\&nbsp\\;|\\>)([а-яё]+)(\\040|\\t|\\&nbsp\\;)(де)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie",
            "/(\\s|^|\\&nbsp\\;|\\>)([а-яё]+)(\\040|\\t|\\&nbsp\\;)(кась)([\\.\\,\\!\\?\\;]|\\040|\\&nbsp\\;|$)/uie"
        ],
        "replacement": lambda m, s: (" " if m.group(1) == "&nbsp;"  else  m.group(1)) + m.group(2) + "-" + m.group(
            4) + (" " if m.group(5) == "&nbsp;" else m.group(5))
    }
])

ALL_RULES = BASIC_CLEANUP + RULEDEF_QUOTES + RULEDEF_DASH + RULEDEF_SYMBOLS + RULEDEF_PUNKT + RULEDEF_NUMBERS + RULEDEF_SPACE + RULEDEF_ABBR + RULEDEF_NOBR + RULEDEF_DATES + RULEDEF_OPTS + RULEDEF_ETC

DEFAULT_SETTINGS = TypographEnvironment(ALL_RULES)


def get_default_environment() -> TypographEnvironment:
    return DEFAULT_SETTINGS
