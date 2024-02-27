import ply.lex as lex
import ply.yacc as yacc

tokens = ('QUERY', 'COLON', 'DOT', 'LPAREN', 'RPAREN', 'STR', 'ID', 'LBRAC', 'RBRAC', 'NUM', 'COMP', 'EQ', 'PLUS')

t_QUERY = r'\?'
t_COLON = r':'
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_STR = r'"""[^"]+"""'
t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_LBRAC = r'\['
t_RBRAC = r'\]'
t_NUM = r'\d+'
t_COMP = r'[<>]=?'
t_EQ = r'[=!]='
t_PLUS = r'\+'

t_ignore = ' \t'

def p_mapping(p):
    '''mapping : term_c
               | ternary_c'''
    p[0] = "'" + p[1] + "'"

def p_string(p):
    'string : STR'
    p[0] = p[1][2:-2]

def p_array(p):
    'array : ID LBRAC NUM RBRAC'
    p[0] = p[1] + p[2] + p[3] + p[4]

def p_func(p):
    '''func : ID LPAREN term_c RPAREN
            | ID LPAREN func RPAREN
            | ID LPAREN RPAREN'''
    if len(p) > 4:
        p[0] = p[1] + p[2] + p[3] + p[4]
    else:
        p[0] = p[1] + p[2] + p[3]

def p_term(p):
    '''term : term_c
            | term PLUS term_c'''

def p_term_s(p):
    '''term_s : array
              | func
              | string
              | ID
              | NUM'''
    p[0] = p[1]

def p_term_c(p):
    '''term_c : term_s DOT array
              | term_s DOT func
              | term_s DOT ID
              | term_s DOT term_c
              | term_s'''
    if len(p) > 2:
        p[0] = p[1] + p[2] + p[3]
    else:
        p[0] = p[1]

def p_ternary_s(p):
    'ternary_s : bool QUERY term_c COLON term_c'
    p[0] = "if " + p[1] + " display " + p[3] + "\notherwise display " + p[5]

def p_ternary_c(p):
    '''ternary_c : ternary_c1
                 | ternary_c2
                 | ternary_s'''
    p[0] = p[1]

def p_ternary_c1(p):
    '''ternary_c1 : bool QUERY ternary_c COLON term_c
                  | bool QUERY ternary_s COLON term_c'''
    sub = '\t' + '\n\t'.join(p[3].split('\n'))
    p[0] = "if " + p[1] + "\n" + sub + "\notherwise display " + p[5]

def p_ternary_c2(p):
    '''ternary_c2 : bool QUERY term_c COLON ternary_c2
                  | bool QUERY term_c COLON ternary_s'''
    p[0] = "if " + p[1] + " display " + p[3] + "\n" + p[5]

def p_bool(p):
    '''bool : term_c COMP term_c
            | term_c EQ term_c
            | term_c'''
    if len(p) > 2:
        p[0] = p[1] + p[2] + p[3]
    else:
        p[0] = p[1]

def parse():
#    data = 'diagnosis_detail.diagnosistype == """Primary""" ? """Principal Diagnosis""":diagnosis_detail.diagnosistype == """Admit""" ?"""Admitting Diagnosis""" : """Other"""'
    data = 'x==y ? y==z ? y==z ? a : b : b : c'
    l = lex.lex()
    l.input(data)

    while True:
        tok = l.token()

        if not tok:
            break

        print(tok)

    y = yacc.yacc()
    print(y.parse(data))

if __name__ == "__main__":
    parse()