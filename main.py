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


def get_interface_dict() -> dict:
    """returns all interfaces(keys) and mac addresses (values) as a dictionary
    >>> cmd_outputs = [
          'eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>,... ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)',
          'lo: flags=73<UP,LOOPBACK,RUNNING>,... ether 00:00:00:00:00:00  txqueuelen 1000  (Ethernet)',
          'wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>, ... TX errors 0  dropped 0 overruns 0'
        ]
    >>> interface_dict = {
            output.split(':')[0]: output.split()[output.split().index('ether') + 1]
            for output in cmd_outputs if 'ether' in output.split()
        }
    >>> interface_dict
    {'eth0': '00:11:22:33:44:55', 'lo': '0a:66:55:44:33:22'}
    """
    # subprocess.check_output returns the output of the command as a byte string => b'<content>'
    # convert the byte string to a string using decode('utf-8')
    # and split the output string into a list by lines using split('\n\n')
    cmd_outputs = subprocess.check_output(['ifconfig']).decode('utf-8').split('\n\n')  # ['eth0:...', 'lo:...']

    # identify interfaces and the line containing 'ether' and extract the mac address along with interface.
    return {
        output.split(':')[0]: output.split()[output.split().index('ether') + 1]
        for output in cmd_outputs if 'ether' in output.split()
    }


def get_mac(interface) -> str:
    """returns the MAC Address of the given interface"""
    cmd_output = subprocess.check_output(['ifconfig', interface]).decode('utf-8').split()
    return cmd_output[cmd_output.index('ether') + 1]


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


def get_interface_list():  # ['eth0', 'lo', 'wlan0']
    """returns a list of all interfaces that we want to change the MAC Address of"""
    return [interface for interface, _ in get_interface_dict().items()]


def is_valid_mac(mac):
    """returns True if the given MAC Address is valid, else returns False"""
    return len(mac.split(':')) == 6 and all(len(octet) == 2 for octet in mac.split(':'))


def change_all_mac(interface=None, mac=None):
    """changes the MAC Address of all the interfaces until the system is rebooted"""
    interfaces = get_interface_list() if interface is None else [interface]  # Eg: ['eth0', 'lo', 'wlan0']
    if (interface is not None) and (interface not in get_interface_list()):  # None in ['eth0', 'lo', 'wlan0'] => False
        print(colored(f'[-] INVALID INTERFACE: {interface}!!! TRY AGAIN', 'red'))
        return
    else:
        for interface in interfaces:
            new_mac = generate_mac() if mac is None else mac
            print(colored(f'[+] Changing MAC Address for {interface} to {new_mac}', 'blue'))
            subprocess.call(['ifconfig', interface, 'down'])
            subprocess.call(['ifconfig', interface, 'hw', 'ether', new_mac])
            subprocess.call(['ifconfig', interface, 'up'])
            if get_mac(interface) == new_mac:
                print(colored(f'[+] MAC Address for `{interface}` was successfully changed to `{new_mac}`', 'green'))
            else:
                print(colored('[-] MAC Address WAS NOT CHANGED!!!', 'red'))


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
        print(colored('[-] Please specify an interface, use --help for more info', 'red'))
        print(colored(f'[+] No INTERFACE specified, changing MAC Address of all available INTERFACES: '
                      f'{", ".join(get_interface_list())}', 'green'))
    if not options.new_mac:
        print(colored('[-] Please specify a mac address, use --help for more info', 'red'))
        print(colored('[+] No MAC Address specified, changing MAC Address to a random MAC Address', 'green'))
    # print(options.interface, options.new_mac)
    change_all_mac(options.interface, options.new_mac)

# OUTPUT:
# [-] Please specify an interface, use --help for more info
# [+] No INTERFACE specified, changing MAC Address of all available INTERFACES: eth0
# [-] Please specify a mac address, use --help for more info
# [+] No MAC Address specified, changing MAC Address to a random MAC Address
# [+] Changing MAC Address for eth0 to 9a:8d:b9:ef:10:14
# [+] MAC Address for `eth0` was successfully changed to `9a:8d:b9:ef:10:14`
