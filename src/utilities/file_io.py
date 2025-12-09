"""
Handles all file reading/writing in a consistent and safe way.
Controllers should NOT touch disk operations directly.
"""
import pathlib
from pathlib import Path
import xml.etree.ElementTree as ET
import re 

## I/O operations

def read_file(path: str) -> [bool, str]:
    """
    Reads a file and returns (success, content or error message).
    This avoids exceptions leaking into controllers.
    """
    try:
        content = Path(path).read_text(encoding="utf-8")
        return True, content
    except Exception as e:
        return False, str(e)


def write_file(path: str, data: str, is_xml: bool = True) -> [bool, str]:
    """
    Writes data to a file in UTF-8. Optionally formats XML data before writing.
    Returns (success, message).
    """
    try:
        if "\\n" in data:
            data = data.replace("\\n", "\n")
        if is_xml:
            final_data = pretty_format(data) #adds indentation and new lines
        else:
            final_data = data                #return raw data
        
        with open(path, "w", encoding="utf-8") as file:
            file.write(final_data)           #write to disk (formatted or raw)
        
        message = "File written successfully."
        if is_xml:
            message = "XML file written successfully with formatting."
            
        return True, message
    except OSError as e:
        return False, f"File error: {e}"

def _indent(elem, level=0, indent="    "):
    """
    Recursively adds indentation (whitespace and newlines) to an ElementTree element.
    This modifies the Element in-place. Used internally by pretty_format.
    """
    i = "\n" + level * indent                               #calculate needed indentation
    if len(elem):                                           #check if the tag has children
        if not elem.text or not elem.text.strip():          #check if text is empty
            elem.text = i + indent
        for subelem in elem:                                #recurse into children
            _indent(subelem, level + 1, indent)
        if not subelem.tail or not subelem.tail.strip():    #check if tail is empty
            subelem.tail = i
    else:
        if level and not elem.tail or not elem.tail.strip():
            elem.tail = i

def pretty_format(xml: str, indent: str = "    ") -> str:
    """
    Pretty-format an XML string using xml.etree.ElementTree and a custom indent routine (no minidom).

    Args:
        xml (str): The raw XML string to be formatted.
        indent (str): The string to use for indentation (default is 4 spaces).

    Returns:
        str: The formatted XML string, or the original string on failure.
    """
    try:
        root = ET.fromstring(xml)
        _indent(root, indent=indent)
        formatted_xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)    #convert back to bytes
        
        return formatted_xml_bytes.decode('utf-8')                          #decode bytes to string and return
    
    except ET.ParseError as e:                                              #catch XML parsing errors
        print(f"Warning: Failed to parse XML for formatting: {e}")                         
        return xml
    except Exception as e:                                                  #catch all other errors
        print(f"Warning: An unexpected error occurred during formatting: {e}")      
        return xml

def minify_xml(xml_string: str) -> str:
    """
    Minify an XML string by removing unnecessary whitespace and indentations.
    """
    xml_string = re.sub(r'>\s+<', '><', xml_string)     #\s+ is a regex for whitespace characters (space \s, tab \t, new line \n)
    xml_string = xml_string.strip()
    return xml_string