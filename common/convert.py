#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import sys
import os.path
from os import chdir
import time
from time import localtime, strftime
import re



gents = time.time()
currentdir = os.getcwd()

if len(sys.argv) != 2:
  print >> sys.stderr, "Usage : python convert.py cisco.conf"
  exit(1)

file = sys.argv[1]
if not os.path.isfile(file):
  print >> sys.stderr, "ERROR : unable to load : ",file
  exit(1)

ifvlanre = re.compile(r'^interface\sVlan([0-9]+)$')
ifcfgre = re.compile(r'^\s+(.*)$')
descre = re.compile(r'^description\s(.*)$')
ipaddrre = re.compile(r'^ip\saddress\s(.*)\s(.*[0-9])$')
nore = re.compile(r'^no\s(.*)$')
gwre = re.compile(r'^standby\s(.*)\sip\s(.*)$')
commentre = re.compile(r'^!.*$')
endblockre = re.compile(r'^!$')

ifvlans = []
ifcfg = {}

lineno = 0
linetype = '0'
linevalue = 0

conf = open(file,'r')

netmap = {
  '240.0.0.0':'4',
  '248.0.0.0':'5',
  '252.0.0.0':'6',
  '254.0.0.0':'7',
  '255.0.0.0':'8',
  '255.128.0.0':'9',
  '255.192.0.0':'10',
  '255.224.0.0':'11',
  '255.240.0.0':'12',
  '255.248.0.0':'13',
  '255.252.0.0':'14',
  '255.254.0.0':'15',
  '255.255.0.0':'16',
  '255.255.128.0':'17',
  '255.255.192.0':'18',
  '255.255.224.0':'19',
  '255.255.240.0':'20',
  '255.255.248.0':'21',
  '255.255.252.0':'22',
  '255.255.254.0':'23',
  '255.255.255.0':'24',
  '255.255.255.128':'25',
  '255.255.255.192':'26',
  '255.255.255.224':'27',
  '255.255.255.240':'28',
  '255.255.255.248':'29',
  '255.255.255.252':'30'
}

def shorten_mask(netmask):
  return netmap[netmask]

for line in conf:
  lineno += 1
#  line = line.strip()


  m = commentre.search(line)
  if m:
    linetype = 'comment'
    linevalue = '0'
    continue

  m = endblockre.search(line)
  if m:
    linetype = 'endblock'
    linevalue = '0'
    continue

  m = ifvlanre.search(line)
  if m:
    ifvlanid = m.group(1)
    linetype = 'ifvlan'
    linevalue = ifvlanid

    ifvlans.append(ifvlanid)
    if not ifcfg.has_key(linevalue):
      ifcfg[linevalue] = {}
    continue

  m = ifcfgre.search(line)
  if m:
    if linetype in ('ifvlan'):
      cfg = m.group(1)

      n = descre.search(cfg)
      if n:
        desc = n.group(1)
        if not ifcfg[ifvlanid].has_key('description'):
          ifcfg[ifvlanid]['description'] = desc.replace("'"," ")
        continue
    
      n = ipaddrre.search(cfg)
      if n:
        ipaddr = n.group(1)
        netmask = n.group(2)
        shortmask = shorten_mask(netmask)
        if not ifcfg[ifvlanid].has_key('address'):
          ifcfg[ifvlanid]['address'] = ipaddr
        if not ifcfg[ifvlanid].has_key('mask'):
          ifcfg[ifvlanid]['mask'] = shortmask
        continue

      n = nore.search(cfg)
      if n:
        continue

      n = gwre.search(cfg)
      if n:
        gw = n.group(2)
        if not ifcfg[ifvlanid].has_key('gateway'):
          ifcfg[ifvlanid]['gateway'] = gw
        continue

    continue

  #print >> sys.stderr, lineno, "ERROR, didn't match line : %s" % line

#print 'vlan_map = ' + str(ifcfg)
vf = open('vlans.py', 'w')
vf.write('vlan_map = {\n')
for vlan in ifcfg.keys():
  try:
    vf.write("  'vlan" + vlan + "' : { 'address' : '" + ifcfg[vlan]['address'] + "/" + ifcfg[vlan]['mask'] + "' , 'gateway' : '" + ifcfg[vlan]['gateway'] + "', 'desc' : '" + ifcfg[vlan]['description'] + "'},\n")
  except:
    try:
      vf.write("  'vlan" + vlan + "' : { 'address' : '" + ifcfg[vlan]['address'] + "/" + ifcfg[vlan]['mask'] + "' , 'gateway' : '" + ifcfg[vlan]['gateway'] + "', 'desc' : 'NODESC'},\n")
    except:
      try:
        vf.write("  'vlan" + vlan + "' : { 'address' : '1.1.1.1/32', 'gateway' : '1.1.1.1', 'desc' : '" + ifcfg[vlan]['description'] + "'},\n")
      except:
        vf.write("  'vlan" + vlan + "' : { 'address' : '1.1.1.1/32', 'gateway' : '1.1.1.1', 'desc' : 'NODESC'},\n")
vf.write('}\n')
vf.close()
