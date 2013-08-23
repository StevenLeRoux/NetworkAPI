import tornado.ioloop
import tornado.web
import common.vlans as VLANS
import ipaddr
import re
import dns.resolver
import dns.reversename
import json

maskre = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(/.+)$')

class VlanInfo(tornado.web.RequestHandler):
  def get(self,vlan):
    try:
      vlanmap = VLANS.vlan_map['vlan'+ vlan]
      self.write(vlanmap)
    except KeyError, e:
      self.send_error(status_code=404 )

class VlanADDR(tornado.web.RequestHandler):
  def get(self,vlan):
    try:
      vlanaddr = VLANS.vlan_map['vlan'+ vlan]['address']
      self.write(vlanaddr)
    except KeyError, e:
      self.send_error(status_code=404 )

class VlanGW(tornado.web.RequestHandler):

  def get(self,vlan):
    try:
      vlangw = VLANS.vlan_map['vlan'+ vlan]['gateway']
      self.write(vlangw)
    except KeyError, e:
      self.send_error(status_code=404 )

class VlanDESC(tornado.web.RequestHandler):
  def get(self,vlan):
    try:
      vlandesc = VLANS.vlan_map['vlan'+ vlan]['desc']
      self.write(vlandesc)
    except KeyError, e:
      self.send_error(status_code=404 )

class IPVlan(tornado.web.RequestHandler):
  def get(self,ip):
    vlan = str([item[0] for item in VLANS.vlan_map.items() if ipaddr.IPv4Address(ip) in ipaddr.IPv4Network(str(ipaddr.IPv4Interface(item[1]['address']).network_address) + str(maskre.search(str(ipaddr.IPv4Interface(item[1]['address']))).group(1)) ) ][0])
    self.write(vlan)

class IPptr(tornado.web.RequestHandler):
  def get(self,ip):
    try:
      no = dns.reversename.from_address(ip)
      answers = dns.resolver.query(no, 'PTR')
      nslist = []
      rd = {}
      for ns in answers:
        nslist.append(str(ns.target))
      rd['ptr'] = nslist
      rd['status'] = 0
    except dns.resolver.NoAnswer:
      rd = {}
      rd['status'] = 1
    except dns.resolver.NXDOMAIN:
      rd = {}
      rd['status'] = 1
    self.write(json.dumps(rd))

application = tornado.web.Application([
  (r"/vlan/([0-9]+)/info", VlanInfo),
  (r"/vlan/([0-9]+)/gw", VlanGW),
  (r"/vlan/([0-9]+)/address", VlanADDR),
  (r"/vlan/([0-9]+)/desc", VlanDESC),
  (r"/ip/(.*)/vlan", IPVlan),
  (r"/ip/(.*)/ptr", IPptr),
])

if __name__ == "__main__":
  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
