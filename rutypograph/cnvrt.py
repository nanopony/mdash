import re

s = r' m.group(2).count(u\"\\\"\")'

with open("./ruledefs_x.py", 'w') as w:
    w.write("""import re

BASE64_PARAGRAPH_TAG = 'cA==='
BASE64_BREAKLINE_TAG = 'YnIgLw==='
BASE64_NOBR_OTAG = 'bm9icg==='
BASE64_NOBR_CTAG = 'L25vYnI=='

QUOTE_FIRS_OPEN = '&laquo;'
QUOTE_FIRS_CLOSE = '&raquo;'
QUOTE_CRAWSE_OPEN = '&bdquo;'
QUOTE_CRAWSE_CLOSE = '&ldquo;'

def make_tag(*args, **kwargs):
    return ""

def util_lowercase(u):
    return u.lower()

def util_substr(s, start, length=None):
    if len(s) <= start:
        return ""
    if length is None:
        return s[start:]
    elif length == 0:
        return ""
    elif length > 0:
        return s[start:start + length]
    else:
        return s[start:length]

def util_strreplace(pattern, replacement, text):
    return text.replace(pattern, replacement)

def util_split_number(num):
    repl = ""
    for i in range(len(num), -1, -3):
        if i - 3 >= 0:
            repl = ("&thinsp;" if i > 3 else "") + num[i - 3:i] + repl
        else:
            repl = num[0:i] + repl
    return repl

def utils_nowrap_ip_address(triads):
    triad = triads.split('.')
    addTag = True

    for value in triad:
        value = int(value)
        if value > 255:
            addTag = False
            break

    if addTag == True:
        triads = make_tag(triads, 'span', {'class': "nowrap"})

    return triads
""")
    with open("./ruledefs.source", 'r') as r:
        for line in r:
            line = line.strip()
            if 'm.group' in line and not 'lambda m:' in line:
                print()
                print("XXX " + line)

                if line[0] == '"' and line[:5] != '"repl':
                    line = "lambda m: " + line[1:]
                    if line[-2:] == '",':
                        line = line[:-2] + ','
                else:
                    line = line.replace('"replacement": "', '"replacement": lambda m: ')
                line = line.replace(r'\\\"', '_QUOTE_')
                line = line.replace('\\"', '"')
                line = line.replace(r'_QUOTE_', r'\"')
                line = line.replace('u"', '"')
                line = line.replace('self.tag', 'make_tag')
                line = line.replace('self.domain_zones', 'DOMAINS')
                line = line.replace('self.nowrap_ip_address', 'utils_nowrap_ip_address')
                line = line.replace('EMT_Lib.strtolower', 'util_lowercase')
                line = line.replace('EMT_Lib.substr', 'util_substr')
                line = line.replace('EMT_Lib.str_replace', 'util_strreplace')
                line = line.replace('EMT_Lib.split_number', 'util_split_number')
                if line[-1] == '"':
                    line = line[:-1]
                print("    " + line)
            w.write(line + "\n")
