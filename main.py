# ============================= CODE IMPLEMENTATION EXPLANATION ==============================
# 1. MAC Address: Media Access Control Address
# 2. It is a permanent, physical and unique address assigned to a network interfaces by the device manufacturer.
# 3. It is a unique identifier assigned to network interfaces for communications on the physical network segment.
# 4. It is used to identify a network interface card (NIC) in a network.
# 5. It is a 48-bit number that is divided into 6 octets (12 hexadecimal digits).
# 6. Format: 00:00:00:00:00:00

# 7. Whether someone is using a wired or a wireless or an ethernet card, each one of these network cards
#    comes with a specific address that is unique to that card.
# 8. There are no two devices in the world with the same MAC address.
# 9. MAC Address is used within a network to identify devices and transfer data between them.
# 10. Each packet of data that is sent over a network has a source MAC address and a destination MAC address.
# 11. WHY MAC ADDRESS IS IMPORTANT?
#       - Used to identify a device on a network.
#       - Used to filter traffic on a network.
#       - Used to prevent unauthorized access to a network.

# WHERE MAC ADDRESS MANIPULATION IS USED?
# Increase anonymity
# Prevent tracking
# Spoofing - MAC Address Spoofing is a technique used to change the MAC address of a network interface card (NIC)
#            in order to impersonate another device on the network.
# Bypass filters: MAC Address filtering is a security measure that allows or blocks network traffic based on the
#                 MAC address of the device sending the traffic.
# Bypass access control lists (ACLs): Access control lists (ACLs) are used to control network traffic
#                                    by defining a set of rules that determine how network traffic is allowed or denied.

# Manually changing the MAC Address of UNIX based systems:
# ifconfig: list all the network interfaces on the current system. By interface, we mean the network card.
# ifconfig eth0 down: - bring down the interface eth0.
#                     - where eth0 is the interface that we'd like to change the MAC address of.
#                     - bringing down the interface will allow us to modify its options.
#                     - And the option that we want to modify is the `ether` option that is the MAC address.
# ifconfig eth0 hw ether 00:11:22:33:44:55 => change the MAC address of the interface eth0 to 00:11:22:33:44:55.
# ifconfig eth0 up: bring up the interface eth0 which we brought down earlier.

# =============================== CODE IMPLEMENTATION ===============================

import subprocess  # to run system commands
from random import choice  # to generate a random MAC Address
import argparse  # allows us to parse command line arguments
from termcolor import colored  # pip install termcolor  => a module to print colored text in the terminal


def get_current_mac():
    """returns the current MAC Address of the interface"""
    eth0 = subprocess.check_output(['ifconfig'])  # returns the output of the command as a byte string => b'<content>'
    # convert the byte string to a string using decode('utf-8) and split the string into a list using split('\n')
    eth0 = eth0.decode('utf-8').split('\n')
    # get the line containing 'ether' and extract the mac address
    mac_address = [line.split()[1] for line in eth0 if 'ether' in line][0]
    return mac_address


def generate_mac():
    """generate a random MAC Address of the format xy:xx:xx:xx:xx:xx where x is a hexadecimal digit
    and y is any of these hexadecimal digits: 0, 2, 4, 6, 8, a, c, e"""
    possible_mac_chars = [char for char in '0123456789abcdef']
    random_mac = []  # list to store the random MAC Address => ['xy', 'xx', 'xx', 'xx', 'xx', 'xx']
    for i in range(6):
        if i == 0:
            random_mac.append(choice(possible_mac_chars) + choice(['0', '2', '4', '6', '8', 'a', 'c', 'e']))
        else:
            random_mac.append(choice(possible_mac_chars) + choice(possible_mac_chars))
    random_mac = ':'.join(random_mac)  # convert the list to a string
    # print(f'Random MAC Address: {random_mac}')
    return random_mac


def get_interface():
    """returns the list of interfaces that we want to change the MAC Address of"""
    interfaces = subprocess.check_output(['ifconfig']).decode('utf-8').split('\n\n')
    interfaces = [interface.split()[0] for interface in interfaces if interface != '']
    # print(interfaces)
    return interfaces


def change_all_mac(interface=None, new_mac=None):
    """changes the MAC Address of all the interfaces until the system is rebooted"""
    interfaces = get_interface()  # Eg: ['eth0', 'lo', 'wlan0']
    for interface in interfaces:
        new_mac = generate_mac()
        print(f'Changing MAC Address for {interface} to {new_mac}')
        subprocess.call(['ifconfig', interface, 'down'])
        subprocess.call(['ifconfig', interface, 'hw', 'ether', new_mac])
        subprocess.call(['ifconfig', interface, 'up'])
        if get_current_mac() == new_mac:
            print(colored(f'[+] MAC Address was successfully changed to {new_mac}', 'green'))
        else:
            print('MAC Address was not changed')


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC Address')
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC Address')
    options = parser.parse_args()
    if not options.interface:
        parser.error('[-] Please specify an interface, use --help for more info.')
    elif not options.new_mac:
        parser.error('[-] Please specify a new MAC Address, use --help for more info.')
    return options


# Change the MAC Address which works two ways:
# 1. If the user specifies the new MAC Address, change the MAC Address to the specified MAC Address
# 2. If the user does not specify the new MAC Address, change the MAC Address to a random MAC Address
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', dest='interface', help='Interface to change its MAC Address')
    parser.add_argument('-m', '--mac', dest='new_mac', help='New MAC Address')
    options = parser.parse_args()
    if not options.interface:
        parser.error('[-] Please specify an interface, use --help for more info')
    elif not options.new_mac:
        print(colored('[+] No MAC Address specified, changing MAC Address to a random MAC Address', 'green'))
        options.new_mac = generate_mac()
    change_all_mac(options.interface, options.new_mac)
