''' Definition of the objects used in the language. '''

import frame
from exception import Exception_lookup, Exception_arg, Exception_type
from interrupt import Interrupt_return

class IntObject(object):
    ''' Integer object. '''
    def __init__(self, value):
        self.value = value
        self.type = 'int'

    def __str__(self):
        return '%d' % self.value

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return IntObject(self.value)

    def evaluate(self):
        return self

# -----------------------------------------------------------

class FloatObject(object):
    ''' Floating-point object. '''
    def __init__(self, value):
        self.value = value
        self.type = 'float'

    def __str__(self):
        value_raw = '%f' % self.value

        if value_raw[-1] == '0':
            value_strip = value_raw.rstrip('0')

            if value_strip[-1] == '.':
                return value_strip + '0'
            else:
                return value_strip
        
        return value_raw

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return FloatObject(self.value)

    def evaluate(self):
        return self

# -----------------------------------------------------------

class StrObject(object):
    ''' String object. '''
    def __init__(self, value):
        self.value = value
        self.type = 'str'

    def __str__(self):
        return '%s' % self.value

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return StrObject(self.value)

    def evaluate(self):
        return self

# -----------------------------------------------------------

class ListObject(object):
    ''' List object. '''
    def __init__(self, value):
        self.value = [e.copy() for e in value]
        self.type = 'list'

    def __str__(self):
        return '(%s)' % ' '.join(str(e) for e in self.value)

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return ListObject([e.copy() for e in self.value])

    def evaluate(self):
        return self

# -----------------------------------------------------------

class NameObject(object):
    ''' Name (= Identifier) object. '''
    def __init__(self, value):
        self.value = value
        self.type = 'name'

    def __str__(self):
        return '<Name %s>' % self.value

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return NameObject(self.value)

    def evaluate(self):
        return self

# -----------------------------------------------------------

class FuncObject(object):
    ''' Function object. '''
    def __init__(self, params, codes):
        self.value = {'params' : params, 'codes' : codes}
        self.params = params
        self.codes = codes
        self.type = 'func'

    def __str__(self):
        names_params = ['var_%d' % (i + 1)
                        for i in xrange(len(self.params))]
        return '<Func (%s)>' % ' '.join(names_params)

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return FuncObject(self.params[:], self.codes[:])

    def evaluate(self):
        return self

# -----------------------------------------------------------

class CodeObject(object):
    ''' Code object. '''
    def __init__(self, op, arg):
        self.value = {'op' : op, 'arg' : arg}
        self.op = op
        self.arg = arg
        self.type = 'code'

    def __str__(self):
        return '<Code %s : %s>' % (self.op, self.arg)

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return CodeObject(self.op, self.arg)

    def evaluate(self):
        op = self.op

        # convert code object to 'real' value
        if op == 'int':
            return IntObject(self.arg)
        elif op == 'float':
            return FloatObject(self.arg)
        elif op == 'str':
            return StrObject(self.arg)
        elif op == 'list':
            return ListObject(self.arg)
        elif op == 'name':
            return NameObject(self.arg)

        # call 'evaluator' ('$' operator)
        elif op == 'eval':
            code_target = self.arg

            # $(name) -> variable lookup
            if code_target.op == 'name':
                var_name = code_target.arg
                var_value = frame.lookup_variable(var_name)

                if var_value is None:
                    raise Exception_lookup(
                        'Failed to find the variable with the name'\
                        ' \'%s\'.' % var_name)
                else:
                    return var_value

            # $(list) -> function call
            elif code_target.op == 'list':
                if not code_target.arg:
                    raise Exception_type(
                        'Can\'t evaluate an empty list.')

                func_request = code_target.arg[0].evaluate()
                args = code_target.arg[1:]
                num_args = len(args)

                if func_request.type == 'name':
                    # 1) lookup user-defined functions first
                    func_name = func_request.value
                    func = frame.lookup_variable(func_name)

                    if func is None:
                        # 2) lookup built-in functions second
                        func, num_params = frame.lookup_builtin(func_name)
                        
                        if func is not None:
                            if num_args != num_params:
                                raise Exception_arg(
                                    'Function \'%s\' expected %d'\
                                    ' arguments, but it got %d.'\
                                    % (func_name, num_params, num_args))

                            obj_return = func(*args)

                            if obj_return is None:
                                return IntObject(0)
                            else:
                                return obj_return

                        # 3) else... -> No way to call that function
                        else:
                            raise Exception_lookup(
                                'Function \'%s\' doesn\'t exist.'\
                                % func_name)
                else:
                    func_name = 'Unnamed'
                    func = func_request

                if func.type != 'func':
                    raise Exception_type('Cannot call \'%s\'.'\
                                         % func.type)

                # call user-defined function
                # 1) set a new frame ('winding')
                # 2) push the arguments
                # 3) eval. the codes until Interrupt_return is raised
                # 4) return to the parent frame ('unwinding')
                # 5) get the return value
                #    (obj. passed by Interrupt_return or
                #     the value of the last code)
                codes = func.codes
                params, num_params = func.params, len(func.params)

                if num_args != num_params:
                    raise Exception_arg(
                        'Function \'%s\' expected %d'\
                        ' arguments, but it got %d.'\
                        % (func_name, num_params, num_args))

                frame.wind_frame()

                for i in xrange(num_args):
                    frame.assign_variable(params[i], args[i].evaluate())

                try:
                    for c in codes:
                        obj_return = c.evaluate()
                except Interrupt_return as e:
                    obj_return = e.obj_return

                frame.unwind_frame()

                return obj_return

            # $(else) -> return itself
            else:
                return code_target.evaluate()

        # what should I do???
        else:
            pass

# -----------------------------------------------------------

def test():
    print '[Object test]'

    # ---------------------------------------------
    # object initialization

    print '\n1) Make some objects\n'
    
    samples = [
        IntObject(-3),
        FloatObject(3.1415),
        StrObject('Hello, world!'),
        ListObject([IntObject(3), IntObject(4), ListObject([])]),
        NameObject('get_it'),
        FuncObject(['a', 'b'], []),
        CodeObject('float', 3.14)
    ]

    for obj in samples:
        print '%5s' % obj.type, '-', obj, '/', obj.value

    # ---------------------------------------------
    # built-in function

    print '\n2) Built-in function\n'

    def func_foo(arg_1, arg_2):
        obj_1 = arg_1.evaluate()
        obj_2 = arg_2.evaluate()

        if obj_1.type == obj_2.type:
            return IntObject(1)
        else:
            return IntObject(0)

    frame.assign_builtin('foo', func_foo, 2)
    
    print 'foo : a, b -> (1 if (a\'s type) == (b\'s type), otherwise 0)'

    code_1 = CodeObject(
        'eval',
        CodeObject(
            'list', [CodeObject('name', 'foo'),
                     CodeObject('int', 3),
                     CodeObject('int', 2)]
        )
    )
    
    code_2 = CodeObject(
        'eval',
        CodeObject(
            'list', [CodeObject('name', 'foo'),
                     CodeObject('int', 3),
                     CodeObject('float', 2.0)]
        )
    )
    
    print 'ex) $(foo 3 2) ->', code_1.evaluate()
    print 'ex) $(foo 3 2.0) ->', code_2.evaluate()

    # ---------------------------------------------
    # user-defined function

    print '\n3) User-defined function\n'

    func = FuncObject(
        ['a', 'b'],
        [CodeObject(
            'eval',
            CodeObject(
                'list', [CodeObject('name', 'foo'),
                         CodeObject('eval', CodeObject('name', 'a')),
                         CodeObject('eval', CodeObject('name', 'b'))]
            )
        )]
    )

    code_1 = CodeObject(
        'eval',
        CodeObject(
            'list', [func,
                     CodeObject('int', 3),
                     CodeObject('int', 2)]
        )
    )

    code_2 = CodeObject(
        'eval',
        CodeObject(
            'list', [func,
                     CodeObject('int', 3),
                     CodeObject('float', 2.0)]
        )
    )

    print 'bar : a, b -> $(foo $a $b)'
    print 'ex) $(bar 3 2) ->', code_1.evaluate()
    print 'ex) $(bar 3 2.0) ->', code_2.evaluate()

if __name__ == '__main__':
    test()
