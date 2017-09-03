# coding: utf8
"""
macros-but-better.py - HexChat script to help with dispatching in the FuelRats.

Copyright (c) 2017 Maximilian "MHajoha" Haye.
All rights reserved.

HexChat is copyright (c) 2009-2014 Berke Viktor.
https://hexchat.github.io/
"""

import platform
import os
from sys import exit
from types import FunctionType, GeneratorType
from functools import wraps

import hexchat

__module_name__ = "Macros but better"
__module_version__ = "2.0-beta"
__module_description__ = "Adds customizable commands for use when dispatching"

DEFAULT_CONFIG = {
    "cmd_char": "§",
    "prefix_char": ": "
}

config_path = ""
""" :var: Path to the config file. Set in init. """

config = dict()
""" :var: Parsed contents of the config file. Set in init. Please keep new config keys in lower case. """


# Helper functions

def parse_config(path: str=None) -> dict:
    """
    Parses the config file at the given location
    :param path: Path to config file. Defaults to global variable `config_path`.
    :raises FileNotFoundError: If there is no file is found at *path*.
    :raises IOError: Upon different failure opening file.
    """
    if path is None:
        path = config_path

    temp = dict()
    with open(path) as f:
        for line in f.readlines():
            key_value = line.split("=", maxsplit=1)
            if len(key_value) == 2:
                temp[key_value[0].strip()] = key_value[1].strip()
    return temp


def write_config(path: str=None, data: dict=None):
    """
    Writes the contents of *cfg* in INI-format.
    :param path: Path to config file. Defaults to global variable `config_path`.
    :param data: Config dict to be written. Defaults to global variable `config`.
    :raises IOError: Upon failure opening / creating file.
    """
    if path is None:
        path = config_path
    if data is None:
        data = config

    with open(path, "w" if os.path.isfile(path) else "x") as f:
        for key, value in data.items():
            f.write(key + " = " + value + "\n")


def prefix(text: str, l):
    """ Prefixes *text* with *l*, comma-separated. """
    return text if len(l) == 0 else ", ".join(l) + config["prefix_char"] + text


def postfix(text: str, l):
    """ Postfixes *text* with *l*, comma-separated. """
    return text if len(l) == 0 else text + ", ".join(l)


def say(it: str or GeneratorType or list):
    """ Says *it* or each `str` in it in the current IRC context """
    if type(it) is str:
        hexchat.command("say " + it)
    else:
        for item in it:
            say(item)


def say_fact(text: str, args: list):
    """
    If any *args* are given, prefix *text* with them and `say` the result.
    Otherwise, just `say` *text*.
    :param text: Fact text, should start with an uppercase letter.
    :param args: Arguments to the fact, i.e. intended recipients. Should be word[1:].
    """
    if len(args) > 0:
        temp = text[0].lower() + text[1:]
    else:
        temp = text

    say(prefix(temp, args))

# Decorators


def require_args(num: int, exact: bool=False):
    """
    Stops command execution if the number of arguments given is less than or anything other than num.
    :param num: Required number of arguments
    :param exact: If True, requires num to match the number of arguments exactly. If False, num is the minimum amount of arguments required
    """
    def dec(fun: FunctionType):
        @wraps(fun)
        def new_fun(word, word_eol):
            if (exact and len(word[1:])) == num or len(word[1:]) >= num:
                return fun(word, word_eol)
            else:
                print(("Command {0} exactly {1} arguments." if exact else "Command {0} takes at least {1} arguments.").format(word[0], num))

        return new_fun
    return dec


# Commands

@require_args(2)
def set_(word, word_eol):
    """ Changes a certain property in `config` or creates it if it does not exist. Writes changes immediately. """
    key = word[1].lower()
    value = word_eol[2]
    config[key] = value
    write_config(config_path, config)
    print("Config item %s set to \"%s\"" % (key, value))


def help_(word, word_eol):
    """ Prints out all available `commands`. """
    print(postfix("Available commands are: ", commands))
    print(postfix("Available facts are: ", facts))


commands = {
    "set": set_,
    "help": help_
}
""" :var: Assigns to each command their function. """

facts = {
    "start": "Hi there! Just to confirm, do you see a blue emergency oxygen depletion timer counting down near the upper right corner of your screen?",
    "startcr": "If you haven't already, please exit to the main menu. There may be a timer which you have to wait for, this is normal.",
    "wing": "Thank you. Next please invite your rat(s) to a wing.",
    "beacon": "Thanks. Now please light your wing beacon so that our rats can find you.",
    "tips": "Glad we could help you today. You can power your modules back up now. If you'll just stick with your rats in game for a bit, they have some advice which might interest you.",
    "tips-db": "Glad we could help you today. You can power your modules back up now. If you could type \"/join #debrief\", someone will give you some tips in there which may interest you.",
    "db-channel": "Please type \"/join #debrief\". Someone will give you tips on fuel management there.",
    "enroute": "Thank you, your rats are making their way to you now. Sit back, relax and tell me immediately if that timer should show up.",
    "long": "Since your rat(s) are still a ways out, please log out to the main menu for now. I will ask you to log back in when they are closer.",
    "need-fuel": "Hi there! Do you require fuel?",
    "join": "If you'd like to look into joining the FuelRats, type \"/join #ratchat\". We'll get you started there.",
    "shrug": "¯\_(ツ)_/¯",
    "lenny": "( ͡° ͜ʖ ͡° )"
}
""" :var: Like Mecha facts. See `say_fact` docstring """


# Initialization

def init():
    """
    Run a single time upon plugin load.
    Sets `config_path` depending on the OS and reads into `config` or creates a new one if necessary.
    Also adds any missing config items from `DEFAULT_CONFIG`.
    """
    global config_path
    global config

    if platform.system() == "Windows":
        config_path = os.path.join(os.getenv("APPDATA"), r"HexChat\mbb.conf")
    elif platform.system() == "Linux":
        config_path = r"~/.config/hexchat/mbb.conf"
    else:
        print("Your OS %s does not seem to be supported.\nMacros but better not loaded." % platform.system())
        exit(1)

    if os.path.isfile(config_path):
        config = parse_config()
        # Add missing config items
        for key, value in DEFAULT_CONFIG.items():
            if key not in config.keys():
                config[key] = DEFAULT_CONFIG[key]

        print(__module_name__ + ": Config file loaded from " + config_path)
    else:
        config = DEFAULT_CONFIG
        write_config()
        print("\n\002{0}\002\nThis seems to be your first time loading this plugin.\n"
              "By default commands begin with {1}. Type {1}set cmd_char <new character> to change this.\n"
              "Type {1}help for a list of all commands and facts.\n"
              .format(__module_name__, config["cmd_char"]))


# Hook functions

def on_send(word, word_eol, userdata):
    """
    Hook function, called upon all commands / messages the user sends.
    If the message is a script command or fact, parse it and call the corresponding function.

    Official HexChat Python interface documentation: http://hexchat.readthedocs.io/en/latest/script_python.html
    """
    if word_eol[0].strip().startswith(config["cmd_char"]) and len(word[0]) > 1:
        word[0] = word[0].lstrip(config["cmd_char"])
        word_eol[0] = word_eol[0].replace(config["cmd_char"], "", 1)

        if word[0] in commands.keys():
            commands[word[0]](word, word_eol)
        elif word[0] in facts.keys():
            say_fact(facts[word[0]], word[1:])
        else:
            print("Command " + word[0] + " not available, " + config["cmd_char"] + "help for a list of all commands.")

        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


init()
hexchat.hook_command("", on_send)

print(__module_name__ + " loaded successfully.")
