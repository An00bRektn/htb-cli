# htb-cli
> I never liked dragging and dropping into VBox anyway.

A command line tool to interact with the [HackTheBox](https://hackthebox.com) platform, using clubby789's unofficial [htb-api](https://github.com/clubby789/htb-api).

## Install
```shell
$ git clone https://github.com/An00bRektn/htb-cli.git; cd htb-cli
$ pip install -r requirements.txt
```
*Maybe use a virtual environment? Don't ask me, it's your computer.*

## Usage
```shell
$ ./htb-cli.py -h
usage: htb-cli.py [-h] [-c CACHE] [-i] {challenge,machine} ...

Interact with HackTheBox from the command line.

optional arguments:
  -h, --help            show this help message and exit
  -c CACHE, --cache CACHE
                        Path to cached credentials (default: ~/.config/.htbcache)
  -i, --input-creds     Use stdin to input credentials

subcommands:
  {challenge,machine}
    challenge           Interact with challenges.
    machine             Interact with machines.
```

### Subcommands
```shell
$ ./htb-cli.py challenge -h
usage: htb-cli.py challenge [-h] -n NAME [-p PATH] [-s] [-f FLAG] [-d [10-100]]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the challenge, or the challenge ID.
  -p PATH, --path PATH  Download challenge files to the specified path.
  -s, --start-docker    Start Docker instance.
  -f FLAG, --flag FLAG  Submit flag.
  -d [10-100], --difficulty [10-100]
                        Submit difficulty rating, 10-100.
```