import socket
import threading
import  SenderHandler
import  AddressPool
import Message


def com_thread(conn,addr,pool,lock):
    messageHandler = SenderHandler.SenderHandler(conn, addr, pool,lock)
    xid = 0
    while 1:
        data = conn.recv(4096)
        if data:
            data = data.decode("utf-8")
            message = Message.Message(data)
            message.messageSplit()
            if xid == 0:
                xid = message.xid
            elif xid == message.xid:
                messageHandler.handle(message)
            else:
                break
        else:
            break

def main():
    #creare obiect de tip socket
    pool = AddressPool.AddressPool('192.168.0.0','255.255.0.0')
    lock = threading.Lock()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 5000))
    s.listen(10)
    print('Asteapta conexiuni ...')
    while 1:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            break
        print('S-a conectat this motherfucker:' + str(addr))
        try:
            threading.Thread(target=com_thread, args=(conn, addr, pool, lock)).start()
        except:
            print('Oroare')

def test():
    print(b'010101'.decode("utf-8"))


if __name__=='__main__':
    main()