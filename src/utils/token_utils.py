"""
Utilities for scanning and tokenizing XML strings.
This file contains simple, reusable helpers
that other controllers (formatter, validator, parser) can depend on.
"""

from typing import List
import pathlib
from .file_io import read_file


def is_opening_tag(token: str) -> bool:
    """Returns True if token is an opening XML tag <...>."""
    return token.startswith("<") and token.endswith(">") and not token.startswith("</")


def is_closing_tag(token: str) -> bool:
    """Returns True if token is a closing XML tag </...>."""
    return token.startswith("</") and token.endswith(">")


def extract_tag_name(token: str) -> str:
    """
    Extracts the tag name from <tag> or </tag>.
    Always returns lowercase to ensure consistent comparisons.
    """
    token = token.strip("<>").strip("/")
    return token.lower()


def tokenize(xml_string: str) -> List[str]:
    """
    Splits XML into tokens:
    - Opening tags
    - Closing tags
    - Text content
    Simplest version: used in validator and parser.
    """
    tokens = []
    buffer = ""
    inside_tag = False

    for ch in xml_string:
        if ch == "<":
            if buffer.strip():
                tokens.append(buffer.strip())
            buffer = "<"
            inside_tag = True
        elif ch == ">":
            buffer += ">"
            tokens.append(buffer)
            buffer = ""
            inside_tag = False
        else:
            buffer += ch

    if buffer.strip():
        tokens.append(buffer.strip())

    return tokens

# remove the following comments to run demo

# p = pathlib.Path("C:/Users/youss/OneDrive/Desktop/Kolya/DSA/trial/Py_GUI/assets/samples/Non_formatted_sample.xml")
#
# txt = read_file(str(p))[1]
#
# tokens = tokenize(txt)
#
# for token in tokens:
#     print(token)

