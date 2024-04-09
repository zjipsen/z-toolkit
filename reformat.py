# -*- coding: utf-8 -*-
from enum import Enum

from prompt_toolkit import HTML, print_formatted_text, PromptSession
from typing import List, Set

import os
import sys
import pdb

class Options(Enum):
    ENTER = 1
    MDASH = 2
    ITALICS = 3

class Reformatter:

    def __init__(self):
        self.enter_str = '<p>&nbsp;</p>'
        self.double_dash = '--'
        self.mdash_str = '&mdash;'
        self.italics_span_open = '</span><em><span style="font-weight: 400;">'
        self.italics_span_close = '</span></em><span style="font-weight: 400;">'
        self.italics_open = '<em>'
        self.italics_close = '</em>'

    def reformat(self, text: str, options: Set[Options]):
        if Options.ENTER in options:
            text = text.replace(self.enter_str, "")
        if Options.MDASH in options:
            text = text.replace(self.double_dash, self.mdash_str)
        if Options.ITALICS in options:
            text = self.italics(text)
        return text
    
    def parse_options(self, user_input_str):
        user_input = set([item.upper() for item in user_input_str.split(" ")])
        abbrev = lambda name: name [0]
        options, valid_options = set(), set()
        for o in Options:
            if o.name in user_input or abbrev(o.name) in user_input:
                options.add(o)
                valid_options.update([o.name, abbrev(o.name)])
        unknown = user_input.difference(valid_options)
        return options, unknown
    
    def italics(self, text: str):
        text = text.replace(self.italics_span_open, self.italics_open)
        text = text.replace(self.italics_span_close, self.italics_close)
        punctuation = [",", ".", self.mdash_str, "?", "!", ]
        invalid_punct = [self.italics_close + " " + p for p in punctuation] + [" " + self.italics_close + p for p in punctuation]
        for index, item in enumerate(invalid_punct):
            if item in text:
                text = text.replace(item, self.italics_close + punctuation[index % len(punctuation)])
        return text


def skyblue(text):
    return f'<skyblue>{text}</skyblue>'

def violet(text):
    return f'<violet>{text}</violet>'

def ask_file_name(session: PromptSession):
    file_name = ""
    for line in sys.argv[1:]:
        file_name = line.rstrip()
        print(f"file name: {file_name}")
    if not file_name:
        # file name was not provided as stdin
        print_formatted_text(HTML(skyblue("Enter the name of the file to be reformatted:")))
        file_name = session.prompt('> ')

    while not os.path.isfile(file_name):
        print_formatted_text(HTML(violet(f"Cannot find file. please try again.")))
        file_name = session.prompt('> ')
    return file_name

def ask_options(session: PromptSession, reformatter: Reformatter):
    print_formatted_text(HTML(skyblue(
        f"Which formatting options? press enter for all. \nAvailable options: {', '.join([o.name for o in Options])}"
        )))
    answer = session.prompt('> ')
    if not answer:
        options = [o for o in Options]
    else:
        options, unknown = reformatter.parse_options(answer)
        if unknown:
            print_formatted_text(HTML(violet(f"Options {', '.join(unknown)} were not known and will be ignored.")))
    print_formatted_text(HTML(skyblue(f"Reformatting using options {', '.join([str(o) for o in options])}.")))
    return options

def write_reformatted(file_name, content):
    file_name_name, file_extension = os.path.splitext(file_name)
    new_file = file_name_name + "_reformatted" + file_extension

    with open(new_file, 'w') as f:
        f.write(content)
    return new_file

def reformat_file():
    print_formatted_text(HTML(skyblue("Reformatting...(exit with control-D)")))
    session = PromptSession()
    reformatter = Reformatter()

    file_name = ask_file_name(session)
    options = ask_options(session, reformatter)
    
    new_contents = None
    with open(file_name, 'r') as f:
        contents = f.read()
        new_contents = reformatter.reformat(contents, options)

    new_file_name = write_reformatted(file_name, new_contents)
    print_formatted_text(HTML(skyblue(f"Reformatted at new file {new_file_name} ")))

def main() -> int:
    """Echo the input arguments to standard output"""
    reformat_file()

if __name__ == '__main__':
    sys.exit(main())
