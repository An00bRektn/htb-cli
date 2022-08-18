#!/usr/bin/env python3

# TODO: Accessibility? Probably need to ask someone what the do's and
#       don't-s of that are

class BannerBuilder:
    def __init__(self, args) -> None:
        self.args = vars(args)
        self.mapping = {
            "cache": "\N{floppy disk} Creds",
            "subcommand": "💿 Mode",
            "path": "💼 Download Path",
            "start_docker": "\N{spouting whale} Spawn Docker?",
            "stop": "🛑 Stop Instance?",
            "reset": "🔄 Reset Instance?",
            "flag": "🚩 Flag",
            "difficulty": "\N{clipboard} Difficulty Rating",
            "spawn": "💻 Spawn Machine?",
            "release_arena": "\N{chequered flag} Release Arena?",
            "switch": "\N{globe with meridians} New Server",
            "tcp":"📶 Use TCP?",
            "download":"💼 Download Path"
        }

    def build_banner(self):
        """Print passed arguments to be more verbose"""
        print('─'*50)
        for key,value in self.args.items():
            if key in self.mapping.keys():
                title = self.mapping[key]
                if key == "subcommand" and (value == "machine" or value == "challenge"):
                    print(f"{title + ' '*(25-len(title))} │ {value} ({self.args['name']})")
                else:
                    print(f"{title + ' '*(25-len(title))} │ {value}")
        print('─'*50)