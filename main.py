import threading
from AddressPool import *
from IPAddress import *

optiuni={
    53:1010101010
}
dictionar={
    "op":range(0,2),
    "2":range(3,4)
}
def main():
    nr=0
    val=b'100101010101010100'.decode("utf-8")
    for i in dictionar["op"]:
        print(val[i])




if __name__ == '__main__':
    main()