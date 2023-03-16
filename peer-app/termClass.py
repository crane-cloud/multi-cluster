class TermClass:
    def __init__(self):
        self.value = 0
    
my_term = TermClass()

def increment():
    my_term.value += 1
    
def set_value( new_value):
    my_term.value = new_value