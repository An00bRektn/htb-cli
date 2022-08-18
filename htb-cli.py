#!/usr/bin/env python3
import argparse
import getpass
import json
from hackthebox import *
from utils.colors import *
from os.path import expanduser, isdir, isfile, exists
from random import choice

# TODO: Fortresses, Endgames, maybe HBG? (don't even know if I can physically test endgames because skill issue)
# TODO: Add option to stop and/or reset container/machine. Not entirely sure 
#       how to accomplish this when we lose the handle after execution but we'll
#       see
# TODO: Improve aesthetics of verbosity and just everything overall
# TODO: Consider changing flags to be more intuitive

def get_args():
    # Begin original commands - mostly related to authentication
    parser = argparse.ArgumentParser(description="Interact with HackTheBox from the command line.")
    parser.add_argument('-c', '--cache', type=str, help='Path to cached credentials.')
    parser.add_argument('-v', '--verbose', action="store_true", help="increase output verbosity")
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Begin challenge subcommand
    parser_chall = subparsers.add_parser('challenge', help="Interact with challenges.")
    parser_chall.add_argument('-n', '--name', required=True, help='Name of the challenge, or the challenge ID.')
    parser_chall.add_argument('-p', '--path', type=str, help='Download challenge files to the specified path.', default=None)
    parser_chall.add_argument('-s', '--start-docker', action="store_true", help='Start Docker instance.')
    parser_chall.add_argument('-f', '--flag', type=str, help='Submit flag.')
    parser_chall.add_argument('-d', '--difficulty', type=int, choices=range(10,101), metavar="[10-100]", help='Submit difficulty rating, 10-100.')

    # Begin machine subcommand
    parser_mach = subparsers.add_parser('machine', help="Interact with machines.")
    parser_mach.add_argument('-n', '--name', required=True, help='Name of the machine, or the machine ID.')
    parser_mach.add_argument('-s', '--spawn', action="store_true", help='Spawn machine.')
    parser_mach.add_argument('--release-arena', action="store_true", help='Spawn machine in release arena.')
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
        if self.args.verbose:
            #print(f"[ DEBUG ] args={self.args}")
            self.print_args()
        self.subcommand = self.args.subcommand
        
        if self.subcommand != 'vpn':
            if self.args.name is not None:
                if self.args.name.isdecimal():
                    self.args.name = int(self.args.name)

        self.cred_management()

    def run(self):
        """Executes the specified subcommand"""
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
        
    def challenge(self):
        """Facilitates interactions with the challenges. TODO: Move to separate class/file"""
        # Attempt to access the challenge to return a Challenge object
        print(info + f'Accessing challenge {self.args.name}...')
        try:
            chall = self.client.get_challenge(self.args.name)
        except errors.NotFoundException:
            print(printError + "Could not find challenge. Exiting...")
            exit()
        print(good + f"Challenge {chall.name} ({chall.category}) retrieved!")

        # If the user has specified they want to download the files, download the files
        if self.args.path is not None and chall.has_download:
            path = expanduser(self.args.path)
            print(info + f'Downloading challenge files to {path}')
            try:
                if exists(path) == False:
                    chall.download(path)
                    print(good + f"Download to {path} successful!")
                elif isdir(path):
                    chall.download(path.rstrip() + f'/{chall.name}.zip')
                    print(good + f"Download to {path} successful!")
                elif isfile(path):
                    overwrite = input(important + "File specified already exists, do you want to overwrite it (y/n)? ")
                    if overwrite.lower() == 'y':
                        chall.download(path)
                        print(good + f"Download to {path} successful!")
                    else:
                        print(info + "Skipping download...")
                else:
                    print(important + "Path specified is not a directory or file, skipping...")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")

        # Spawn docker assuming the challenge has docker
        if self.args.start_docker and chall.has_docker:
            print(info + f'Starting Docker instance...')
            try:
                instance = chall.start()
                print(good + f"Docker started @ {instance.ip}:{instance.port}")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")

        # submit flag and difficulty rating, both are required for a valid submission
        if self.args.flag is not None and self.args.difficulty is not None:
            try:
                print(info + f'Submitting flag...')
                submission = chall.submit(self.args.flag, self.args.difficulty)
                if submission:
                    print(good + f"Congratulations! {chall.name} ({chall.category}, {chall.points} pts) has been solved!")
            except errors.IncorrectFlagException:
                print(printError + 'Incorrect flag!')
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
        elif (self.args.flag is None) != (self.args.difficulty is None):
            print(important + "You need a flag and a difficulty to submit!")

    def machine(self):
        """Facilitates interactions with the machines. TODO: Move to separate class/file"""
        # Pull down the machine object
        print(info + f'Accessing machine {self.args.name}...')
        try:
            machine = self.client.get_machine(self.args.name)
            name = machine.name
        except errors.NotFoundException:
            print(printError + "Could not find machine. Exiting...")
            exit()

        print(good + f"Machine {machine.name} ({machine.difficulty}) retrieved!")

        # attempt to spawn the machine either normally or in release arena
        # TODO: Known Issue, after talking with clubby, found out that there
        #       may have been an API change that breaks the regular spawn :(.
        #       Need to check it out with burp or something.
        if self.args.spawn:
            try:
                if self.args.release_arena == True:
                    print(info + f'Spawning {name} in Release Arena...')
                    instance = machine.spawn(release_arena=True)
                else:
                    print(info + f'Spawning {name}...')
                    instance = machine.spawn()
                print(good + f"{name} started @ {instance.ip}")
                print(f"  \\\\--> Server: {instance.server}")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")

        # submit flag and difficulty rating, both are required for a valid submission
        if self.args.flag is not None and self.args.difficulty is not None:
            try:
                print(info + f'Submitting flag...')
                submission = machine.submit(self.args.flag, self.args.difficulty)
                print(good + submission)
            except errors.IncorrectFlagException:
                print(printError + 'Incorrect flag!')
            except errors.UserAlreadySubmitted:
                print(important + "You've already submitted the user flag!")
            except errors.RootAlreadySubmitted:
                print(important + "You've already submitted the root flag!")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
        elif (self.args.flag is None) != (self.args.difficulty is None):
            print(important + "You need a flag and a difficulty to submit!")

    def vpn(self):
        """Manage VPN connections using specified flags."""
        ra = self.args.release_arena
        vpn_servers = [v for v in self.client.get_all_vpn_servers(release_arena=ra)]
        vpn_names = [v.friendly_name.lower() for v in vpn_servers]

        # If the user specified a switch, try to switch to server
        # If the switch is specified but there's no server, open a menu
        try:
            if self.args.switch is not None and self.args.switch.lower() != "menu":
                print(info + f"Finding {self.args.switch}...")
                if self.args.switch.lower() in vpn_names:
                    desired = vpn_servers[vpn_names.index(self.args.switch.lower())]
                    print(info + f"Attempting to switch to {desired}...")
                    desired.switch()
                    print(good + "Switched!")
                else:
                    print(important + "Couldn't find server.")
                    self.args.switch = 'menu'
        except Exception as e:
            print(printError + f"We encountered an error: {e}")

        # menu stuffs
        try:
            if self.args.switch.lower() == 'menu':
                print(info + "Bringing up options...")
                for i,v in enumerate(vpn_servers):
                    print(f"  {recc}{i} -> {v.friendly_name} (users: {v.current_clients})")
                
                selection = -1
                while selection < 0 or selection >= len(vpn_names):
                    selection = int(input(recc + 'Type the index of the server you want to switch to: '))

                print(info + f"Selected {vpn_names[selection]}")
                desired = vpn_servers[selection]
                print(info + f"Attempting to switch to {desired}...")
                desired.switch()
                print(good + "Switched!")
        except Exception as e:
            print(printError + f"We encountered an error: {e}")

        # Download the VPN file
        if self.args.download is not None:
            try:
                print(info + f'Accessing current VPN Server...')
                server = self.client.get_current_vpn_server()
                print(good + f'Server {server.friendly_name} found!')
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
                print(info + "Exiting...")
                exit()

            path = expanduser(self.args.download)
            print(info + f'Downloading VPN file to {path}')
            try:
                if exists(path) == False:
                    server.download(path, tcp=self.args.tcp)
                    print(good + "Download successful!")
                elif isdir(path):
                    server.download(self.args.path.rstrip() + f'/{server.name}.ovpn', tcp=self.args.tcp)
                    print(good + "Download successful!")
                elif isfile(path):
                    overwrite = input(important + "File specified already exists, do you want to overwrite it (y/n)? ")
                    if overwrite.lower() == 'y':
                        server.download(path)
                        print(good + f"Download to {path} successful!")
                    else:
                        print(info + "Skipping download...")
                else:
                    print(important + "Path specified is not a directory or file, skipping...")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")

if __name__ == "__main__":
    flavortext = [
        "Skill issue.",
        "Old UI > New UI",
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

    print(f'\033[92mHTB CLI - version v0.1 | "{choice(flavortext)}"\033[0m')
    print('\033[35mauthor: @An00bRektn (an00brektn.github.io)\033[0m')
    h = HTBCLI()
    try:
        h.run()
    except KeyboardInterrupt:
        print("\n" + info + "Exiting...")
    except errors.RateLimitException:
        print(important + "You might be making too many requests. " 
                        + "Please wait at least 30 seconds before issuing another command.")