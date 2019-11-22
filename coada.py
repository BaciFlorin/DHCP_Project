
class coada():
    def __init__(self):
        self.vector=[]

    def push(self,_element):
        self.vector.append(_element)

    def get(self):
        if len(self.vector)!=0:
            return self.vector.pop(1)

    def isEmpty(self):
        if len(self.vector)==0:
            return True
        else:
            return False

