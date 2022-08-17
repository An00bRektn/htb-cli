#!/usr/bin/env python3
import argparse
import getpass
import json
import time
from hackthebox import *
from utils.colors import *
from os.path import expanduser

# TODO: Fortresses, Endgames, and VPN (maybe HBG?)
# TODO: Add option to stop and/or reset container/machine. Not entirely sure 
#       how to accomplish this when we lose the handle after execution but we'll
#       see
# TODO: If a machine/challenge id is supplied, convert it to the name and handle that 
#       correctly

def get_args():
    # Begin original commands - mostly related to authentication
    parser = argparse.ArgumentParser(description="Interact with HackTheBox from the command line.")
    parser.add_argument('-c', '--cache', type=str, help='Path to cached credentials (default: ~/.config/.htbcache)', default='~/.config/.htbcache')
    parser.add_argument('-i', '--input-creds', action="store_true", help='Use stdin to input credentials')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Begin challenge subcommand
    parser_chall = subparsers.add_parser('challenge', help="Interact with challenges.")
    parser_chall.add_argument('-n', '--name', required=True, help='Name of the challenge, or the challenge ID.')
    parser_chall.add_argument('-p', '--path', default='', type=str, help='Download challenge files to the specified path.')
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
        print(f"[ DEBUG ] args={self.args}")
        self.subcommand = self.args.subcommand
        self.cred_management()
 
    def run(self):
        if self.subcommand == 'challenge':
            self.challenge()
        elif self.subcommand == 'machine':
            self.machine()

    def cred_management(self):
        """Applies flags to authenticate with the API, either through input or caching."""
        if self.args.input_creds:
            self.username = input('Email: ')
            self.password = getpass.getpass('Password: ')
            try:
                self.client = HTBClient(email=self.username, password=self.password)
            except errors.ApiError as e:
                print(printError + f"Couldn't authenticate: {e}")
                print(info + "Exiting...")
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
        print(info + f'Accessing {self.args.name}...')
        try:
            chall = self.client.get_challenge(self.args.name)
        except errors.NotFoundException:
            print(printError + "Could not find challenge. Exiting...")
            exit()

        # If the user has specified they want to download the files, download the files
        if self.args.path != '' and chall.has_download:
            print(info + f'Downloading challenge files to {self.args.path}')
            try:
                chall.download(self.args.path)
                print(good + "Download successful!")
            # TODO: Implement a check before downloading the file to see if it's a directory or not.
            #       A 30s lockout is just too brutal.
            except IsADirectoryError:
                time.sleep(self.client.challenge_cooldown - int(time.time()))
                chall.download(self.args.path.rstrip() + f'/{chall.name}.zip')
                print(good + "Download successful!")
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
        print(info + f'Accessing {self.args.name}...')
        try:
            machine = self.client.get_machine(self.args.name)
            name = machine.name
        except errors.NotFoundException:
            print(printError + "Could not find machine. Exiting...")
            exit()

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