import sys
import ipaddress

def main():

	if len(sys.argv) != 2:
        	sys.exit("Usage: %s <core1|core2|dmz1|dmz2>" % sys.argv[0])

	switch = sys.argv.pop()
	if ("core" in switch):
		peerConfig(switch)
		tenantConfig(switch)
		vpcConfig()
		sharedConfig()

	if ("dmz" in switch):
		dmzConfig()

def dmzConfig():

	print "vlan 305"
	print "  name DMZ-MEE-RMSONE"
	print

	for i in (["po10","po11","po12","po13"]):
		print "interface " + i
		print "  switchport trunk allowed vlan add 305"
		print "exit"
		print

def vpcConfig():
	for i in (["po2","po3","po22","po23","po25","po26"]):
		print "interface " + i
		print "  switchport trunk allowed vlan add 1250-1491"
		print

def sharedConfig():
	for i in (range(1252,1256)):
		if i == 1252:
			name = "SRV01"
		if i == 1253:
			name = "SRV02"
		if i == 1254:
			name = "DMZ01"
		if i == 1255:
			name = "DMZ02"

		print "vlan " + str(i)
		print "  name MS_400_SHARED-" + name
		print "exit"
		print

	for i in (["po2","po3","po22","po23","po25","po26","po51"]):
		print "interface " + i
		print "  switchport trunk allowed vlan add 1252-1255"
		print "exit"
		print

def peerConfig(core):
	peer_vlan_start = 1003
	peer_vlan_end = 1061
	peer_network_start = ipaddress.IPv4Address(u'10.x.4.24')

	for i in range(peer_vlan_start, peer_vlan_end):
		tenant_id = i - 602
		if core == "core1":
			core_ip = peer_network_start + 4
			priority = "120"
		if core == "core2":
			core_ip = peer_network_start + 5
			priority = "110"
		core_hsrp_ip = peer_network_start + 6
		default_gw = peer_network_start + 1
		print "vlan " + str(i)
		print "  name KEF1-" + str(tenant_id) + "-COR-ZN"
		print "exit"
		print
		print "vrf context vrf_kef1_prd_MS_" + str(tenant_id)
		print "  ip route 0.0.0.0/0 " + str(default_gw)
		print "exit"
		print
		print "interface Vlan" + str(i)
		print "  vrf member vrf_kef1_prd_MS_" + str(tenant_id)
		print "  ip flow monitor XX input sampler XX"
		print "  no ip redirects"
		print "  ip address " + str(core_ip) + "/29"
		print "  hsrp version 2"
		print "  hsrp " + str(i)
		print "    authentication md5 key-string XXXX"
		print "    preempt"
		print "    priority " + priority
		print "    ip " + str(core_hsrp_ip)
		print "  description Peering Edge FW to COR VDC / VRF : Tenant - " + str(tenant_id)
		print "  no shutdown"
		print
		peer_network_start += 8

def tenantConfig(core):

	tenant_vlan_start = 1260
	tenant_vlan_end = 1492
	tenant_id = 401
	tenant_network_start = ipaddress.IPv4Address(u'10.x.24.0')
	App = 1

	for i in range(tenant_vlan_start,tenant_vlan_end):
		if (i % 4 == 0) & (i != 1260):
			tenant_id += 1
			App = 1

		if core == "core1":
			core_ip = tenant_network_start + 2
			priority = "120"
		if core == "core2":
			core_ip = tenant_network_start + 3
			priority = "110"
		core_hsrp_ip = tenant_network_start + 1
		print "vlan " + str(i)
		print "  name MS_" + str(tenant_id) + "_APP_0" + str(App)
		print "exit"
		print
		print "interface Vlan" + str(i)
		print "  vrf member vrf_kef1_prd_MS_" + str(tenant_id)
		print "  ip flow monitor XX input sampler XX"
		print "  no ip redirects"
		print "  ip address " + str(core_ip) + "/24"
		print "  hsrp version 2"
		print "  hsrp " + str(i)
		print "    authentication md5 key-string XXX"
		print "    preempt"
		print "    priority " + priority
		print "    ip " + str(core_hsrp_ip)
		print "  description VLAN " + str(tenant_network_start)[:-2] + ":APP_0" + str(App)
		print "  no shutdown"
		print

		App += 1


		tenant_network_start += 256

if __name__ == "__main__":
	main()