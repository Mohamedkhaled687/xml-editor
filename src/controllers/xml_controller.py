"""
XMLController Module
====================
This module provides functionality for XML parsing, formatting, and minification.

Key Features:
- Parse XML strings into tokens
- Format XML with proper indentation (4 spaces per level)
- Wrap long text content across multiple lines (80 char limit)
- Minify XML by removing all whitespace

Author: [Your Name]
Date: [Date]
"""

import textwrap  # Imported to handle clean text wrapping at specified width
from typing import List  # For type hints to improve code readability


class XMLController:
    """
    Main controller class for parsing, formatting with text-wrapping,
    and minifying XML strings.
    
    This class provides methods to:
    1. Parse raw XML into structured tokens
    2. Format XML with intelligent indentation and text wrapping
    3. Minify XML by removing all unnecessary whitespace
    
    Attributes:
        xml_string (str): The XML content to be processed
    """
    
    def __init__(self, xml: str = None):
        """
        Initialize the XMLController with optional XML content.
        
        Args:
            xml (str, optional): Initial XML string to process. Defaults to None.
        
        Example:
            controller = XMLController("<root><child>text</child></root>")
        """
        # Store XML string as instance attribute for use across all methods
        self.xml_string: str = xml

    # ===================================================================
    # SECTION 1: HELPER METHODS (Setter, Getter, Tokenizer)
    # ===================================================================
    
    def set_xml_string(self, xml_string: str):
        """
        Set or update the XML string to be processed.
        
        Args:
            xml_string (str): The new XML content
            
        Example:
            controller.set_xml_string("<person><name>John</name></person>")
        """
        self.xml_string = xml_string

    def get_xml_string(self) -> str:
        """
        Retrieve the current XML string.
        
        Returns:
            str: The current XML content stored in the controller
            
        Example:
            xml = controller.get_xml_string()
        """
        return self.xml_string
    
    def _get_tokens(self) -> List:
        """
        Parse a raw XML string into a structured list of tokens.
        
        This method breaks down XML into its component parts:
        - Opening tags: <tag>, <tag attr="value">
        - Closing tags: </tag>
        - Text content: the text between tags
        
        Returns:
            List: A list of tokens extracted from the XML
            
        Example:
            Input:  "<user><name>Ali</name></user>"
            Output: ['<user>', '<name>', 'Ali', '</name>', '</user>']
            
        Algorithm:
            1. Iterate through the XML string character by character
            2. When '<' is found, extract the complete tag up to '>'
            3. When not in a tag, extract text content up to next '<'
            4. Skip whitespace-only text nodes
        """
        tokens = []  # Initialize empty list to store tokens
        i = 0  # Current position in the XML string
        length = len(self.xml_string)  # Cache length for efficiency

        # Main parsing loop: process entire XML string
        while i < length:
            # CASE 1: Found opening angle bracket - this is a tag
            if self.xml_string[i] == '<':
                # Find the matching closing angle bracket
                j = self.xml_string.find('>', i)
                
                # If no closing '>' found, XML is malformed - stop parsing
                if j == -1: 
                    break
                
                # Extract complete tag including angle brackets
                # Example: "<name>" or "</name>" or "<user id='1'>"
                tag = self.xml_string[i:j + 1]
                tokens.append(tag)
                
                # Move position to after the closing '>'
                i = j + 1
                
            # CASE 2: Not a tag - this is text content
            else:
                j = i
                
                # Find where text content ends (at next '<' or end of string)
                while j < length and self.xml_string[j] != '<':
                    j += 1
                
                # Extract text content between current position and next tag
                raw_text = self.xml_string[i:j]
                
                # Skip empty or whitespace-only text nodes
                # Example: "   \n   " would be skipped
                if not raw_text.strip():
                    i = j
                    continue
                
                # Add trimmed text to tokens (removes leading/trailing whitespace)
                tokens.append(raw_text.strip())
                i = j
                
        return tokens

    # ===================================================================
    # SECTION 2: FORMAT METHOD (Main Formatting Logic)
    # ===================================================================
    
    def format(self) -> str:
        """
        Reconstruct and format the XML with proper indentation and text wrapping.
        
        Formatting Rules:
        1. Each nesting level is indented by 4 spaces
        2. Short text (≤80 chars) stays inline: <name>Value</name>
        3. Long text (>80 chars) is wrapped across multiple lines
        4. Wrapped text is indented one level deeper than its tag
        
        Returns:
            str: Beautifully formatted XML string with newlines
            
        Example:
            Input:  "<user><name>Ali</name><bio>Long text here...</bio></user>"
            Output:
                <user>
                    <name>Ali</name>
                    <bio>
                        Long text here...
                    </bio>
                </user>
        """
        # Step 1: Parse XML into tokens
        tokens = self._get_tokens()
        
        # Step 2: Initialize formatting variables
        formatted = []  # Will store formatted lines
        level = 0  # Current indentation level (0 = root)
        indentation = "    "  # 4 spaces per indentation level
        k = 0  # Current token index

        # Configuration for text wrapping
        MAX_WIDTH = 80  # Maximum characters per line for text content

        # Step 3: Process each token
        while k < len(tokens):
            token = tokens[k]  # Get current token

            # ---------------------------------------------------------------
            # SCENARIO A: Closing Tag (e.g., </user>, </name>)
            # ---------------------------------------------------------------
            if token.startswith('</'):
                # Decrease indentation level (moving back up in XML tree)
                level = max(0, level - 1)  # Use max() to prevent negative levels
                
                # Add closing tag with appropriate indentation
                formatted.append((indentation * level) + token)

            # ---------------------------------------------------------------
            # SCENARIO B: Opening Tag (e.g., <user>, <name>)
            # ---------------------------------------------------------------
            elif token.startswith('<') and not token.startswith('</'):

                # Check if this is a "Leaf Node" pattern: <tag>text</tag>
                # We need 3 consecutive tokens: opening tag, text, closing tag
                if (k + 2 < len(tokens) and  # Ensure we have 2 more tokens
                        not tokens[k + 1].startswith('<') and  # Next token is text (not a tag)
                        tokens[k + 2].startswith('</')):  # Token after that is closing tag

                    # --- LEAF NODE PROCESSING ---
                    
                    # Step 1: Get and clean the text content
                    # Remove existing newlines/extra spaces to treat as one block
                    text_content = tokens[k + 1]
                    clean_text = " ".join(text_content.split())  # Normalize whitespace

                    # Step 2: DECISION - Should we wrap this text or keep it inline?
                    if len(clean_text) > MAX_WIDTH:
                        # ===== LONG TEXT LOGIC (Text Wrapping) =====
                        
                        # A. Add opening tag on its own line (normal indentation)
                        formatted.append((indentation * level) + tokens[k])

                        # B. Wrap the text intelligently at word boundaries
                        # TextWrapper breaks long text at spaces, not mid-word
                        wrapper = textwrap.TextWrapper(
                            width=MAX_WIDTH,  # Max chars per line
                            break_long_words=False  # Don't split words
                        )
                        wrapped_lines = wrapper.wrap(clean_text)

                        # C. Add each wrapped line with deeper indentation (level + 1)
                        # This makes it clear the text belongs to the parent tag
                        for line in wrapped_lines:
                            formatted.append((indentation * (level + 1)) + line)

                        # D. Add closing tag on its own line (back to normal indentation)
                        formatted.append((indentation * level) + tokens[k + 2])

                    else:
                        # ===== SHORT TEXT LOGIC (Inline) =====
                        # Keep everything on one line: <tag>text</tag>
                        line = (indentation * level) + tokens[k] + clean_text + tokens[k + 2]
                        formatted.append(line)

                    # Skip the next two tokens since we've already processed them
                    # (text content and closing tag)
                    k += 2

                else:
                    # --- PARENT TAG (has nested children) ---
                    # Example: <user> that contains <name>, <age>, etc.
                    
                    # Add opening tag with current indentation
                    formatted.append((indentation * level) + token)
                    
                    # Increase indentation level for nested content
                    level += 1

            # ---------------------------------------------------------------
            # SCENARIO C: Loose Text (Fallback - shouldn't normally happen)
            # ---------------------------------------------------------------
            else:
                # This handles any text not caught by the leaf node logic
                # Add it with current indentation, trimmed of whitespace
                formatted.append((indentation * level) + token.strip())

            # Move to next token
            k += 1

        # Step 4: Join all formatted lines with newline characters
        return "\n".join(formatted)

    # ===================================================================
    # SECTION 3: MINIFY METHOD
    # ===================================================================
    
    def minify(self) -> str:
        """
        Minify the XML by removing all whitespace and newlines.
        
        This creates a compact, single-line version of the XML with no
        formatting or indentation. Useful for reducing file size or
        network transmission.
        
        Returns:
            str: Minified XML string (single line, no spaces)
            
        Example:
            Input (formatted):
                <user>
                    <name>Ali</name>
                </user>
            
            Output (minified):
                <user><name>Ali</name></user>
                
        Algorithm:
            1. Parse XML into tokens (tags and text)
            2. Concatenate all tokens directly without any separators
            3. Return as single continuous string
        """
        # Get tokens from the XML
        tokens = self._get_tokens()
        
        # Join all tokens together with no separator (no spaces, no newlines)
        return "".join(tokens)