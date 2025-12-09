"""
XML Controller - Handles XML parsing, validation, and formatting operations.
It manages the XML state and relies on the utilities package for low-level tasks.
"""

import xml.etree.ElementTree as ET
import re
from ..utilities import file_io
from ..utilities import token_utils


class XMLController:
    """Controller for XML-related operations."""
    
    def __init__(self):
        self.xml_tree = None
        self.xml_data = None
        self.current_file_path = ""
        self.user_record_count = 0
    
    def parse_xml_file(self, file_path):       #assuming the file is already structurally valid
        """
        Parse an XML file and load the data into the controller state.
        
        Returns:
            tuple: (success: bool, message: str, user_count: int)
        """
        try:
            self.xml_tree = ET.parse(file_path)
            self.xml_data = self.xml_tree.getroot()
            self.current_file_path = file_path
            self.user_record_count = len(self.xml_data.findall('.//user'))
            return True, f"File loaded successfully. Found {self.user_record_count} user records.", self.user_record_count
        except ET.ParseError as e:
            return False, f"XML parsing failed: {str(e)}", 0
        except FileNotFoundError:
            return False, f"File not found: {file_path}", 0
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", 0

    def format_xml_file(self, file_path):
        """
        Prettifies (formats) the XML file content and saves it back.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            success, raw_content = file_io.read_file(file_path)         #read content
            if not success:                                             #check if failed
                 return False, f"Failed to read file for formatting: {raw_content}"
                 
            success, message = file_io.write_file(file_path, raw_content, is_xml=True)
            
            if success:                                         
                self.xml_tree = ET.parse(file_path)             #reload the formatted XML
                self.xml_data = self.xml_tree.getroot()         #update internal state to reflect changes
                self.user_record_count = len(self.xml_data.findall('.//user'))
                return True, f"XML file formatted successfully. {message}"
            else:
                return False, f"Failed to save formatted XML: {message}"
                
        except ET.ParseError as e:                      #catch XML parsing errors 
            return False, f"XML parsing failed during formatting check: {str(e)}"
        except Exception as e:                          #catch other errors    
            return False, f"Failed to format XML: {str(e)}"