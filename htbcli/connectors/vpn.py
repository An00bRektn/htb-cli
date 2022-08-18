#!/usr/bin/env python3
from hackthebox import *
from htbcli.utils.colors import *
from os.path import expanduser, isdir, isfile, exists

class VpnInterface:
    def __init__(self, client: HTBClient, name, release_arena=False) -> None:
        self.client = client
        self.name = name
        self.vpn_servers = [v for v in self.client.get_all_vpn_servers(release_arena)]
        self.vpn_names = [v.friendly_name.lower() for v in self.vpn_servers]

    def switch_servers(self, new_server:str):
        try:
            if new_server is not None and new_server.lower() != "menu":
                print(info + f"Finding {new_server}...")
                if new_server.lower() in self.vpn_names:
                    desired = self.vpn_servers[self.vpn_names.index(new_server.lower())]
                    print(info + f"Attempting to switch to {desired}...")
                    desired.switch()
                    print(good + "Switched!")
                else:
                    print(important + "Couldn't find server.")
                    new_server = 'menu'
        except Exception as e:
            print(printError + f"We encountered an error: {e}")

        try:
            if new_server.lower() == 'menu':
                print(info + "Bringing up options...")
                for i,v in enumerate(self.vpn_servers):
                    print(f"  {recc}{i} -> {v.friendly_name} (users: {v.current_clients})")
                
                selection = -1
                while selection < 0 or selection >= len(self.vpn_names):
                    selection = int(input(recc + 'Type the index of the server you want to switch to: '))

                print(info + f"Selected {self.vpn_names[selection]}")
                desired = self.vpn_servers[selection]
                print(info + f"Attempting to switch to {desired}...")
                desired.switch()
                print(good + "Switched!")
        except Exception as e:
            print(printError + f"We encountered an error: {e}")

    def download_vpn(self, path: str, tcp=False):
        try:
            print(info + f'Accessing current VPN Server...')
            server = self.client.get_current_vpn_server()
            print(good + f'Server {server.friendly_name} found!')
        except Exception as e:
            print(printError + f"We encountered an error: {e}")
            print(info + "Exiting...")
            exit()

        path = expanduser(path)
        print(info + f'Downloading VPN file to {path}')
        try:
            if exists(path) == False:
                server.download(path, tcp)
                print(good + "Download successful!")
            elif isdir(path):
                server.download(path.rstrip() + f'/{server.name}.ovpn', tcp)
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