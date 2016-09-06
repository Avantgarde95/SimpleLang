''' Lexical analysis / Parsing using PLY '''

import ply.lex as lex
import ply.yacc as yacc
from exception import Exception_syntax
from object import CodeObject

tokens = ['NAME', 'INT', 'FLOAT', 'STR']
literals = '$()'

map_escape = {
    '\\\\' : '\\',
    '\\n' : '\n',
    '\\r' : '\r',
    '\\0' : '\0',
    '\\t' : '\t',
    '\\a' : '\a',
    '\\b' : '\b',
    '\\\'' : '\'',
    '\\\"' : '\"'
}

chars_escape = map_escape.keys()

# --------------------------------------------------------
# lexer

t_ignore = ' \n\t'

def t_error(t):
    raise Exception_syntax('Invalid character \'%s\'' % t.value[0])

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_FLOAT(t):
    r'[-+]?\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'[-+]?\d+'
    t.value = int(t.value)
    return t

def t_STR(t):
    r'("(\\"|[^"])*")|(\'(\\\'|[^\'])*\')'
    value_temp = t.value[1:-1]

    for ch in chars_escape:
        value_temp = value_temp.replace(ch, map_escape[ch])

    t.value = value_temp

    return t

def t_COMMENT(t):
    r'\#.*'
    pass

lex.lex()

# --------------------------------------------------------
# parser

def p_error(p):
    raise Exception_syntax('Wrong syntax.')

def p_expr(p):
    ''' expr : const
             | name
             | list
             | eval
    '''
    p[0] = p[1]

def p_eval(p):
    ''' eval : '$' expr '''
    p[0] = CodeObject('eval', p[2])

def p_list_empty(p):
    ''' list : '(' ')' '''
    p[0] = CodeObject('list', [])

def p_list_nonempty(p):
    ''' list : '(' listbody ')' '''
    p[0] = CodeObject('list', p[2])

def p_listbody_single(p):
    ''' listbody : expr '''
    p[0] = [p[1]]

def p_listbody_multiple(p):
    ''' listbody : listbody expr '''
    p[0] = p[1] + [p[2]]

def p_name(p):
    ''' name : NAME '''
    p[0] = CodeObject('name', p[1])

def p_int(p):
    ''' const : INT '''
    p[0] = CodeObject('int', p[1])

def p_float(p):
    ''' const : FLOAT '''
    p[0] = CodeObject('float', p[1])

def p_str(p):
    ''' const : STR '''
    p[0] = CodeObject('str', p[1])

yacc.yacc(debug = False)

# --------------------------------------------------------
# main code

def parse(src):
    return yacc.parse('$(main (%s\n))' % src)

# --------------------------------------------------------

def test():
    from pprint import pprint

    print '[Parser test]'

    src = '$(let A 1)\n'\
            '$(let b 2)\n'\
            '$(print $(add $a $b))'

    print '\n1) Source code\n'
    print src

    print '\n2) Lexer\n'
    lex.input(src)

    while 1:
        t = lex.token()

        if t: 
            if t.type in literals:
                print 'Literal |', t.value
            else:
                print '%7s' % t.type, '|', t.value
        else:
            break

    print '\n3) Parser\n'
    
    def to_tuple(code):
        if isinstance(code.arg, CodeObject):
            return (code.op, to_tuple(code.arg))
        elif isinstance(code.arg, list):
            return (code.op, map(to_tuple, code.arg))
        else:
            return (code.op, code.arg)

    pprint(to_tuple(parse(src)))

if __name__ == '__main__':
    test()
