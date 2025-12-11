"""
XMLController Module
====================
This module provides functionality for XML parsing, formatting, minification,
and validation.

Key Features:
- Parse XML strings into tokens
- Format XML with proper indentation (4 spaces per level)
- Wrap long text content across multiple lines (80 char limit)
- Minify XML by removing all whitespace
- Validate XML structure and semantics

Author: [Your Name]
Date: [Date]
"""

import textwrap
import re
from typing import List


class XMLController:
    """
    Main controller class for parsing, formatting, minifying, and validating
    XML strings.

    This class provides methods to:
    1. Parse raw XML into structured tokens
    2. Format XML with intelligent indentation and text wrapping
    3. Minify XML by removing all unnecessary whitespace
    4. Validate XML for structural and semantic errors

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
        """
        tokens = []
        i = 0
        length = len(self.xml_string)

        while i < length:
            if self.xml_string[i] == '<':
                j = self.xml_string.find('>', i)

                if j == -1:
                    break

                tag = self.xml_string[i:j + 1]
                tokens.append(tag)
                i = j + 1

            else:
                j = i

                while j < length and self.xml_string[j] != '<':
                    j += 1

                raw_text = self.xml_string[i:j]

                if not raw_text.strip():
                    i = j
                    continue

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
        """
        tokens = self._get_tokens()
        formatted = []
        level = 0
        indentation = "    "
        k = 0
        MAX_WIDTH = 80

        while k < len(tokens):
            token = tokens[k]

            if token.startswith('</'):
                level = max(0, level - 1)
                formatted.append((indentation * level) + token)

            elif token.startswith('<') and not token.startswith('</'):
                if (k + 2 < len(tokens) and
                        not tokens[k + 1].startswith('<') and
                        tokens[k + 2].startswith('</')):

                    text_content = tokens[k + 1]
                    clean_text = " ".join(text_content.split())

                    if len(clean_text) > MAX_WIDTH:
                        formatted.append((indentation * level) + tokens[k])
                        wrapper = textwrap.TextWrapper(
                            width=MAX_WIDTH,
                            break_long_words=False
                        )
                        wrapped_lines = wrapper.wrap(clean_text)
                        for line in wrapped_lines:
                            formatted.append((indentation * (level + 1)) + line)
                        formatted.append((indentation * level) + tokens[k + 2])
                    else:
                        line = (indentation * level) + tokens[k] + clean_text + tokens[k + 2]
                        formatted.append(line)

                    k += 2
                else:
                    formatted.append((indentation * level) + token)
                    level += 1
            else:
                formatted.append((indentation * level) + token.strip())

            k += 1

        return "\n".join(formatted)

    # ===================================================================
    # SECTION 3: MINIFY METHOD
    # ===================================================================

    def minify(self) -> str:
        """
        Minify the XML by removing all whitespace and newlines.

        Returns:
            str: Minified XML string (single line, no spaces)
        """
        tokens = self._get_tokens()
        return "".join(tokens)

    # ===================================================================
    # SECTION 4: VALIDATION METHOD (XML Consistency Checker)
    # ===================================================================

    def validate(self):
        """
        Parses self.xml_string, detects structural errors, and returns a new string
        where errors are annotated with '<---' at the end of the problematic lines.
        """
        stack = []

        # Split string into a list of lines.
        # We will modify this list directly to add annotations.
        lines = self.xml_string.split('\n')

        # We create a separate list for output to avoid modifying the logic
        # while iterating (though strings are immutable, this keeps it clean).
        annotated_lines = lines[:]

        for line_idx, line in enumerate(lines):
            # Regex to find tags: captures <tag> or </tag>
            # Group 1: '/' if closing, empty if opening
            # Group 2: The tag name
            tags = re.finditer(r'<(/?)(\w+)[^>]*>', line)

            for match in tags:
                is_closing = match.group(1) == '/'
                tag_name = match.group(2)

                if not is_closing:
                    # OPENING TAG: Push tag name and Line Index to stack
                    stack.append({'tag': tag_name, 'line_idx': line_idx})
                else:
                    # CLOSING TAG
                    if not stack:
                        # Error: Closing tag found, but stack is empty
                        annotated_lines[line_idx] += f" <--- ORPHAN TAG: Found </{tag_name}> but no opening tag exists."
                    else:
                        top = stack[-1]
                        if top['tag'] == tag_name:
                            # Match found, valid pair
                            stack.pop()
                        else:
                            # Error: Mismatch
                            # We found a closing tag, but it doesn't match the most recent opening tag.
                            annotated_lines[
                                line_idx] += f" <--- MISMATCH: Expected </{top['tag']}>, found </{tag_name}>."

                            # Logic Decision:
                            # We do NOT pop the stack here. We assume the current closing tag is the error
                            # and the previous opening tag still needs a mate later on.

        # After processing all lines, check if the stack is not empty.
        # These are tags that were opened but never closed.
        while stack:
            leftover = stack.pop()
            # We go back to the line where this tag was opened and add the error there
            idx = leftover['line_idx']
            annotated_lines[idx] += f" <--- MISSING CLOSING TAG: Tag <{leftover['tag']}> is never closed."

        # Join the lines back into a single string to be displayed in the UI text box
        return "\n".join(annotated_lines)

    def autocorrect(self):
        """
        Attempts to fix the XML by balancing tags.
        Returns the fixed XML string and updates self.xml_string.
        """
        stack = []
        fixed_lines = []

        # We need to parse slightly differently: we want to rebuild the string
        # Regex to tokenize: Tag OR non-tag content
        tokens = re.split(r'(<[^>]+>)', self.xml_string)

        corrected_output = []

        for token in tokens:
            if not token:
                continue

            # Check if this token is a tag
            match = re.match(r'<(/?)(\w+)[^>]*>', token)

            if match:
                is_closing = match.group(1) == '/'
                tag_name = match.group(2)

                if not is_closing:
                    # OPENING TAG
                    stack.append(tag_name)
                    corrected_output.append(token)
                else:
                    # CLOSING TAG
                    if stack and stack[-1] == tag_name:
                        # Perfectly matches
                        stack.pop()
                        corrected_output.append(token)
                    else:
                        # MISMATCH SCENARIO
                        # Strategy: If it matches a parent higher up, close the intermediates.
                        # If it matches nothing, ignore it (delete stray closing tag).

                        if tag_name in stack:
                            # It is valid, but we forgot to close something in between
                            # Example: <a> <b> </a> -> We need to close <b> first
                            while stack[-1] != tag_name:
                                missing_tag = stack.pop()
                                corrected_output.append(f"</{missing_tag}>")

                            # Now pop the matching tag
                            stack.pop()
                            corrected_output.append(token)
                        else:
                            # It's a stray closing tag that wasn't opened. Ignore/Delete it.
                            pass
            else:
                # Just text content, append as is
                corrected_output.append(token)

        # Final cleanup: Close any tags left open at the end
        while stack:
            missing_tag = stack.pop()
            corrected_output.append(f"</{missing_tag}>")

        # Update the class attribute
        self.xml_string = "".join(corrected_output)
        return self.format()
