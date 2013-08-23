NetworkAPI
==========

Expose network info (such as Vlans infos) through an API

## Get VLAN infos

```
GET /vlan/<vlan_id>/info
=>  {"address": "10.0.0.0/24", "gateway": "10.0.0.254", "desc": "VLAN: VLAN DESCRIPTION: 10.0.0.0/24"}
```


## Get VLAN from IP

Example :
```
GET /ip/10.0.42.1/vlan
=> vlan42
```
