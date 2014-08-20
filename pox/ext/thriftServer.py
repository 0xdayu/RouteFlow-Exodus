import sys
sys.path.append('./gen-py')
 
from route import GetRouteEntry 
from route.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
 
import socket

class GetRouteEntryHandler:
    def __init__(self):
        t = ("1","1.2.3.4","32","6")
        q = ("1","1.2.3.4","32","5")
        self.RouteTable = []
        self.RouteTable.append(q)       
        self.RouteTable.append(t)   
        self.log = {}

    def get(self, req):
        if len(req.arguments) != 4:
            reply = QueryReply()
            reply.result = None
            reply.exception_code = "1"
            reply.exception_message = "Not Enough Arguments"
            return reply

        token = req.arguments
        
        req_swid = token[0]
        req_addr = token[1]
        req_mask = token[2]
        req_outport = token[3]

        reply = QueryReply()
        
        rt_result = filter(lambda (a,b,c,d): \
                    (isVal(req_swid) or a == req_swid) and \
                    (isVal(req_addr) or b == req_addr) and \
                    (isVal(req_mask) or c == req_mask) and \
                    (isVal(req_outport) or d == req_outport),
                    self.RouteTable)
    
        result = []

        for a,b,c,d in rt_result:
            temp = [a,b,c,d]
            result.append(temp)

        reply.result = result
        
        return reply

def isVal(a):
    b = a.replace(".","")
    return not b.isdigit()
    

handler = GetRouteEntryHandler()
processor = GetRouteEntry.Processor(handler)
transport = TSocket.TServerSocket("localhost", port = 9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
 
print "Starting thrift server in python..."
server.serve()
print "done!"
