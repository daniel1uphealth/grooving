import sys
import re
import ply.lex as lex
import ply.yacc as yacc

tokens = ('QUERY', 'COLON', 'DOT', 'COMMA', 'LPAREN', 'RPAREN', 'STR', 'ID', 'LBRAC', 'RBRAC', 'NUM', 'COMP', 'EQ', 'PLUS', 'QUOTE', 'AT')

t_QUERY = r'\?'
t_COLON = r':'
t_DOT = r'\.'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_STR = r'""([^,"]||[^"]{2,})""'
t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_NUM = r'\d+'
t_COMP = r'[<>]=?'
t_EQ = r'[=!]='
t_PLUS = r'\+'
t_QUOTE = r'"'
t_AT = r'@'

t_ignore = ' \t\n'

re_comment = re.compile(r'(^.*),("{0,3}?)[^"]*\2,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*$')

def p_mapping(p):
    """mapping : ID COMMA ID COMMA path_elem COMMA path COMMA value"""
    p[0] = p[1] + "," + p[3] + "," + p[5] + "," + p[7] + "," + p[9]

def p_path(p):
    '''path : path DOT path_elem
            | path_elem'''
    p[0] = to_string(p)

def p_path_elem(p):
    '''path_elem : ID
                 | ID LBRAC NUM RBRAC
                 | ID LBRAC path_id RBRAC'''
    p[0] = to_string(p)

def p_path_id(p):
    '''path_id : ID AT ID COLON ID'''
    p[0] = to_string(p)

def p_value(p):
    '''value : QUOTE term QUOTE
             | term'''
    if len(p) > 2:
        p[0] = '"' + p[2] + '"'
    else:
        p[0] = '"' + p[1] + '"'

def p_term(p):
    '''term : term PLUS complex_term
            | LPAREN term RPAREN
            | complex_term
            | string_term'''
#    print("TERM: %s" % to_string(p))
    p[0] = to_string(p)

def p_string_term(p):
    '''string_term : STR DOT complex_term
                   | STR LBRAC NUM RBRAC
                   | STR'''
#    print("STRING_TERM: %s" % to_string(p))
    p[0] = to_string(p)

def p_complex_term(p):
    '''complex_term : complex_term DOT terminal_term
                    | terminal_term DOT terminal_term
                    | ID complex_term
                    | terminal_term
                    | string_term
                    | ternary'''
#    print("COMPLEX_TERM: %s" % to_string(p))
    if len(p) > 3:
        p[0] = p[1] + p[2] + p[3]
    elif len(p) > 2:
        p[0] = p[1] + ' ' + p[2]
    else:
        p[0] = p[1]

def p_simple_term(p):
    '''simple_term : simple_term DOT terminal_term
                   | terminal_term DOT terminal_term
                   | ID simple_term
                   | terminal_term
                   | string_term'''
#    print("SIMPLE_TERM: %s" % to_string(p))
    if len(p) > 3:
        p[0] = p[1] + p[2] + p[3]
    elif len(p) > 2:
        p[0] = p[1] + ' ' + p[2]
    else:
        p[0] = p[1]

def p_terminal_term(p):
    '''terminal_term : array
                     | func
                     | ID
                     | NUM'''
#    print("TERMINAL_TERM: %s" % to_string(p))
    p[0] = p[1]

def p_array(p):
    'array : ID LBRAC NUM RBRAC'
#    print("ARRAY: %s" % to_string(p))
    p[0] = to_string(p)

def p_func(p):
    '''func : ID LPAREN params RPAREN
            | ID LPAREN RPAREN'''
#    print("FUNC: %s" % to_string(p))
    p[0] = to_string(p)

def p_params(p):
    '''params : params COMMA term
              | term'''
    p[0] = to_string(p)

def p_ternary(p):
    '''ternary : simple_ternary
               | complex_ternary1
               | complex_ternary2'''
#    print("TERNARY: %s" % to_string(p))
    p[0] = p[1]

def p_simple_ternary(p):
    '''simple_ternary : condition QUERY simple_term COLON simple_term'''
#    print("SIMPLE_TERNARY: %s" % to_string(p))
    p[0] = "if " + p[1] + " display " + p[3] + "\notherwise display " + p[5]

def p_complex_ternary1(p):
    '''complex_ternary1 : condition QUERY ternary COLON simple_term'''
#    print("COMPLEX_TERNARY1: %s" % to_string(p))
    sub = '\t' + '\n\t'.join(p[3].split('\n'))
    p[0] = "if " + p[1] + "\n" + sub + "\notherwise display " + p[5]

def p_complex_ternary2(p):
    '''complex_ternary2 : condition QUERY simple_term COLON ternary'''
#    print("COMPLEX_TERNARY2: %s" % to_string(p))
    p[0] = "if " + p[1] + " display " + p[3] + "\n" + p[5]

def p_condition(p):
    '''condition : bool
                 | LPAREN bool RPAREN'''
#    print("CONDITION: %s" % to_string(p))
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_bool(p):
    '''bool : term COMP term
            | term EQ term
            | term'''
#    print("BOOL: %s" % to_string(p))
    p[0] = to_string(p)

def parse(data):
#    data = '''TPL,Coverage,coverage[coverageSegment@segment:TPL00003],period.start,"x(x)"'''
    l = lex.lex()
    l.input(data)

    # while True:
    #     tok = l.token()
    #
    #     if not tok:
    #         break
    #
    #     print(tok)

    y = yacc.yacc()
    print(">>> " + data)
    print("<<< "+"\n<<< ".join(y.parse(data).split('\n')))

def to_string(p):
    out = ""
    for i in range(1, len(p)):
        out += p[i]

    return out

def translate(file):
    first = True
    to_parse = None

    for line in file.readlines():
        if first:
            fields = line.strip().split(',')
            header = True

            for field in fields:
                if field[0] != '"' or field[-1] != '"':
                    header = False
                    break

            if header:
                continue

            first = False

        if to_parse:
            to_parse += line.strip()
        else:
            to_parse = line.strip()

        if to_parse.endswith(','):
            parse(strip_trailing_fields(to_parse))
            to_parse = None

    if to_parse:
        print("Last line is incomplete: " + to_parse)

def strip_trailing_fields(line):
    m = re_comment.match(line)
    out = None

    if m:
        out = m[1]
    else:
        print("Could not match fields 6-13")

    return out

if __name__ == "__main__":
    if len(sys.argv) == 1:
        translate(sys.stdin)
    elif len(sys.argv) == 2:
        translate(open(sys.argv[1], "r"))
    else:
        print("Unexpected arguments")