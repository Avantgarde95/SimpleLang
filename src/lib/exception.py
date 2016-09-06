''' Custom exceptions '''

# Exceptions

class Exception_base(Exception):
    ''' Base class for the exceptions. '''
    name = 'Error-general'

class Exception_syntax(Exception_base):
    ''' Exception : syntax error. '''
    name = 'Error-syntax'

class Exception_arg(Exception_base):
    ''' Exception : wrong number of arguments. '''
    name = 'Error-arg'

class Exception_type(Exception_base):
    ''' Exception : argument's type is wrong. '''
    name = 'Error-type'

class Exception_index(Exception_base):
    ''' Exception : out-of-bound error. '''
    name = 'Error-index'

class Exception_divbyzero(Exception_base):
    ''' Exception : dividing by zero. '''
    name = 'Error-divbyzero'

class Exception_lookup(Exception_base):
    ''' Exception : variable with such name doesn't exit. '''
    name = 'Error-lookup'

class Exception_user(Exception_base):
    ''' User-defined error. '''
    name = 'Error-user'
