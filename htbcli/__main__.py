#!/usr/bin/env python3
import argparse
import getpass
import json

from hackthebox import *
from htbcli.connectors.challenge import ChallengeInterface
from htbcli.connectors.machine import MachineInterface
from htbcli.connectors.vpn import VpnInterface
from htbcli.utils.colors import *
from os.path import expanduser, isdir, isfile, exists
from random import choice

# TODO: Fortresses, Endgames, maybe HBG? (don't even know if I can physically test endgames because skill issue)
# TODO: Add option to see/search for info about challenges and machines on the platform
# TODO: Improve aesthetics of verbosity and just everything overall
# TODO: Consider changing flags to be more intuitive

def get_args():
    # Begin original commands - mostly related to authentication
    parser = argparse.ArgumentParser(
        description="Interact with HackTheBox from the command line.",
        usage="htbcli [-h] [-c CACHE] [-v] {challenge,machine,vpn} ..."
        )
    parser.add_argument('-c', '--cache', type=str, help='Path to cached credentials.')
    parser.add_argument('-v', '--verbose', action="store_true", help="increase output verbosity")
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Begin challenge subcommand
    parser_chall = subparsers.add_parser('challenge', help="Interact with challenges.")
    parser_chall.add_argument('-n', '--name', required=True, help='Name of the challenge, or the challenge ID.')
    parser_chall.add_argument('-p', '--path', type=str, help='Download challenge files to the specified path.', default=None)
    parser_chall.add_argument('-s', '--start-docker', action="store_true", help='Start Docker instance.')
    parser_chall.add_argument('--stop', action="store_true", help='Stop challenge instance.')
    parser_chall.add_argument('-r', '--reset', action="store_true", help='Stop and then start challenge instance.')
    parser_chall.add_argument('-f', '--flag', type=str, help='Submit flag.')
    parser_chall.add_argument('-d', '--difficulty', type=int, choices=range(10,101), metavar="[10-100]", help='Submit difficulty rating, 10-100.')

    # Begin machine subcommand
    parser_mach = subparsers.add_parser('machine', help="Interact with machines.")
    parser_mach.add_argument('-n', '--name', required=True, help='Name of the machine, or the machine ID.')
    parser_mach.add_argument('-s', '--spawn', action="store_true", help='Spawn machine.')
    parser_mach.add_argument('--release-arena', action="store_true", help='Spawn machine in release arena.')
    parser_mach.add_argument('--stop', action="store_true", help='Stop currently assigned machine.')
    parser_mach.add_argument('-r', '--reset', action="store_true", help='Attempt to reset currently assigned machine')
    parser_mach.add_argument('-f', '--flag', type=str, help='Submit flag.')
    parser_mach.add_argument('-d', '--difficulty', type=int, choices=range(10,101), metavar="[10-100]", help='Submit difficulty rating, 10-100.')
    
    # Begin VPN subcommands
    parser_vpn = subparsers.add_parser('vpn', help="Manage your VPN connection.")
    parser_vpn.add_argument('-s', '--switch', type=str, help='Switch currently assigned VPN server. Machine labs only. Pass "menu" to select from menu.')
    parser_vpn.add_argument('--release-arena', action="store_true", help='Work with release arena servers.')
    parser_vpn.add_argument('-t', '--tcp', action="store_true", help='Use TCP instead of UDP for VPN config.')
    parser_vpn.add_argument('-d', '--download', type=str, help='Download your assigned VPN config file to the specified path.', default=None)

    args = parser.parse_args()

    return args

class HTBCLI:
    def __init__(self) -> None:
        self.args = get_args()
        #print(f"[ DEBUG ] args={self.args}")

        if self.args == argparse.Namespace(cache=None, subcommand=None, verbose=False):
            print(recc + "Use the -h/--help flag for basic help information.")
            exit()

        if self.args.verbose:
            self.print_args()
        self.subcommand = self.args.subcommand
        
        if self.subcommand != 'vpn' and self.subcommand is not None:
            if self.args.name.isdecimal():
                self.args.name = int(self.args.name)

    def run(self):
        """Executes the specified subcommand"""
        self.cred_management()
        if self.subcommand == 'challenge':
            self.challenge()
        elif self.subcommand == 'machine':
            self.machine()
        elif self.subcommand == 'vpn':
            self.vpn()

    def print_args(self):
        """Print passed arguments to be more verbose"""
        print('─'*50)
        for key,value in vars(self.args).items():
            if value is not None: 
                print(f"{key+' '*(15-len(key))} │ {value}")
        print('─'*50)

    def cred_management(self):
        """Applies flags to authenticate with the API, either through input or caching."""
        
        # If the user wants to input creds directly
        if self.args.cache is None:
            self.username = input(recc + 'Email: ')
            self.password = getpass.getpass(recc + 'Password: ')
            try:
                self.client = HTBClient(email=self.username, password=self.password)
            except errors.ApiError as e:
                print(printError + f"Couldn't authenticate: {e}")
                print(info + "Exiting...")
                exit()
            except AttributeError as e:
                print(printError + f"Couldn't authenticate: {e}")
                print(info + "Exiting...")
                exit()
        # If the path given to the cache is invalid
        elif exists(expanduser(self.args.cache)) == False:
            cache_choice = input(important + f"No cache found at {expanduser(self.args.cache)}, would you like to create a cache there (y/n)? ")
            self.username = input(recc + 'Email: ')
            self.password = getpass.getpass(recc + 'Password: ')
            try:
                if cache_choice.lower() == 'y':
                    self.client = HTBClient(email=self.username, password=self.password, cache=expanduser(self.args.cache))
                else:
                    self.client = HTBClient(email=self.username, password=self.password)
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
                print(info + "Exiting...")
                exit()
        # The cache exists
        else:
            try:
                self.client = HTBClient(cache=expanduser(self.args.cache))
            except json.decoder.JSONDecodeError:
                print(printError + f"Encountered an error reading {expanduser(self.args.cache)}. Please check if the " +
                            "file is valid JSON, or delete the cache file and rerun this program" + 
                            " to create a new one.")
                print(info + "Exiting...")
                exit()
            except AttributeError as e:
                print(printError + f"Couldn't authenticate: {e}")
                print(info + "Exiting...")
                exit()
            except IsADirectoryError:
                print(printError + "Specified cache file is a directory")
                print(info + "Exiting...")
                exit()
        
    def challenge(self):
        """Facilitates interactions with the challenges. TODO: Move to separate class/file"""
        # Attempt to access the challenge to return a Challenge object
        chall_interface = ChallengeInterface(self.client, self.args.name)
        
        # If the user has specified they want to download the files, download the files
        if self.args.path is not None and chall_interface.chall.has_download:
            chall_interface.download_chall_files(self.args.path)

        # Spawn docker assuming the challenge has docker
        if self.args.start_docker and chall_interface.chall.has_docker:
            chall_interface.spawn_docker()

        if self.args.stop and chall_interface.chall.has_docker:
            chall_interface.stop_instance()

        if self.args.reset and chall_interface.chall.has_docker:
            chall_interface.stop_instance()
            chall_interface.spawn_docker()

        # submit flag and difficulty rating, both are required for a valid submission
        if self.args.flag is not None and self.args.difficulty is not None:
            chall_interface.attempt_submission(self.args.flag, self.args.difficulty)
        elif (self.args.flag is None) != (self.args.difficulty is None):
            print(important + "You need a flag and a difficulty to submit!")

        
    def machine(self):
        """Facilitates interactions with the machines. TODO: Move to separate class/file"""
        # Pull down the machine object
        machine = MachineInterface(self.client, self.args.name)

        # attempt to spawn the machine either normally or in release arena
        if self.args.spawn:
            machine.spawn_machine(self.args.release_arena)

        # submit flag and difficulty rating, both are required for a valid submission
        if self.args.flag is not None and self.args.difficulty is not None:
            machine.attempt_submission(self.args.flag, self.args.difficulty)
        elif (self.args.flag is None) != (self.args.difficulty is None):
            print(important + "You need a flag and a difficulty to submit!")

        if self.args.stop:
            machine.stop_instance()

        if self.args.reset:
            machine.reset_instance()

    def vpn(self):
        """Manage VPN connections using specified flags."""
        ra = self.args.release_arena
        vpn_interface = VpnInterface(self.client, self.args.switch, ra)

        # If the user specified a switch, try to switch to server
        # If the switch is specified but there's no server, open a menu
        if self.args.switch is not None:
            vpn_interface.switch_servers(self.args.switch)

        # Download the VPN file
        if self.args.download is not None:
            vpn_interface.download_vpn(self.args.download, self.args.tcp)

def main():
    flavortext = [
        "Skill issue.",
        "Old UI > New UI > this UI",
        "New UI > Old UI?",
        "bin.",
        ":lemonthink:",
        "*perfect infra* :)",
        "No spoilers or flag leaks >:(",
        "Powered by the officially unofficial HTB API :D",
        "Why do machines when you can just do challenges?",
        "Can I get a reset? No? Well alright then.",
        "If you're using Windows, don't."
    ]

    print(f'\033[92mhtbcli - version v0.1 | "{choice(flavortext)}"\033[0m')
    print('\033[35mauthor: @An00bRektn (an00brektn.github.io)\033[0m')
    h = HTBCLI()
    try:
        h.run()
    except KeyboardInterrupt:
        print("\n" + info + "Exiting...")
    except errors.RateLimitException:
        print(important + "You might be making too many requests. " 
                        + "Please wait at least 30 seconds before issuing another command.")

if __name__ == "__main__":
    main()