import os

import validators
from pyfiglet import figlet_format
from PyInquirer import Token, ValidationError, Validator, prompt, style_from_dict
from termcolor import colored

try:
    import colorama

    colorama.init()
except ImportError:
    colorama = None


style = style_from_dict(
    {
        Token.QuestionMark: "#fac731 bold",
        Token.Answer: "#4688f1 bold",
        Token.Instruction: "",  # default
        Token.Separator: "#cc5454",
        Token.Selected: "#0abf5b",  # default
        Token.Pointer: "#673ab7 bold",
        Token.Question: "",
    }
)


class FilePathValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if os.path.isfile(value.text):
                return True
            else:
                raise ValidationError(message="File not found", cursor_position=len(value.text))
        else:
            raise ValidationError(message="You can't leave this blank", cursor_position=len(value.text))


class UrlValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if validators.url(value.text):
                return True
            else:
                raise ValidationError(message="File not found", cursor_position=len(value.text))
        else:
            raise ValidationError(message="You can't leave this blank", cursor_position=len(value.text))


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)


def ask_information(auto: bool = False) -> None:
    questions = [
        {
            "type": "input",
            "name": "playlist_url",
            "message": "Enter playlist url:",
            "validate": UrlValidator,
            "default": os.getenv("PL"),
            "when": lambda a: not auto,
        },
        {
            "type": "input",
            "name": "playlist_config_path",
            "message": "Enter playlist config path:",
            "validate": FilePathValidator,
            "default": os.getenv("CONFIG_FILE_PATH"),
            "when": lambda a: os.getenv("CONFIG_FILE_PATH") is None,
            # "filter": lambda val: open(val).read(),
        },
        {
            "type": "input",
            "name": "strm_output_path",
            "message": "Enter strm output path:",
            "validate": FilePathValidator,
            "default": os.getenv("STRM_OUTPUT_PATH"),
            "when": lambda a: os.getenv("STRM_OUTPUT_PATH") is None,
            # "filter": lambda val: open(val).read(),
        },
        {
            "type": "confirm",
            "name": "generate",
            "message": "Do you want to generate now",
            "when": lambda a: not auto,
        },
    ]

    answers = prompt(questions, style=style)
    return answers
