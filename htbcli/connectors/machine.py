#!/usr/bin/env python3
from hackthebox import *
from htbcli.utils.colors import *

class MachineInterface:
    def __init__(self, client: HTBClient, name) -> None:
        self.client = client
        self.name = name
        print(info + f'Accessing machine {self.name}...')
        try:
            self.machine = self.client.get_machine(self.name)
            name = self.machine.name
        except errors.NotFoundException:
            print(printError + "Could not find machine. Exiting...")
            exit()
        print(good + f"Machine {self.machine.name} ({self.machine.os}, {self.machine.difficulty}) retrieved!")

    def spawn_machine(self, release_arena: bool):
        try:
            if release_arena:
                print(info + f'Spawning {self.name} in Release Arena...')
                instance = self.machine.spawn(release_arena=True)
            else:
                print(info + f'Spawning {self.name}...')
                try:
                    instance = self.machine.spawn()
                except Exception as e:
                    request = self.client.do_request(f'machine/play/{self.machine.id}', post=True)
                    instance = self.client.get_active_machine()
            ip = instance.ip
            print(good + f"{self.machine.name} started @ {instance.ip}")
            print(f"  \\\\--> Server: {instance.server}")
        except Exception as e:
            ip = ''
            print(printError + f"We encountered an error: {e}")
        return ip

    def attempt_submission(self, flag: str, difficulty: int):
        try:
            print(info + f'Submitting flag...')
            submission = self.machine.submit(flag, difficulty)
            print(good + submission)
        except errors.IncorrectFlagException:
            print(printError + 'Incorrect flag!')
        except errors.UserAlreadySubmitted:
            print(important + "You've already submitted the user flag!")
        except errors.RootAlreadySubmitted:
            print(important + "You've already submitted the root flag!")
        except Exception as e:
            print(printError + f"We encountered an error: {e}")

    def stop_instance(self):
        instance = self.client.get_active_machine()
        if instance is None:
            print(printError + "No assigned machine detected! Exiting...")
            exit()
        if instance is not None:
            try:
                print(info + f"Stopping {instance.machine.name} ({instance.ip})...")
                instance.stop()
                if self.client.get_active_machine() is not None:
                    request = self.client.do_request(f'machine/stop', post=True)
            except Exception as e:
                print(printError + f"We encountered an error: {e}")

    def reset_instance(self):
        instance = self.client.get_active_machine()
        if instance is None:
            print(printError + "No assigned machine detected! Exiting...")
            exit()
        try:
            print(info + f"Attempting to reset {instance.machine.name} ({instance.ip})")
            attempt = instance.reset()
            if attempt:
                print(good + "Reset message sent! You might want to wait 1 to 5 minutes before hacking again, or just check the actual website for the current status.")
        except TooManyResetAttempts:
            print(printError + "Too many reset machine attempts. Try again later!")
        except Exception as e:
            print(printError + f"We encountered an error: {e}")
        