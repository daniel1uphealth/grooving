#! python3

import sys
import ply.lex as lex
import ply.yacc as yacc


reserved = {
    'new': 'NEW',
    'def': 'DEF'
}


def t_ID(t):
    '''[a-zA-Z_][a-zA-Z0-9_]*'''
    t.type = reserved.get(t.value, 'ID')
    return t


def t_error(t):
    sys.stderr.write("Illegal character '%s'\n" % t.value[0])

# Match double-quated strings, including '""""', but not ',"","",'
t_DSTR = r'""([^,"]||[^"]{2,})""'
# Single quoted strings tend to be simpler
t_SSTR = r'\'[^\']*\''
t_COMP = r'[<>]=?'
t_EQ = r'[=!]='
t_AND = r'&&'
t_OR = r'\|\|'
t_NUM = r'\d+'
t_QDOT = r'\?\.'
t_QUERY = r'\?'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_PLUS = r'\+'
t_QUOTE = r'"'
t_AT = r'@'
t_COLON = r':'
t_COMMA = r','

t_ignore = ' \t\n'

tokens = ['QUERY', 'COLON', 'DOT', 'COMMA', 'LPAREN', 'RPAREN', 'DSTR', 'SSTR', 'ID', 'LBRAC', 'RBRAC', 'NUM', 'COMP',
          'EQ', 'PLUS', 'QUOTE', 'AT', 'AND', 'OR', 'QDOT'] + list(reserved.values())

# Track progress through the file
succeeded = 0
failed = 0
line_num = 0


def p_mapping(p):
    """mapping : file COMMA type COMMA namespace COMMA path COMMA value"""
    p[0] = p[1] + "," + p[3] + "," + p[5] + "," + p[7] + "," + p[9]


def p_file(p):
    '''file : QUOTE file QUOTE
            | ID'''
    p[0] = to_string(p)


def p_type(p):
    '''type : QUOTE type QUOTE
            | ID'''
    p[0] = to_string(p)


def p_namespace(p):
    '''namespace : QUOTE namespace QUOTE
                 | path_elem'''
    p[0] = to_string(p)


def p_path(p):
    '''path : QUOTE path QUOTE
            | path DOT path_elem
            | path_elem'''
    p[0] = to_string(p)


def p_path_elem(p):
    '''path_elem : ID
                 | ID LBRAC NUM RBRAC
                 | ID LBRAC ID RBRAC
                 | ID LBRAC path_id RBRAC'''
    p[0] = to_string(p)


def p_path_id(p):
    '''path_id : ID AT ID COLON ID'''
    p[0] = to_string(p)


def p_quoted_value(p):
    '''value : QUOTE term QUOTE'''
    p[0] = '"' + p[2] + '"'


def p_value(p):
    '''value : term'''
    p[0] = '"' + p[1] + '"'


def p_term(p):
    '''term : LPAREN term RPAREN
            | complex_term'''
    p[0] = to_string(p)


def p_string_term(p):
    '''string_term : string DOT complex_term
                   | string LBRAC NUM RBRAC
                   | string'''
    p[0] = to_string(p)


def p_string(p):
    '''string : DSTR
              | SSTR'''
    p[0] = p[1]


def p_complex_term(p):
    '''complex_term : simple_term
                    | ternary_term'''
    p[0] = p[1]


def p_simple_term_ops(p):
    '''simple_term : simple_term DOT terminal_term
                   | simple_term PLUS terminal_term
                   | LPAREN simple_term RPAREN'''
    if p[1] == '_' and p[2] == '.':
        p[0] = p[3]
    else:
        p[0] = p[1] + p[2] + p[3]


def p_simple_term_null(p):
    '''simple_term : simple_term QDOT terminal_term'''
    p[0] = p[1] + p[2] + p[3]


def p_simple_term(p):
    '''simple_term : terminal_term'''
    p[0] = p[1]


def p_terminal_term(p):
    '''terminal_term : array
                     | func
                     | ID
                     | NUM
                     | string_term
                     | empty'''
    p[0] = p[1]


def p_terminal_term_func(p):
    '''terminal_term : NEW func'''
    p[0] = p[1] + ' ' + p[2]


def p_array(p):
    'array : ID LBRAC NUM RBRAC'
    p[0] = to_string(p)


def p_func(p):
    '''func : ID LPAREN params RPAREN
            | ID LPAREN RPAREN'''
    p[0] = to_string(p)


def p_params(p):
    '''params : params COMMA term
              | term'''
    p[0] = to_string(p)


def p_ternary_term(p):
    '''ternary_term : ternary
               | LPAREN ternary_term RPAREN
               | ternary_term PLUS term'''
    p[0] = to_string(p)


def p_simple_ternary(p):
    '''ternary : compound_bool QUERY simple_term COLON simple_term'''
    p[0] = "if " + p[1] + " display " + p[3] + "\notherwise display " + p[5]


def p_complex_ternary1(p):
    '''ternary : compound_bool QUERY ternary_term COLON simple_term'''
    sub = '\t' + '\n\t'.join(p[3].split('\n'))
    p[0] = "if " + p[1] + "\n" + sub + "\notherwise display " + p[5]


def p_complex_ternary2(p):
    '''ternary : compound_bool QUERY simple_term COLON ternary_term'''
    p[0] = "if " + p[1] + " display " + p[3] + "\notherwise " + p[5]


def p_compound_bool_parens(p):
    '''compound_bool : LPAREN compound_bool RPAREN'''
    p[0] = to_string(p)


def p_compound_bool(p):
    '''compound_bool : compound_bool AND bool
                     | compound_bool OR bool'''
    p[0] = "%s %s %s" % (p[1], bool_to_string(p[2]), p[3])


def p_compound_bool_bool(p):
    '''compound_bool : bool'''
    p[0] = p[1]


def p_bool(p):
    '''bool : LPAREN bool RPAREN
            | term COMP term
            | term EQ term
            | term'''
    p[0] = to_string(p)


def p_empty(p):
    '''empty :'''
    p[0] = '<BLANK>'


def parse(data, debug=False):
    global failed, succeeded, line_num

    # If the pre-parser couldn't handle the trailing fields, call it a failure and move on.
    # This is a ugly way to handle the error, but this is the function where we're
    # tracking the number of failed lines.
    if not data:
        failed += 1
        return

    l = lex.lex()
    l.input(data)

    y = yacc.yacc()
    parsed = None

    try:
        parsed = y.parse(data, debug=debug)
    except:
        parsed = None

    if parsed:
        sys.stdout.write("%d,%s\n" % (line_num, parsed))
        succeeded += 1
    else:
        sys.stderr.write("!!! %d,%s\n" % (line_num, data))
        failed += 1


def to_string(p):
    out = ""
    for i in range(1, len(p)):
        out += p[i]

    return out


def bool_to_string(b):
    if b == '&&':
        return 'and'
    elif b == '||':
        return 'or'
    else:
        return b


def translate(file):
    global line_num
    first = True
    to_parse = None

    for line in file.readlines():
        if first:
            # Check if the first line is a header
            fields = line.strip().split(',')
            header = True

            # If not every field is present and quoted, it's not a header line
            for field in fields:
                if len(field) < 3 or field[0] != '"' or field[-1] != '"':
                    header = False
                    break

            # If it is a header, just skip it
            if header:
                continue

            first = False

        # Because rows can span lines, put the full row together before parsing
        if to_parse:
            to_parse += line.strip()
        else:
            to_parse = line.strip()

        # Really bold assumption here! In our data files, the last column is always
        # empty. When a row is split across lines, it's in the middle of code.
        # Therefore, if we see a trailing comma, it means we've found the end of the
        # line.
        if to_parse.endswith(','):
            line_num += 1
            parse(strip_trailing_fields(to_parse))
            to_parse = None

    if to_parse:
        sys.stderr.write("Last line is incomplete: %s\n" % to_parse)


def strip_trailing_fields(line):
    out = None
    count = 0
    in_quote = False
    skip = False
    i = 0

    # We parse this manually because it's just too hard to do with regex
    for i in range(len(line) - 1, 0, -1):
        if skip:
            skip = False
        elif in_quote and line[i] == '"' and line[i - 1] == '"':
            skip = True
        elif line[i] == '"':
            in_quote = not in_quote
        elif not in_quote and line[i] == ',':
            count += 1

            if count == 8:
                out = line[0:i]
                break

    if i <= 0:
        sys.stderr.write("Could not match fields 6-13: %s\n" % line)

    return out


def usage():
    sys.stdout.write("python3 grooving.py [filename]\n")


if __name__ == "__main__":
    failed = 0

    if len(sys.argv) == 1:
        translate(sys.stdin)
    elif len(sys.argv) == 2 and sys.argv[1] == '--help':
        usage()
        sys.exit(1)
    elif len(sys.argv) == 2:
        translate(open(sys.argv[1], "r"))
    elif len(sys.argv) == 3 and sys.argv[1] == '-X':
        data = sys.argv[2]
        parse(data, True)
    else:
        sys.stderr.write("Unexpected arguments: %s\n" % " ".join(sys.argv[1:]))
        usage()
        sys.exit(1)

    sys.stderr.write("%d failed, %d succeeded\n" % (failed, succeeded))
    sys.exit(0)
