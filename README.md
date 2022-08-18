# htb-cli
> I never liked dragging and dropping into VBox anyway.

A command line tool to interact with the [HackTheBox](https://hackthebox.com) platform, using clubby789's unofficial [htb-api](https://github.com/clubby789/htb-api).

## Install
```shell
$ git clone https://github.com/An00bRektn/htb-cli.git; cd htb-cli
$ pip install -r requirements.txt
```
*Maybe use a virtual environment? Don't ask me, it's your computer.*

You can then build it locally from the repo directory
```shell
$ pip install .
$ htbcli -h
```

Or you can just run it using python.
```shell
$ python -m htbcli -h
```

## Usage
```shell
$ htbcli -h
htbcli - version v0.1 | "Powered by the officially unofficial HTB API :D"
author: @An00bRektn (an00brektn.github.io)
usage: htbcli [-h] [-c CACHE] [-v] {challenge,machine,vpn} ...

Interact with HackTheBox from the command line.

optional arguments:
  -h, --help            show this help message and exit
  -c CACHE, --cache CACHE
                        Path to cached credentials.
  -v, --verbose         increase output verbosity

subcommands:
  {challenge,machine,vpn}
    challenge           Interact with challenges.
    machine             Interact with machines.
    vpn                 Manage your VPN connection.
```

### Features
- 🎯 Challenges
  - 🗃️ Download challenge files
  - 🚩 Submit flags
  - 🐳 Spawn Docker instances
- 🖥️ Machines
  - ✔️ Spawn Machines, normally and Release Arena
    - **Known Bug**: API to spawn a machine normally is a little wonky right now, trying to fix that
  - 🚩 Submit flags
- 📡 VPN
  - 🌐 Switch Machine lab servers, Release Arena and normal
  - 📝 Download your VPN config

### TODO List
- [ ] Stop and/or restart docker instances
- [ ] Stop and/or restart spawned machine (and fix normal machine spawn bug)
- [ ] Improve aesthetics
- [ ] Possibly change flags to feel more intuitive
- [x] Refactor and reformat code for better extensibility and to be used as a module
- [ ] Support 2FA/OTP

## FAQ
#### How are you doing?
A bit tired, genuinely surprised I put the initial build together in ~4-6 hours.

#### What's this project do?
You skipped the entire README just to ask me that? Disrespectful smh.

#### Is this an official HTB project?
Nope, but it would be kind of hype if it was or they hired me 👀

#### Can I get [feature]?
I mostly made this on a whim, and it's heavily dependent on another API (although I could make some custom requests to the API if I had the time to investigate). If you want to contribute your own feature, go ahead! Make a pull request. But don't make one of those cringe issues because you didn't bother reading the code at all, because that's cringe.

#### Are my credentials secure when using this program?
You can choose to cache your credentials, but obviously those do get stored on disk. They expire after a variable length of time, but consider that. You can also just not cache the credentials and just input your username and password everytime.

#### Why does this code look so bad?
Hey, that's mean, but that doesn't mean you're wrong. Also I worked on this at night leave me alone.

#### What's your opinion on the current state of the world considering that the consequences of climate change only become more apparent everyday with limited proactiveness from the world's governments to try and take any action that isn't entirely concerned with the potential for reelection or retaining/gaining power?
not based :( 

## Acknowledgements
- This project is not as easy without clubby's [htb-api](https://github.com/clubby789/htb-api)
- I only realized after making the first iteration that [calebstewart](https://github.com/calebstewart/python-htb) already did this, but it hasn't been updated since 2020 (that was 2 years ago???) so who cares it's open source. I definitely did copy the setup.py stuff from him :)

## Disclaimer/Licensing
This project is wholly unaffiliated with any part of HackTheBox and is under the MIT License for usage.