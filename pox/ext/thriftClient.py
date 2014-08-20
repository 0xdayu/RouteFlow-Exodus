import sys
sys.path.append('./gen-py')
 
from route import GetRouteEntry 
from route.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift import Thrift
 
import socket

try:
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = GetRouteEntry.Client(protocol)
    transport.open()
   
    q = Query()
    q.arguments = ["1","1.2.3.4","10","5"]
    
    result = client.get(q)

    print result

except Thrift.TException, ex:
  print "%s" % (ex.message)
