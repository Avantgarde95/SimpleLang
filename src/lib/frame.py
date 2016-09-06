''' Definition of 'frame' and the functions related to variable
assignment.
'''

class FrameObject(object):
    ''' 'frame' object - An simple object which stores the mapping
    of variables and their names.
    '''
    def __init__(self, parent = None, map_variable = None):
        self.parent = parent

        if map_variable is None:
            self.map_variable = {}
        else:
            self.map_variable = map_variable

# ------------------------------------------------------

map_builtin = {} # built-in functions
frame_curr = FrameObject() # current working frame

def assign_builtin(name, func, num_params):
    ''' Load built-in function in the current scope. '''
    map_builtin[name] = (func, num_params)

def lookup_builtin(name):
    ''' Find out whether the built-in function with such name exists. '''
    return map_builtin.get(name, (None, None))

def assign_variable(name, obj):
    ''' Map given object to the name in the current scope. '''
    frame_curr.map_variable[name] = obj

def lookup_variable(name):
    ''' Lookup the name in the current scope, and return the matching
    object. If it doesn't exist, return None.
    '''
    return frame_curr.map_variable.get(name, None)

def wind_frame():
    ''' Generate a new child frame and import variables from the parent
    frame. '''
    global frame_curr

    frame_curr = FrameObject(
        parent = frame_curr,
        map_variable = frame_curr.map_variable.copy()
    )

def unwind_frame():
    ''' Return to the parent frame. '''
    global frame_curr

    frame_curr = frame_curr.parent

# ------------------------------------------------------

def test():
    print '[Frame test]'

    print '\n<Frame id : %d>' % id(frame_curr)
    print 'Assigned A -> 3, B -> 2.'
    assign_variable('A', 3)
    assign_variable('B', 2)
    print 'A =', lookup_variable('A'), 'B =', lookup_variable('B')
    
    print '\nAdding a child frame...'
    wind_frame()
    
    print '\n<Frame id : %d>' % id(frame_curr)
    print 'Assigned A -> 5.'
    assign_variable('A', 5)
    print 'A =', lookup_variable('A'), 'B =', lookup_variable('B')

    print '\nReturning to the parent frame...'
    unwind_frame()
    
    print '\n<Frame id : %d>' % id(frame_curr)
    print 'A =', lookup_variable('A'), 'B =', lookup_variable('B')

if __name__ == '__main__':
    test()
