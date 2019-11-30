from Message import *
from Options import *
import pprint
def main():
    message = b"01010600AABBCCDD03008000C0A864EEC0A864C1C0A864ABC0A864127C7635E2FD3D00000000000000000000416e647265692020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202067656e65726963202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200104FFFFFFA4FF0308C0A86446C0A864A3FF0604C0A86445FF15085461746142616369FF2804C0A864C7FF530103FF5404C0A864B6FF580400011940FF"
    message = message.decode("utf-8")
    m = Message(message)
    m.messageSplit()
    o = Options(m.options)
    o.optionSplit()
    o.optionDecode()
    pprint.pprint(m.__dict__, sort_dicts=False)
    pprint.pprint(o.__dict__, sort_dicts=False)





if __name__=='__main__':
    main()