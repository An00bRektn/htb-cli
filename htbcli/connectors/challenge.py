#!/usr/bin/env python3
from hackthebox import *
from htbcli.utils.colors import *
from os.path import expanduser, isdir, isfile, exists


class ChallengeInterface:
    def __init__(self, client: HTBClient, name) -> None:
        self.client = client
        self.name = name
        print(info + f'Accessing challenge {self.name}...')
        try:
            self.chall = self.client.get_challenge(self.name)
        except errors.NotFoundException:
            print(printError + "Could not find challenge. Exiting...")
            exit()
        print(good + f"Challenge {self.chall.name} ({self.chall.category}) retrieved!")

    def download_chall_files(self, path: str):
        if self.chall.has_download:
            path = expanduser(path)
            print(info + f'Downloading challenge files to {path}')
            try:
                if exists(path) == False:
                    self.chall.download(path)
                    print(good + f"Download to {path} successful!")
                elif isdir(path):
                    self.chall.download(path.rstrip() + f'/{self.chall.name}.zip')
                    print(good + f"Download to {path} successful!")
                elif isfile(path):
                    overwrite = input(important + "File specified already exists, do you want to overwrite it (y/n)? ")
                    if overwrite.lower() == 'y':
                        self.chall.download(path)
                        print(good + f"Download to {path} successful!")
                    else:
                        print(info + "Skipping download...")
                else:
                    print(important + "Path specified is not a directory or file, skipping...")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
        else:
            print(important + f"{self.chall.name} doesn't have challenge files!")

    def spawn_docker(self):
        if self.chall.has_docker:
            print(info + f'Starting Docker instance...')
            try:
                instance = self.chall.start()
                addr = f'{instance.ip}:{instance.port}'
                print(good + f"Docker started @ {instance.ip}:{instance.port}")
            except Exception as e:
                print(printError + f"We encountered an error: {e}")
        else:
            addr = ''
            print(important + f"{self.chall.name} doesn't have a deployed instance!")
        return addr

    def attempt_submission(self, flag: str, difficulty: int):
        try:
            print(info + f'Submitting flag...')
            submission = self.chall.submit(flag, difficulty)
            if submission:
                print(good + f"Congratulations! {self.chall.name} ({self.chall.category}, {self.chall.points} pts) has been solved!")
        except errors.IncorrectFlagException:
            print(printError + 'Incorrect flag!')
        except Exception as e:
            print(printError + f"We encountered an error: {e}")