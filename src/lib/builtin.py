''' Define & load built-in functions '''
import sys
import inspect
import frame
from object import *
from exception import *
from interrupt import *

def load():
    ''' Store the built-in functions to the current scope with
    proper names.
    * Each function should start with 'func_'.
      (ex. def func_print: ... -> $(print ...))
    '''
    members = inspect.getmembers(sys.modules[__name__])

    for name, obj in members:
        if inspect.isfunction(obj) and name.startswith('func_'):
            num_params = len(inspect.getargspec(obj).args)
            frame.assign_builtin(name[5:], obj, num_params)

# flag for handling newline in REPL
# ... becomes True when 'print' or 'output' is called at least once
called_print = False

# flag for preventing user to call 'main'
# ... becomes True when 'main' is called at least once
called_main = False

# --------------------------------------------------
# internal functions

def read_string():
    return sys.stdin.readline().rstrip('\n')

def print_string(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def to_boolean(obj):
    if obj.type == 'int' and obj.value == 0:
        return False
    else:
        return True

def eval_recur(obj):
    if obj.type == 'list':
        return ListObject([eval_recur(item) for item in obj.value])
    elif obj.type == 'code':
        return eval_recur(obj.evaluate())
    else:
        return obj

# --------------------------------------------------
# built-in functions
# ... They should start with 'func_'
# ... ex) $(print 3) -> def func_print(arg): ...

# -------------------------------
# main entry

def func_main(arg):
    global called_main

    if called_main:
        raise Exception_base('\'main\' can\'t be called by the user.')

    called_main = True
    codes = arg.evaluate()

    for c in codes.value:
        try:
            c.evaluate()
        except Interrupt_base:
            pass

# -------------------------------
# eager evaluation

def func_early(arg):
    obj = arg.evaluate()
    return eval_recur(obj)

# -------------------------------
# terminate

def func_exit(arg):
    status = arg.evaluate()

    if status.type != 'int':
        raise Exception_type('Argument of \'exit\' should be \'int\','\
                             ' not \'%s\'.' % status.type)

    if status.value >= 0:
        sys.exit(status.value)
    else:
        sys.exit(max(status.value, 0))

def func_error(arg):
    msg = arg.evaluate()

    if msg.type != 'str':
        raise Exception_type('Argument of \'error\' should be \'str\','\
                             ' not \'%s\'.' % msg.type)

    raise Exception_user(msg.value)

# -------------------------------
# I / O

def func_input(arg):
    msg = arg.evaluate()

    if msg.type != 'str':
        raise Exception_type('Argument of \'input\' should be \'str\','\
                             ' not \'%s\'.' % msg.type)

    print_string(msg.value)

    return StrObject(read_string())

def func_output(arg):
    global called_print

    obj = arg.evaluate()
    called_print = True
    print_string(str(obj))

def func_print(arg):
    global called_print

    obj = arg.evaluate()
    called_print = True
    print_string(str(eval_recur(obj)))

# -------------------------------
# conditional

def func_if(arg_1, arg_2):
    cond, codes = arg_1.evaluate(), arg_2.evaluate()

    if codes.type != 'list':
        raise Exception_type('Second argument of \'if\' should be'\
                             ' \'list\', not \'%s\'.' % codes.type)
    if to_boolean(cond) and codes.value:
        return [c.evaluate() for c in codes.value][-1]

def func_if_else(arg_1, arg_2, arg_3):
    cond = arg_1.evaluate()
    codes_true, codes_false = arg_2.evaluate(), arg_3.evaluate()

    if codes_true.type != 'list':
        raise Exception_type('Second argument of \'if_else\' should be'\
                             ' \'list\', not \'%s\'.' % codes_true.type)
    
    if codes_false.type != 'list':
        raise Exception_type('Third argument of \'if_else\' should be'\
                             ' \'list\', not \'%s\'.' % codes_false.type)

    if to_boolean(cond):
        if codes_true.value:
            return [c.evaluate() for c in codes_true.value][-1]
    else:
        if codes_false.value:
            return [c.evaluate() for c in codes_false.value][-1]

# -------------------------------
# looping

def func_for(arg_1, arg_2, arg_3):
    var_name, var_range = arg_1.evaluate(), arg_2.evaluate()
    codes = arg_3.evaluate()

    if var_name.type != 'name':
        raise Exception_type('First argument of \'for\' should be'\
                             ' \'name\', not \'%s\'.' % var.type)

    if var_range.type != 'list':
        raise Exception_type('Second argument of \'for\' should be'\
                             ' \'list\', not \'%s\'.' % var_range.type)
    
    if codes.type != 'list':
        raise Exception_type('Third argument of \'for\' should be'\
                             ' \'list\', not \'%s\'.' % codes.type)

    for item in var_range.value:
        status = 'normal'
        frame.assign_variable(var_name.value, item)
        
        for c in codes.value:    
            try:
                c.evaluate()
            except Interrupt_loop as e:
                status = e.status
                break

        if status == 'break':
            break
        elif status == 'continue':
            continue
        else:
            pass

def func_while(arg_1, arg_2):
    codes = arg_2.evaluate()

    if codes.type != 'list':
        raise Exception_type('Second argument of \'while\' should be'\
                             ' \'list\', not \'%s\'.' % codes.type)

    while to_boolean(arg_1.evaluate()):
        status = 'normal'
        
        for c in codes.value:
            try:
                c.evaluate()
            except Interrupt_loop as e:
                status = e.status
                break
        
        if status == 'break':
            break
        elif status == 'continue':
            continue
        else:
            pass

# -------------------------------
# flow control

def func_return(arg):
    raise Interrupt_return(arg.evaluate())

def func_break():
    raise Interrupt_loop('break')

def func_continue():
    raise Interrupt_loop('continue')

# -------------------------------
# assignment

def func_let(arg_1, arg_2):
    name, obj = arg_1.evaluate(), arg_2.evaluate()

    if name.type != 'name':
        raise Exception_type('First argument of \'let\' should be'\
                             ' \'name\', not \'%s\'.' % name.type)

    # assign obj.copy() instead of obj, to force passing by value
    frame.assign_variable(name.value, obj.copy())
    return obj

# -------------------------------
# lambda

def func_func(arg_1, arg_2):
    params_raw, codes_raw = arg_1.evaluate(), arg_2.evaluate()

    if params_raw.type != 'list':
        raise Exception_type('First argument of \'func\' should be'\
                             ' \'list\', not \'%s\'.' % name.type)

    if codes_raw.type != 'list':
        raise Exception_type('Second argument of \'func\' should be'\
                             ' \'list\', not \'%s\'.' % codes_raw.type)

    params, codes = [], codes_raw.value

    for p_raw in params_raw.value:
        p = p_raw.evaluate()

        if p.type == 'name':
            params.append(p.value)
        else:
            raise Exception_type('Each item of the first argument of'\
                                 ' \'func\' should be \'name\','\
                                 ' not \'%s\'.' % p.type)

    return FuncObject(params, codes)

# -------------------------------
# type check

def func_type(arg):
    return StrObject(arg.evaluate().type)

def func_is_type(arg_1, arg_2):
    obj, name = arg_1.evaluate(), arg_2.evaluate()

    if name.type != 'str':
        raise Exception_type('Second argument of \'is_type\' should be'
                             ' \'str\', not \'%s\'.' % name.type)

    if name.value == 'any':
        return IntObject(1)

    if obj.type == name.value:
        return IntObject(1)

    if obj.type in ('int', 'float') and name.value == 'num':
        return IntObject(1)
    
    if obj.type in ('str', 'list') and name.value == 'seq':
        return IntObject(1)

    return IntObject(0)

# -------------------------------
# type conversion

def func_to_int(arg):
    obj = arg.evaluate()

    if obj.type == 'int':
        return obj.copy()
    elif obj.type == 'float':
        return IntObject(int(obj.value))
    elif obj.type == 'str':
        try:
            v = int(obj.value)
        except ValueError:
            raise Exception_type('Failed to convert the string \'%s\''\
                                 ' to integer.' % obj.value)
        return IntObject(v)
    else:
        raise Exception_type('Can\'t convert \'%s\' to \'int\'.'\
                             % obj.type)

def func_to_float(arg):
    obj = arg.evaluate()

    if obj.type == 'int':
        return FloatObject(float(obj.value))
    elif obj.type == 'float':
        return obj.copy()
    elif obj.type == 'str':
        try:
            v = float(obj.value)
        except ValueError:
            raise Exception_type('Failed to convert the string \'%s\''\
                                 ' to floating-point number.'\
                                 % obj.value)
        return FloatObject(v)
    else:
        raise Exception_type('Can\'t convert \'%s\' to \'float\'.'\
                             % obj.type)

def func_to_str(arg):
    obj = arg.evaluate()
    
    if obj.type in ('int', 'float'):
        return StrObject(str(obj.value))
    elif obj.type == 'str':
        return obj.copy()
    else:
        return StrObject(str(obj))

def func_to_list(arg):
    obj = arg.evaluate()

    if obj.type == 'str':
        return ListObject([StrObject(c) for c in obj.value])
    elif obj.type == 'list':
        return obj.copy()
    else:
        raise Exception_type('Can\'t convert \'%s\' to \'list\'.'\
                             % obj.type)

# -------------------------------
# comparison

def func_geq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()
    
    if (left.type in ('int', 'float') and
        right.type in ('int', 'float')):
        if left.value >= right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'str' and right.type == 'str':
        if left.value >= right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    else:
        raise Exception_type('Can\'t find whether \'%s\' >= \'%s\'.'\
                             % (left.type, right.type))

def func_gnq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()
    
    if (left.type in ('int', 'float') and
        right.type in ('int', 'float')):
        if left.value > right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'str' and right.type == 'str':
        if left.value > right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    else:
        raise Exception_type('Can\'t find whether \'%s\' > \'%s\'.'\
                             % (left.type, right.type))

def func_leq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()
    
    if (left.type in ('int', 'float') and
        right.type in ('int', 'float')):
        if left.value <= right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'str' and right.type == 'str':
        if left.value <= right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    else:
        raise Exception_type('Can\'t find whether \'%s\' <= \'%s\'.'\
                             % (left.type, right.type))

def func_lnq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if (left.type in ('int', 'float') and
        right.type in ('int', 'float')):
        if left.value < right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'str' and right.type == 'str':
        if left.value < right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    else:
        raise Exception_type('Can\'t find whether \'%s\' < \'%s\'.'\
                             % (left.type, right.type))

def func_eq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()
    
    if left.type != right.type:
        return IntObject(0)

    if left.type in ('int', 'float', 'str', 'name'):
        if left.value == right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'list':
        for i in xrange(len(left.value)):
            if not to_boolean(func_eq(left.value[i], right.value[i])):
                return IntObject(0)

        return IntObject(1)
    else:
        return IntObject(0)

def func_neq(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()
    
    if left.type != right.type:
        return IntObject(1)

    if left.type in ('int', 'float', 'str', 'name'):
        if left.value != right.value:
            return IntObject(1)
        else:
            return IntObject(0)
    elif left.type == 'list':
        for i in xrange(len(left.value)):
            if not to_boolean(func_eq(left.value[i], right.value[i])):
                return IntObject(1)

        return IntObject(0)
    else:
        return IntObject(1)

# -------------------------------
# arithmetic

def func_add(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if left.type == 'int' and right.type == 'int':
        return IntObject(left.value + right.value)

    if (left.type in ('int', 'float')
        and right.type in ('int', 'float')):
        return FloatObject(left.value + right.value)

    if left.type == 'str' and right.type == 'str':
        return StrObject(left.value + right.value)

    if left.type == 'list' and right.type == 'list':
        return ListObject(left.value + right.value)

    raise Exception_type('Can\'t \'add\' \'%s\' and \'%s\'.'\
                         % (left.type, right.type))

def func_sub(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if left.type == 'int' and right.type == 'int':
        return IntObject(left.value - right.value)

    if (left.type in ('int', 'float')
        and right.type in ('int', 'float')):
        return FloatObject(left.value - right.value)

    raise Exception_type('Can\'t \'subtract\' \'%s\' from \'%s\'.'\
                         % (right.type, left.type))

def func_mul(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if left.type == 'int' and right.type == 'int':
        return IntObject(left.value * right.value)

    if (left.type in ('int', 'float')
        and right.type in ('int', 'float')):
        return FloatObject(left.value * right.value)

    if (left.type, right.type) in (('str', 'int'), ('int', 'str')):
        return StrObject(left.value * right.value)
    
    if (left.type, right.type) in (('list', 'int'), ('int', 'list')):
        return ListObject(left.value * right.value)

    raise Exception_type('Can\'t \'multiply\' \'%s\' and \'%s\'.'\
                         % (left.type, right.type))

def func_div(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if left.type == 'int' and right.type == 'int':
        if right.value == 0:
            raise Exception_divbyzero('Dividing by zero is illegal.')
        else:
            return IntObject(left.value / right.value)

    if (left.type in ('int', 'float')
        and right.type in ('int', 'float')):
        if right.value == 0:
            raise Exception_divbyzero('Dividing by zero is illegal.')
        else:
            return FloatObject(left.value / right.value)

    raise Exception_type('Can\'t \'divide\' \'%s\' by \'%s\'.'\
                         % (left.type, right.type))

def func_mod(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if left.type != 'int':
        raise Exception_type('First argument of \'mod\' should be'\
                             ' \'int\', not \'%s\'.' % left.type)

    if right.type != 'int':
        raise Exception_type('Second argument of \'mod\' should be'\
                             ' \'int\', not \'%s\'.' % right.type)

    return IntObject(left.value % right.value)

def func_neg(arg):
    obj = arg.evaluate()

    if obj.type == 'int':
        return IntObject(-obj.value)
    elif obj.type == 'float':
        return IntObject(-obj.value)
    else:
        raise Exception_type('Argument of \'neg\' should be \'int\''\
                             ' or \'float\', not \'%s\'.' % obj.type)

# -------------------------------
# Logical

def func_and(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if to_boolean(left) and to_boolean(right):
        return IntObject(1)
    else:
        return IntObject(0)

def func_or(arg_1, arg_2):
    left, right = arg_1.evaluate(), arg_2.evaluate()

    if to_boolean(left) or to_boolean(right):
        return IntObject(1)
    else:
        return IntObject(0)

def func_not(arg):
    obj = arg.evaluate()

    if to_boolean(obj):
        return IntObject(0)
    else:
        return IntObject(1)

# -------------------------------
# Length

def func_len(arg):
    obj = arg.evaluate()

    if obj.type == 'str':
        return IntObject(len(obj.value))
    elif obj.type == 'list':
        return IntObject(len(obj.value))
    else:
        raise Exception_type('Argument of \'len\' should be \'str\''\
                             ' or \'list\', not \'%s\'.' % obj.type)

# -------------------------------
# Range

def func_range(arg_1, arg_2, arg_3):
    start, end = arg_1.evaluate(), arg_2.evaluate()
    diff = arg_3.evaluate()

    if start.type != 'int':
        raise Exception_type('First argument of \'range\' shoud be'\
                             ' \'int\', not \'%s\'.' % start.type)
    
    if end.type != 'int':
        raise Exception_type('Second argument of \'range\' shoud be'\
                             ' \'int\', not \'%s\'.' % end.type)
    
    if diff.type != 'int':
        raise Exception_type('Third argument of \'range\' shoud be'\
                             ' \'int\', not \'%s\'.' % diff.type)

    if diff.value == 0:
        raise Exception_type('Third argument of \'range\' should be'\
                             ' nonzero.')

    return ListObject([IntObject(e) for e in range(
        start.value, end.value, diff.value)])

# -------------------------------
# Indexing

def func_get(arg_1, arg_2):
    seq, index = arg_1.evaluate(), arg_2.evaluate()

    if seq.type not in ('str', 'list'):
        raise Exception_type('First argument of \'get\' should be'\
                             ' \'str\' or \'list\', not \'%s\'.'\
                             % seq.type)

    if index.type != 'int':
        raise Exception_type('Second argument of \'get\' should be'\
                             ' \'int\', not \'%s\'.' % index.type)

    try:
        v = seq.value[index.value]
    except IndexError:
        raise Exception_index('Can\'t \'get\' %dth item of \'%s\' whose'\
                              ' length is %d.'\
                              % (index.value, seq.type, len(seq.value)))

    if seq.type == 'str':
        return StrObject(v)
    else:
        return v.evaluate()

def func_set(arg_1, arg_2, arg_3):
    seq, index = arg_1.evaluate(), arg_2.evaluate()
    obj = arg_3.evaluate()
    
    if seq.type not in ('str', 'list'):
        raise Exception_type('First argument of \'set\' should be'\
                             ' \'str\' or \'list\', not \'%s\'.'\
                             % seq.type)

    if index.type != 'int':
        raise Exception_type('Second argument of \'set\' should be'\
                             ' \'int\', not \'%s\'.' % index.type)

    try:
        v = seq.value[index.value]
    except IndexError:
        raise Exception_index('Can\'t \'set\' %dth item of \'%s\' whose'\
                              ' length is %d.'\
                              % (index.value, seq.type, len(seq.value)))

    if seq.type == 'str':
        if obj.type == 'str':
            if len(obj.value) == 1:
                # make the index positive
                index_pos = index.value % len(seq.value)

                value_new = seq.value[:index_pos] + obj.value\
                        + seq.value[index_pos+1:]

                return StrObject(value_new)
            else:
                raise Exception_type('For the strings, length of the'\
                                     'third argument of \'set\' should'\
                                     'be 1.')
        else:
            raise Exception_type('For the strings, third argument of'\
                                 ' \'set\' should be \'str\', not'\
                                 ' \'%s\'.' % obj.type)
    else:
        index_pos = index.value % len(seq.value)

        value_new = seq.value[:index_pos] + [obj]\
                + seq.value[index_pos+1:]

        return ListObject(value_new)

def func_slice(arg_1, arg_2, arg_3, arg_4):
    seq = arg_1.evaluate()
    start, end = arg_2.evaluate(), arg_3.evaluate()
    diff = arg_4.evaluate()

    if seq.type not in ('str', 'list'):
        raise Exception_type('First argument of \'slice\' should be'\
                             ' \'str\' or \'list\', not \'%s\'.'\
                             % seq.type)

    if start.type != 'int':
        raise Exception_type('Second argument of \'slice\' should be'\
                             ' \'int\', not \'%s\'.' % start.type)
    
    if end.type != 'int':
        raise Exception_type('Third argument of \'slice\' should be'\
                             ' \'int\', not \'%s\'.' % end.type)
    
    if diff.type != 'int':
        raise Exception_type('Fourth argument of \'slice\' should be'\
                             ' \'int\', not \'%s\'.' % diff.type)

    if diff.value == 0:
        raise Exception_type('Fourth argument of \'slice\' should be'\
                             ' nonzero.')

    if seq.type == 'str':
        return StrObject(seq.value[start.value:end.value:diff.value])
    else:
        return ListObject(seq.value[start.value:end.value:diff.value])

# -------------------------------
# Copy
# (Is this function really needed??)

def func_copy(arg):
    obj = arg.evaluate()
    return obj.copy()
