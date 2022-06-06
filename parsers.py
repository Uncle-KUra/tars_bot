def stupid_tokenize(s):
    s = s.lower()
    result = []
    current = []
    prev_c = ''
    for c in s:
        print(c)
        if c == ' ':
            result.append(''.join(current))
            current = []
            prev_c = ' '
            continue
        if not c.isalnum():
            result.append(''.join(current))
            result.append(c)
            current = []
            prev_c = ' '
            continue
        if c.isalpha() != prev_c.isalpha():
            result.append(''.join(current))
            current = [c]
            prev_c = c
            continue
        current.append(c)
        prev_c = c
    result.append(''.join(current))
    return [x for x in result if x]


def is_help_string(s):
    return s in ('h', 'help')


def is_prefix(s):
    return s in ('?', '!')


def parse_help(parts):
    if len(parts) == 1 and is_help_string(parts[0]):
        return True, False
    if len(parts) == 2 and is_prefix(parts[0]) and is_help_string(parts[1]):
        return True, False
    if len(parts) == 2 and is_prefix(parts[1]) and is_help_string(parts[0]):
        return True, False
    if len(parts) == 2 and parts[0] == '?' and parts[1] == '?':
        return True, True
    if len(parts) == 2 and parts[0] == '!' and parts[1] == '?':
        return True, True
    return False, None