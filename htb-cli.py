#!/usr/bin/env python3
import argparse
import getpass
import json
import time
from hackthebox import *
from utils.colors import *
from os.path import expanduser, isdir, isfile, exists

# TODO: Fortresses, Endgames, and VPN (maybe HBG?)
# TODO: Add option to stop and/or reset container/machine. Not entirely sure 
#       how to accomplish this when we lose the handle after execution but we'll
#       see
# TODO: Improve aesthetics of verbosity

def get_args():
    # Begin original commands - mostly related to authentication
    parser = argparse.ArgumentParser(description="Interact with HackTheBox from the command line.")
    parser.add_argument('-c', '--cache', type=str, help='Path to cached credentials (default: ~/.config/.htbcache)', default='~/.config/.htbcache')
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
    
    args = parser.parse_args()

    return args

class HTBCLI:
    def __init__(self) -> None:
        self.args = get_args()
        if self.args.verbose:
            #print(f"[ DEBUG ] args={self.args}")
            self.print_args()
        self.subcommand = self.args.subcommand
        
        if self.args.name is not None:
            if self.args.name.isdecimal:
                self.args.name = int(self.args.name)

        self.cred_management()

    def run(self):
        """Executes the specified subcommand"""
        if self.subcommand == 'challenge':
            self.challenge()
        elif self.subcommand == 'machine':
            self.machine()

    def print_args(self):
        """Print passed arguments to be more verbose"""
        print('HTB CLI - version v0.1')
        print('author: @An00bRektn (an00brektn.github.io)')
        print('─'*50)
        for key,value in vars(self.args).items():
            if value is not None: 
                print(f"{key+' '*(15-len(key))} │ {value}")
        print('─'*50)

    def cred_management(self):
        """Applies flags to authenticate with the API, either through input or caching."""
        if exists(expanduser(self.args.cache)) == False:
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
        else:
            try:
                self.client = HTBClient(cache=expanduser(self.args.cache))
            except json.decoder.JSONDecodeError:
                print(printError + f"Encountered an error reading {expanduser(self.args.cache)}. Please check if the " +
                            "file is valid JSON, or delete the cache file and rerun this program" + 
                            " to create a new one.")
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
                if isdir(path):
                    chall.download(self.args.path.rstrip() + f'/{chall.name}.zip')
                    print(good + "Download successful!")
                elif isfile(path):
                    chall.download(self.args.path)
                    print(good + "Download successful!")
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

if __name__ == "__main__":
    h = HTBCLI()
    try:
        h.run()
    except KeyboardInterrupt:
        print(info + "Exiting...")