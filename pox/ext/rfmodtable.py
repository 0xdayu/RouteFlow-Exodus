import binascii
import logging
from socket import inet_aton

from pox.openflow.libopenflow_01 import *
from pox.lib.addresses import *
from pox.core import core

from rflib.defs import *
from rflib.types.Match import *
from rflib.types.Action import *
from rflib.types.Option import *

from rfofmsg import *

log = core.getLogger("rfproxy")

class RouteModTable:
    def __init__(self):
        self.RouteModTable = {}
        self.RouteTable = []

    def getRouteModTable(self):
        return self.RouteModTable

    def processRouteModTable(self, routemod):
        mod = routemod.get_mod()
        
        in_port = addr = prefix = out_port = None
        dl_src = dl_dst = None
        dl_type = nw_proto = None
        tp_src = tp_dst = None
        set_dl_src = set_dl_dst = None
        priority = idle_timeout = hard_timeout = None
       
        for match in routemod.get_matches():
            match = Match.from_dict(match)
            if match._type == RFMT_IPV4:
                addr = str(match.get_value()[0])
                prefix = get_cidr_prefix(inet_aton(match.get_value()[1]))
                dl_type = ETHERTYPE_IP
            elif match._type == RFMT_ETHERNET:
                dl_dst = match.get_value()
            elif match._type == RFMT_ETHERTYPE:
                dl_type = match.get_value()
            elif match._type == RFMT_NW_PROTO:
                nw_proto = match.get_value()
            elif match._type == RFMT_TP_SRC:
                tp_src = match.get_value()
            elif match._type == RFMT_TP_DST:
                tp_dst = match.get_value()
            elif match._type == RFMT_IN_PORT:
                in_port = match.get_value()

        for action in routemod.get_actions():
            action = Action.from_dict(action)
            value = action.get_value()
            if action._type == RFAT_OUTPUT:
                out_port = (value & 0xFFFF)
            elif action._type == RFAT_SET_ETH_SRC:
                set_dl_src = EthAddr(value)
            elif action._type == RFAT_SET_ETH_DST:
                set_dl_dst = EthAddr(value) 
        
        for option in routemod.get_options():
            option = Option.from_dict(option)
            if option._type == RFOT_PRIORITY:
                priority = option.get_value()
            elif option._type == RFOT_IDLE_TIMEOUT:
                idle_timeout = option.get_value()
            elif option._type == RFOT_HARD_TIMEOUT:
                hard_timeout = option.get_value()
            
        '''rule = (routemod.get_id(), in_port, addr, prefix, nw_proto, tp_src, tp_dst, \
                dl_type, dl_src, dl_dst, out_port, set_dl_src, set_dl_dst, priority, \
                idle_timeout, hard_timeout)
        '''
        
        rule_match = (routemod.get_id(), in_port, addr, prefix, nw_proto, tp_src, tp_dst, \
                dl_type, dl_src, dl_dst, priority, idle_timeout, hard_timeout)

        rule_action = (out_port, set_dl_src, set_dl_dst)

        if mod == RMT_ADD:
            self.RouteModTable[rule_match] = rule_action
        elif mod == RMT_DELETE:
            if rule_match in self.RouteModTable.keys():
                del self.RouteModTable[rule_match] 
        else:
            log.error("Unrecognised RouteMod Type (type: %s)" % (mod))
        
        self.generateRouteTable()

    def generateRouteTable(self):
        tempRouteTable = set()
        for key, value in self.RouteModTable.iteritems():
            (swid, in_port, addr, prefix, nw_proto, tp_src, tp_dst, \
                dl_type, dl_src, dl_dst, priority, idle_timeout, hard_timeout) = key
            (out_port, set_dl_src, set_dl_dst) = value
            if out_port == 65533 or addr is None or prefix is None or out_port is None:
                continue
            tempRouteTable.add((str(swid), str(addr), str(prefix), str(out_port)))
        self.RouteTable = list(tempRouteTable)

    def printRouteTable(self):

        print "##########Routing Table:#############"
        
        for r in self.RouteTable: 
           print "%s" % str(r)
