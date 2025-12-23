"""
Handles all file reading/writing in a consistent and safe way.
Controllers should NOT touch disk operations directly.
"""
import re
import pathlib
from pathlib import Path
from typing import Tuple, Union


def read_file(path: str) -> Tuple[bool, str]:
    """
    Reads a file and returns (success, content or error message).
    This avoids exceptions leaking into controllers or CLI.
    """
    try:
        content = Path(path).read_text(encoding="utf-8")
        return True, content
    except Exception as e:
        return False, str(e)

def pretty_format(xml: str, indent: str = "    ") -> str:
    """
    Pretty-format an XML string with indentation based on tag scope.
    """
    # Tokenize by tags or text
    tokens = re.findall(r"<[^>]+>|[^<]+", xml)

    formatted = []
    level = 0

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        if token.startswith("<?") and token.endswith("?>"):
            # XML declaration
            formatted.append(token)

        elif token.startswith("</"):
            # Closing tag: decrease indent first
            level -= 1
            formatted.append(f"{indent * level}{token}")

        elif token.endswith("/>"):
            # Self-closing tag: same level
            formatted.append(f"{indent * level}{token}")

        elif token.startswith("<"):
            # Opening tag: print then increase level
            formatted.append(f"{indent * level}{token}")
            level += 1

        else:
            # Text node: print at current level
            formatted.append(f"{indent * level}{token}")

    return "\n".join(formatted)


def write_file(path: str, data: str) -> Tuple[bool, str]:
    """
    Writes data to a file in UTF-8.
    Returns (success, message).
    """
    try:
        if "\\n" in data:
            data = data.replace("\\n", "\n")
        formatted = pretty_format(data)
        with open(path, "w", encoding="utf-8") as file:
            file.write(formatted)
        return True, "XML file written successfully with formatting."
    except OSError as e:
        return False, f"File error: {e}"


def write_binary(path: str, data: bytes) -> Tuple[bool, str]:
    """
    Writes binary data (used by compress/decompress).
    """
    try:
        Path(path).write_bytes(data)
        return True, "Binary file saved successfully."
    except Exception as e:
        return False, str(e)


def read_binary(path: str) -> Tuple[bool, Union[bytes, str]]:
    """
    Reads binary data safely.
    """
    try:
        content = Path(path).read_bytes()
        return True, content
    except Exception as e:
        return False, str(e)

# remove the following comments to run demo

# p = pathlib.Path("C:/Users/youss/OneDrive/Desktop/Kolya/DSA/trial/Py_GUI/assets/samples/Non_formatted_sample.xml")
#
# txt = read_file(str(p))[1]
#
# b = pathlib.Path("C:/Users/youss/OneDrive/Desktop/Kolya/DSA/trial/Py_GUI/assets/samples/file_io_result.xml")
# print(write_file(path=str(b), data=str(txt)))

