''' 'Interrupts' - Special exceptions used for flow control '''

class Interrupt_base(Exception):
    ''' Base class for the interrupts '''
    pass

class Interrupt_return(Interrupt_base):
    ''' Interrupt for 'return'. '''
    def __init__(self, obj_return):
        self.obj_return = obj_return

class Interrupt_loop(Interrupt_base):
    ''' Interrupt for 'for', 'continue'. ''' 
    def __init__(self, status):
        self.status = status
