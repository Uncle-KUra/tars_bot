class ParseResult:
    def __init__(self, command=None, hard=False, params=None):
        self.command = command
        self.hard = hard
        self.params = params if params else {}


def stupid_tokenize(s):
    s = s.lower()
    result = []
    current = []
    prev_c = ''
    for c in s:
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


def is_level_string(s):
    try:
        i = int(s)
        return 2 <= i <= 15
    except ValueError:
        return False


def is_mode(s):
    return s in ('dark', 'duo', 'simple', 'common')


def convert_mode(s):
    if s == 'simple':
        return ''
    if s == 'common':
        return ''
    return s


def parse_command(parts, name, command_strings, command_weak_strings):
    def is_command(s):
        return s in command_strings

    def is_weak_command(s):
        return s in command_weak_strings

    if len(parts) == 1 and is_command(parts[0]):
        return ParseResult(name)
    if len(parts) == 2 and is_prefix(parts[0]) and is_command(parts[1]):
        return ParseResult(name)
    if len(parts) == 2 and is_prefix(parts[1]) and is_command(parts[0]):
        return ParseResult(name)
    if len(parts) == 2 and is_prefix(parts[0]) and is_weak_command(parts[1]):
        return ParseResult(name, hard=True)
    return ParseResult()


def parse_full_out(parts):
    return parse_command(parts, 'full_out', ('out', 'o', 'exit'), [])


def parse_help(parts):
    return parse_command(parts, 'help', ('help', 'h'), ('?',))


def parse_status(parts):
    return parse_command(parts, 'status', ('status', 'queue'), [])


def parse_command_with_level(parts, name, command_strings, command_weak_strings):
    def is_command(s):
        return s in command_strings

    def is_weak_command(s):
        return s in command_weak_strings

    if len(parts) == 2 and is_command(parts[0]) and is_level_string(parts[1]):
        return ParseResult(name, params={'level': int(parts[1])})
    if len(parts) == 2 and is_weak_command(parts[0]) and is_level_string(parts[1]):
        return ParseResult(name, params={'level': int(parts[1])}, hard=True)
    if len(parts) == 2 and is_weak_command(parts[1]) and is_level_string(parts[0]):
        return ParseResult(name, params={'level': int(parts[0])}, hard=True)
    if len(parts) == 3 and is_prefix(parts[0]) and is_command(parts[1]) and is_level_string(parts[2]):
        return ParseResult(name, params={'level': int(parts[2])})
    if len(parts) == 3 and is_prefix(parts[0]) and is_command(parts[2]) and is_level_string(parts[1]):
        return ParseResult(name, params={'level': int(parts[1])})
    if len(parts) == 3 and is_prefix(parts[0]) and is_weak_command(parts[1]) and is_level_string(parts[2]):
        return ParseResult(name, params={'level': int(parts[2])}, hard=True)
    if len(parts) == 3 and is_prefix(parts[0]) and is_weak_command(parts[2]) and is_level_string(parts[1]):
        return ParseResult(name, params={'level': int(parts[1])})

    if len(parts) == 3 and is_command(parts[0]) and is_level_string(parts[1]) and is_mode(parts[2]):
        return ParseResult(name, params={'level': int(parts[1]), 'mode': convert_mode(parts[2])})
    if len(parts) == 3 and is_weak_command(parts[0]) and is_level_string(parts[1]) and is_mode(parts[2]):
        return ParseResult(name, params={'level': int(parts[1]), 'mode': convert_mode(parts[2])}, hard=True)
    if len(parts) == 4 and is_prefix(parts[0]) and is_command(parts[1]) and is_level_string(parts[2]) and is_mode(
            parts[3]):
        return ParseResult(name, params={'level': int(parts[2]), 'mode': convert_mode(parts[2])})
    if len(parts) == 4 and is_prefix(parts[0]) and is_command(parts[3]) and is_level_string(parts[1]) and is_mode(
            parts[2]):
        return ParseResult(name, params={'level': int(parts[1]), 'mode': convert_mode(parts[2])})
    if len(parts) == 4 and is_prefix(parts[0]) and is_weak_command(parts[1]) and is_level_string(parts[2]) and is_mode(
            parts[3]):
        return ParseResult(name, params={'level': int(parts[2]), 'mode': convert_mode(parts[2])}, hard=True)

    return ParseResult()


def parse_level_out(parts):
    return parse_command_with_level(parts, 'level_out', ('out', 'o', 'exit'), ('-',))


def parse_level_in(parts):
    return parse_command_with_level(parts, 'level_in', ('in', 'i'), ('+',))


def parse_level_start(parts):
    return parse_command_with_level(parts, 'level_start', ('start', 's'), [])


def parse_level_dark(parts):
    return parse_command_with_level(parts, 'level_dark', ('dark',), [])


def parse_level_duo(parts):
    return parse_command_with_level(parts, 'level_dou', ('duo',), [])


def parse_all(parts):
    for parser in (parse_help, parse_full_out, parse_level_out, parse_level_in, parse_level_start, parse_level_dark,
                   parse_level_duo, parse_status):
        result = parser(parts)
        if result.command:
            return result
    return
