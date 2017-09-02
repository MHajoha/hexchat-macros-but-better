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
__module_version__ = "1.7-beta"
__module_description__ = "Adds customizable commands for use when dispatching"

DEFAULT_CHAR = "§"
""" :var: "cmd_char" used to create a config file if none exists. """

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
            f.write(key + " = " + value)


def prefix(text: str, l):
    """ Prefixes *text* with *l*, comma-separated. """
    return text if len(l) == 0 else ", ".join(l) + ", " + text


def postfix(text: str, l):
    """ Postfixes *text* with *l*, comma-separated. """
    return text if len(l) == 0 else text + ", ".join(l)


# Decorators

def say(fun: FunctionType):
    """ Says the return of the decorated function in the current context. """
    @wraps(fun)
    def new_fun(word, word_eol):
        temp = fun(word, word_eol)

        if type(temp) is str:
            hexchat.command("say " + temp)
        elif type(temp) is GeneratorType:
            for string in temp:
                hexchat.command("say " + string)

    return new_fun


def fact(fun: FunctionType):
    """
    Says the return of the decorated function prefixed with all given arguments in the current context.
    Also decapitalizes the first letter if there are arguments.
    Commands using this decorator should therefore start with an upper case letter.
    """
    @wraps(fun)
    def new_fun(word, word_eol):
        if len(word[1:]) > 0:
            temp = fun(word, word_eol)
            temp = temp[0].lower() + temp[1:]
        else:
            temp = fun(word, word_eol)

        if type(temp) is str:
            hexchat.command("say " + prefix(temp, word[1:]))
        elif type(temp) is GeneratorType:
            for string in temp:
                hexchat.command("say " + prefix(string, word[1:]))

    return new_fun


def require_args(num: int, exact: bool=False):
    """
    Stops command execution when the number of arguments given is less than or anything other than num.
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
    config[word[1].lower()] = word_eol[2]
    write_config(config_path, config)


def help_(word, word_eol):
    """ Prints out all available `commands`. """
    print(postfix("Available commands are: ", commands))


@fact
def start(word, word_eol):
    return "Hi there! Just to confirm, do you see a blue emergency oxygen depletion timer counting down near the upper right corner of your screen?"


@fact
def startcr(word, word_eol):
    return "If you haven't already, please exit to the main menu. There may be a timer which you have to wait for, this is normal."


@require_args(2)
@say
def add_rats(word, word_eol):
    return "{0}, your rat(s) are: {1}. Please add them to your friends list.".format(word[1], ", ".join(word[2:]))


@fact
def wing(word, word_eol):
    return "Thank you. Next please invite your rat(s) to a wing."


@fact
def beacon(word, word_eol):
    return "Thanks. Now please light your wing beacon so that our rats can find you."


@fact
def tips(word, word_eol):
    return "Glad we could help you today. You can power your modules back up now. If you'll just stick with your rats ingame for a bit, they have some advice which might interest you."


@fact
def tips_db(word, word_eol):
    return "Glad we could help you today. You can power your modules back up now. If you could type \"/join #debrief\", someone will give you some tips in there which may interest you."


@fact
def db_channel(word, word_eol):
    return "Please type \"/join #debrief\". Someone will give you tips on fuel management there."


@fact
def enroute(word, word_eol):
    return "Thank you, your rats are making their way to you now. Sit back, relax and tell me immediately if that timer should show up."


@fact
def long_trip(word, word_eol):
    return "Since your rat(s) are still a ways out, please log out to the main menu for now. I will ask you to log back in when they are closer."


@fact
def need_fuel(word, word_eol):
    return "Hi there! Do you require fuel?"


@fact
def join(word, word_eol):
    return "If you'd like to look into joining the FuelRats, type \"/join #ratchat\". We'll get you started there."


commands = {
    "set": set_,
    "help": help_,
    "start": start,
    "startcr": startcr,
    "add-rats": add_rats,
    "wing": wing,
    "beacon": beacon,
    "tips": tips,
    "tips-db": tips_db,
    "db-channel": db_channel,
    "enroute": enroute,
    "long": long_trip,
    "need-fuel": need_fuel,
    "join": join
}
""" :var Assigns to each command their function. """


# Initialization

def init():
    """
    Run a single time upon plugin load.
    Sets `config_path` depending on the OS and reads `config` or creates a new one if necessary.
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
        print(__module_name__ + ": Config file loaded from " + config_path)
    else:
        config = {
            "cmd_char": DEFAULT_CHAR
        }
        write_config()
        print("\002{0}\002\nThis seems to be your first time loading this plugin.\nBy default commands begin with {1}."
              " Type {1}set cmd_char <new character> to change this.".format(__module_name__, DEFAULT_CHAR))


# Hook functions

def on_send(word, word_eol, userdata):
    """
    Hook function, called upon all commands / messages the user sends.
    If the message is a script command, parses it and calls the corresponding function.

    Official HexChat Python interface documentation: http://hexchat.readthedocs.io/en/latest/script_python.html
    """
    if word_eol[0].strip().startswith(config["cmd_char"]) and len(word[0]) > 1:
        word[0] = word[0].lstrip(config["cmd_char"])
        word_eol[0] = word_eol[0].replace(config["cmd_char"], "", 1)

        if word[0] in commands.keys():
            commands[word[0]](word, word_eol)
        else:
            print("Command " + word[0] + " not available, " + config["cmd_char"] + "help for a list of all commands.")

        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


init()
hexchat.hook_command("", on_send)

print(__module_name__ + " loaded successfully.")
