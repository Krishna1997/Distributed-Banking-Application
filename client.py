import socket
import sys
import json
import threading
from threading import Thread, Lock
import time
from tt import TimeTable
from block import Transaction, BlockChain, BallotNum

PID = int(sys.argv[1])
print("Process id: ", PID)

IP = "127.0.0.1"
BUFFER_SIZE = 1024
CLIENTS = []
LAMPORT = 0
BALANCE = 10
BALLOT_NUM = BallotNum()
ACCEPT_NUM = BallotNum()
ACCEPT_VAL = []
ACK_COUNT = 0
ACCEPT_COUNT = 0
MAX_ACK_NUM = BallotNum()
MAX_ACK_VAL = []
isLeader = False
transaction_log = []

PORT = 5000+PID
clientConn = {}
pidConn = {}     

def sendMessage(msg, conn):
    time.sleep(5)
    conn.sendall(msg.encode('utf-8'))

def sendLog(pid):
    # incrementLamport()
    events = []
    node = chain.get_head()
    while node is not None:
        if not hasrec(pid, node.data):
            events.append(node.data.toJSON())
        node = node.next_node
    data = {
        'clock': LAMPORT,
        'table': tt.toJSON(),
        'events': events
    }
    message = json.dumps(data)
    threading.Thread(target = sendMessage, args = (message, pidConn[pid],)).start()
    print ('Message sent to client '+str(pid))

def sendPrepare(ballotNum):
    data = {
        'type': 'prepare',
        'ballot': ballotNum.toJSON()
    }
    message = json.dumps(data)
    for client in CLIENTS:
        threading.Thread(target = sendMessage, args = (message, client,)).start()
    print ('Prepare message sent to clients')
    

def runPaxos():
    # Leader election
    message = "prepare;{};{}".format(BALLOT_NUM, PID)
    for client in CLIENTS:
        threading.Thread(target = sendMessage, args = (message, pidConn[pid],)).start()
        print ('Message sent to client '+str(pid))
    # Normal Operation    
    
    
def processInput(data):
    dataList = data.split(',')
    if dataList[0] == 'transfer':
        # Update getBalance to get balance 
        amountBefore = chain.getBalance(PID)
        if amountBefore >= int(dataList[2]) and PID != int(dataList[1]):
            transaction_log.append()
            print("SUCCESS")
            print("Balance before: $"+str(amountBefore))
            print("Balance after: $"+str(amountBefore-int(dataList[2])))
        else:
            # Run Paxos
            runPaxos()
            print("INCORRECT")
    elif dataList[0] == 'balance':
        if len(dataList) == 1:
            dataList.append(str(PID))
        print("Balance: $"+str(chain.getBalance(int(dataList[1]))))
    elif dataList[0] == 'message':
        if int(dataList[1]) != PID:
            sendLog(int(dataList[1]))
        

def acceptBallot(ballotNum):
    newBallot = False
    if ballotNum.num > ACCEPT_NUM.num:
        newBallot = True
    elif ballotNum.num == ACCEPT_NUM.num and ballotNum.pid > ACCEPT_NUM.pid:
        newBallot = True
    return newBallot
    

def processMessage(pid, data):    
    print ('Message from client ' + str(pid))
    data = json.loads(data)
    if data['type'] == 'prepare':
        ballotNum = BallotNum.load(data['ballot'])
        if acceptBallot(ballotNum):
            ACCEPT_NUM = ballotNum
            val = []
            for aval in ACCEPT_VAL:
                val.append(aval.toJSON())
            data = {
                'type': 'ack',
                'ballot': ballotNum.toJSON(),
                'accept_ballot': ACCEPT_NUM.toJSON(),
                'accept_val': val 
            }
            message = json.dumps(data)
            threading.Thread(target = sendMessage, args = (message, pidConn[pid],)).start()
            print ('Ack message sent to client '+str(pid))
            
    elif data['type'] == 'ack':
        #  check for majority and send accept to followers
        ACK_COUNT += 1
        acceptBallot = BallotNum.load(data['accept_ballot'])
        acceptVal = data['accept_val']
        if len(acceptVal) != 0 and acceptBallot.isHigher(MAX_ACK_NUM):
            MAX_ACK_NUM = acceptBallot
            MAX_ACK_VAL.clear()
            MAX_ACK_VAL = acceptVal
            
            
        if 
        data = {
            'type': 'leader_accept',
            
        }
         
    elif data['type'] == 'leader_accept':
        # do stuff and relay message to leader
        # AC
    
    elif data['type'] == 'accept':
        # do stuff and relay message to leader
        # AC
                  

                
def listenToClient(pid, conn):
    with conn:
        while True:
            try:
                data = conn.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                processMessage(pid, data)
            except socket.error:
                print ("Socket error in receiving message")
                break
        if conn in CLIENTS:
            CLIENTS.remove(conn)


def createServer(pid):
    try: 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))         
        print("socket binded to %s" %(PORT))
        s.listen(1)      
        print("socket successfully created")
    except socket.error as err: 
        print("socket creation failed with error %s" %(err)) 

    while True:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE).decode('utf-8')
        if not data:
            break
        dataList = data.split(',')
        if dataList[0] == 'pid':
            clientConn[conn] = int(dataList[1])
            pidConn[int(dataList[1])] = conn
            print('Accepted connection from client ', dataList[1])
        CLIENTS.append(conn)
        print("#clients connected: ", len(CLIENTS))
        threading.Thread(target = listenToClient,args = (int(dataList[1]),conn,)).start()


def connectToClient(pid, ip, port):
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    c_socket.connect((ip, port))
    c_socket.sendall(("pid,"+str(PID)).encode('utf-8'))
    CLIENTS.append(c_socket)
    clientConn[c_socket] = pid
    pidConn[pid] = c_socket
    threading.Thread(target = listenToClient,args = (pid,c_socket,)).start()
   
     
if __name__ == "__main__":
    # Reading the client configurations
    f = open(sys.argv[2], 'r')
    configList = f.readlines()
    config = configList[PID-1].strip('\n').split(',')
    if len(config) != 3:
        print("Incorrect configuration")
        sys.exit()
    IP = config[0]
    PORT = int(config[1])
    BALANCE = int(config[2])
    
    # Creating server to listen for connections
    server_thread = threading.Thread(target = createServer,args = (PID,)) 
    server_thread.start() 

    # Connect to existing clients
    for i in range(1, PID):
        clientConfig = configList[i-1].strip('\n').split(',')
        connectToClient(i, clientConfig[0], int(clientConfig[1]))
    print("#clients connected: ", len(CLIENTS))
    print("Balance: $"+str(BALANCE))
    
    # Listen for client inputs
    chain = BlockChain()

    while True:
        message = input("Enter transaction: ")
        processInput(message)

