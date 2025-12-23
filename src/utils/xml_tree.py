"""
Custom XML Tree Implementation - A tree data structure for parsing XML.
Implements a tree without using Python's xml.etree.ElementTree.
"""

from typing import Dict, List, Optional, Tuple
import re


class XMLNode:
    """Represents a node in the XML tree."""
    
    def __init__(self, tag: str, attributes: Dict[str, str] = None, text: str = None):
        self.tag = tag
        self.attributes = attributes or {}
        self.text = text
        self.children: List['XMLNode'] = []
        self.parent: Optional['XMLNode'] = None
    
    def add_child(self, child: 'XMLNode') -> None:
        """Add a child node to this node."""
        child.parent = self
        self.children.append(child)
    
    def get(self, attribute: str, default: str = None) -> Optional[str]:
        """Get an attribute value."""
        return self.attributes.get(attribute, default)
    
    def find(self, tag: str) -> Optional['XMLNode']:
        """Find first direct child with given tag."""
        for child in self.children:
            if child.tag == tag:
                return child
        return None
    
    def findall(self, path: str) -> List['XMLNode']:
        """
        Find all matching elements.
        Supports simple paths like 'tag' or './/tag' (recursive).
        """
        if path.startswith('.//'):
            # Recursive search
            tag = path[3:]
            return self._find_recursive(tag)
        else:
            # Direct children only
            return [child for child in self.children if child.tag == path]
    
    def _find_recursive(self, tag: str) -> List['XMLNode']:
        """Recursively find all nodes with given tag."""
        results = []
        for child in self.children:
            if child.tag == tag:
                results.append(child)
            results.extend(child._find_recursive(tag))
        return results
    
    def __repr__(self) -> str:
        return f"XMLNode(tag='{self.tag}', children={len(self.children)})"


class XMLTree:
    """
    Custom XML parser that builds a tree structure.
    Parses XML string into XMLNode tree without using ElementTree.
    """
    
    def __init__(self):
        self.root: Optional[XMLNode] = None

    def get_root(self):
        return self.root

    @staticmethod
    def fromstring(xml_string: str) -> XMLNode:
        """Parse XML string and return root element."""
        parser = XMLTree()
        return parser._parse_string(xml_string)
    
    @staticmethod
    def parse(file_path: str) -> XMLNode:
        """Parse XML file and return root element."""
        with open(file_path, 'r', encoding='utf-8') as f:
            xml_string = f.read()
        return XMLTree.fromstring(xml_string)
    
    def _parse_string(self, xml_string: str) -> XMLNode:
        """Parse XML string into tree structure."""
        # Remove XML declaration if present
        xml_string = re.sub(r'<\?xml[^?]*\?>', '', xml_string).strip()
        
        # Remove comments
        xml_string = re.sub(r'<!--.*?-->', '', xml_string, flags=re.DOTALL)
        
        # Parse the root element
        self.root = self._parse_element(xml_string)
        return self.root
    
    def _parse_element(self, xml_string: str) -> Optional[XMLNode]:
        """Parse a single XML element and its children."""
        xml_string = xml_string.strip()
        if not xml_string:
            return None
        
        # Match opening tag with attributes
        open_tag_match = re.match(r'<(\w+)([^>]*)>', xml_string)
        if not open_tag_match:
            return None
        
        tag_name = open_tag_match.group(1)
        attributes_str = open_tag_match.group(2)
        
        # Parse attributes
        attributes = self._parse_attributes(attributes_str)
        
        # Check if self-closing tag
        if attributes_str.rstrip().endswith('/'):
            return XMLNode(tag_name, attributes)
        
        # Find matching closing tag
        content_start = open_tag_match.end()
        close_tag = f'</{tag_name}>'
        close_pos = self._find_matching_close_tag(xml_string, tag_name, content_start)
        
        if close_pos == -1:
            # No closing tag found, treat as self-closing
            return XMLNode(tag_name, attributes)
        
        # Extract content between tags
        content = xml_string[content_start:close_pos].strip()
        
        # Create node
        node = XMLNode(tag_name, attributes)
        
        # Parse content (text and/or child elements)
        if content:
            self._parse_content(node, content)
        
        return node
    
    def _parse_attributes(self, attr_string: str) -> Dict[str, str]:
        """Parse attribute string into dictionary."""
        attributes = {}
        # Match attribute="value" or attribute='value'
        pattern = r'(\w+)\s*=\s*["\']([^"\']*)["\']'
        matches = re.findall(pattern, attr_string)
        for name, value in matches:
            attributes[name] = value
        return attributes
    
    def _find_matching_close_tag(self, xml_string: str, tag_name: str, start_pos: int) -> int:
        """Find the position of the matching closing tag."""
        depth = 1
        pos = start_pos
        open_pattern = re.compile(rf'<{tag_name}(\s|>|/)')
        close_pattern = re.compile(rf'</{tag_name}>')
        
        while pos < len(xml_string) and depth > 0:
            # Find next opening or closing tag
            open_match = open_pattern.search(xml_string, pos)
            close_match = close_pattern.search(xml_string, pos)
            
            if close_match is None:
                return -1
            
            if open_match and open_match.start() < close_match.start():
                # Check if it's not a self-closing tag
                tag_end = xml_string.find('>', open_match.start())
                if tag_end != -1 and xml_string[tag_end-1] != '/':
                    depth += 1
                pos = tag_end + 1
            else:
                depth -= 1
                if depth == 0:
                    return close_match.start()
                pos = close_match.end()
        
        return -1
    
    def _parse_content(self, parent: XMLNode, content: str) -> None:
        """Parse content that may contain text and/or child elements."""
        content = content.strip()
        
        # Check if content is just text (no child elements)
        if not re.search(r'<\w+', content):
            parent.text = content
            return
        
        # Parse mixed content (text and elements)
        pos = 0
        text_parts = []
        
        while pos < len(content):
            # Find next tag
            tag_match = re.search(r'<(\w+)', content[pos:])
            
            if not tag_match:
                # Remaining is text
                remaining = content[pos:].strip()
                if remaining:
                    text_parts.append(remaining)
                break
            
            # Capture text before tag
            text_before = content[pos:pos + tag_match.start()].strip()
            if text_before:
                text_parts.append(text_before)
            
            # Find the complete element
            elem_start = pos + tag_match.start()
            tag_name = tag_match.group(1)
            
            # Find opening tag end
            open_end = content.find('>', elem_start)
            if open_end == -1:
                break
            
            # Check if self-closing
            if content[open_end - 1] == '/':
                # Self-closing tag
                elem_str = content[elem_start:open_end + 1]
                child = self._parse_element(elem_str)
                if child:
                    parent.add_child(child)
                pos = open_end + 1
            else:
                # Find closing tag
                close_pos = self._find_matching_close_tag(content, tag_name, open_end + 1)
                if close_pos == -1:
                    break
                
                close_end = content.find('>', close_pos) + 1
                elem_str = content[elem_start:close_end]
                child = self._parse_element(elem_str)
                if child:
                    parent.add_child(child)
                pos = close_end
        
        # Set text if any
        if text_parts:
            parent.text = ' '.join(text_parts)


class XMLParseError(Exception):
    """Exception raised for XML parsing errors."""
    pass
