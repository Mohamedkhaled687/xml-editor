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
import json
from typing import List, Tuple, Optional
from utils.binary_utils import ByteUtils


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
        self.xml_data: Optional[None] = None  # placeholder for parsed XML data structure,avoid attributes error
        if xml: self.set_xml_string(xml)  # initialize with provided XML

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
        self.xml_data = None  # reset parsed data structure

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

    def _get_tag_info(self, token: str) -> Tuple[str, dict]:
        """
        Custom parser helper to extract tag name and attributes from a token.
        """
        tag_content = token.strip('<>').strip('/')  # remove angle brackets and slashes

        tag_name = tag_content.split(' ')[0]  # extract tag name
        attributes = {}  # dictionary to hold attributes
        # use regex to find all attribute in " " and appends with those in ''
        attr_matches = re.findall(r'(\w+)="([^"]*)"', tag_content) + \
                       re.findall(r"(\w+)='([^']*)'", tag_content)

        for name, value in attr_matches:
            attributes[name] = value.strip()

        return tag_name, attributes

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

    # ===================================================================
    # SECTION 5: JSON EXPORT METHOD
    # ===================================================================

    def export_to_json(self, file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Export XML data to JSON format and save it to a file.


        Args:
            file_path: Path to save the JSON file

        Returns:
            tuple: (success: bool, message: str, error: str)
        """
        if self.xml_string is None:
            return False, "", "No data loaded. Please set a valid XML file first."

        try:
            tokens = self._get_tokens()
            json_data = {"users": []}

            # state variables for custom parsing
            user_dict = None
            post_dict = None
            relationship_dict = None  # NEW: state variable to temporarily hold a follower/following object before appending
            current_container = None  # tracks if we are inside 'name', 'body', 'topic', ... etc.
            parent_stack = []  # Stack to track parent tag hierarchy for proper context
            i = 0
            while i < len(tokens):
                token = tokens[i]

                # ---------------------------------------------------------------
                # CASE A: Opening Tag (e.g., <user>, <name>)
                # ---------------------------------------------------------------
                if token.startswith('<') and not token.startswith('</'):
                    tag_name, attrs = self._get_tag_info(token)

                    if tag_name == 'user':
                        # start of a new user record
                        user_dict = {
                            "id": attrs.get('id'),  # extract ID from attribute
                            "name": None,
                            "posts": [],
                            "followers": [],
                            "followings": []
                        }

                    elif tag_name == 'post' and user_dict is not None:
                        # start of a new post record
                        post_dict = {
                            "content": None,
                            "topics": []
                        }
                    elif tag_name == 'follower' or tag_name == 'following':  # NEW: If we start a relationship tag
                        relationship_dict = {}  # NEW: Initialize the object we need to build, e.g., {"id": "..."}
                    # set the current container tag (e.g., 'name', 'id' inside follower)
                    # Push opening tag onto the parent stack
                    parent_stack.append(tag_name)
                    current_container = tag_name

                # ---------------------------------------------------------------
                # CASE B: Closing Tag (e.g., </user>, </name>)
                # ---------------------------------------------------------------
                elif token.startswith('</'):
                    tag_name, _ = self._get_tag_info(token)

                    if tag_name == 'user' and user_dict is not None:
                        # end of user record, finalize and append
                        json_data["users"].append(user_dict)
                        user_dict = None

                    elif tag_name == 'post' and user_dict is not None and post_dict is not None:
                        # end of post record, finalize and append
                        user_dict["posts"].append(post_dict)
                        post_dict = None

                    elif tag_name == 'follower' and user_dict is not None and relationship_dict is not None:  # NEW: When </follower> closes
                        user_dict["followers"].append(
                            relationship_dict)  # NEW: Append the complete {"id": "X"} object to the list.
                        relationship_dict = None  # NEW: Reset the temporary relationship dict.

                    elif tag_name == 'following' and user_dict is not None and relationship_dict is not None:  # NEW: When </following> closes
                        user_dict["followings"].append(
                            relationship_dict)  # NEW: Append the complete {"id": "X"} object to the list.
                        relationship_dict = None  # NEW: Reset the temporary relationship dict.
                    # Pop closing tag from the parent stack
                    if parent_stack and parent_stack[-1] == tag_name:
                        parent_stack.pop()
                    current_container = None

                # ---------------------------------------------------------------
                # CASE C: Text Content
                # ---------------------------------------------------------------
                else:
                    text_content = token.strip()
                    if not text_content:
                        i += 1
                        continue

                    # assign content based on the most recently opened relevant tag
                    if current_container == 'name' and user_dict is not None and user_dict["name"] is None:
                        user_dict["name"] = text_content

                    elif (current_container == 'body' or current_container == 'content') and post_dict is not None and \
                            post_dict["content"] is None:
                        post_dict["content"] = text_content

                    elif current_container == 'topic' and post_dict is not None:
                        post_dict["topics"].append(text_content)


                    elif current_container == 'id':
                        # Use parent stack to determine the correct context
                        # parent_stack[-1] is 'id', parent_stack[-2] is the parent tag
                        parent_tag = parent_stack[-2] if len(parent_stack) >= 2 else None

                    if parent_tag in ('follower', 'following') and relationship_dict is not None:
                        # ID inside a follower or following tag
                        relationship_dict["id"] = text_content
                    elif parent_tag == 'user' and user_dict is not None:
                        # ID inside a user tag (but not inside a follower/following)
                        if user_dict["id"] is None:  # Only assign if not already set by attribute
                            user_dict["id"] = text_content

                    current_container = None  # reset container state after text processing

                i += 1

            # final check
            final_user_count = len(json_data["users"])

            # handle file I/O
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            return True, f"Successfully exported {final_user_count} users to JSON. File saved: {file_path}", None

        except Exception as e:
            return False, "", f"Failed to export to JSON using custom parser: {str(e)}"



"""
    # ===================================================================
    # SECTION 5: Compression and Decompression
    # ===================================================================

    def compress_to_string(self) -> str:
        if not self.xml_string:
            return ""

        tokens = [ord(c) for c in self.xml_string]
        merges = []  # List to preserve order
        next_token = 256

        for _ in range(100):
            pair_counts = {}
            for i in range(len(tokens) - 1):
                key = (tokens[i] << 16) | tokens[i + 1]
                pair_counts[key] = pair_counts.get(key, 0) + 1

            if not pair_counts:
                break

            most_key = None
            most_count = 0
            for key, count in pair_counts.items():
                if count > most_count:
                    most_count = count
                    most_key = key

            if most_count < 2:
                break

            # Store with creation order
            merges.append((most_key, next_token))

            # Merge pass
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1:
                    key = (tokens[i] << 16) | tokens[i + 1]
                    if key == most_key:
                        new_tokens.append(next_token)
                        i += 2
                        continue
                new_tokens.append(tokens[i])
                i += 1

            tokens = new_tokens
            next_token += 1

        # Serialize
        out = bytearray()
        out.extend(ByteUtils.pack_u32(len(merges)))

        for key, merged in merges:
            t1 = (key >> 16) & 0xFFFF
            t2 = key & 0xFFFF
            out.extend(ByteUtils.pack_u16(t1))
            out.extend(ByteUtils.pack_u16(t2))
            out.extend(ByteUtils.pack_u16(merged))

        out.extend(ByteUtils.pack_u32(len(tokens)))
        for t in tokens:
            out.extend(ByteUtils.pack_u16(t))

        return bytes([b if b < 256 else 63 for b in out]).decode("latin-1")

    def decompress_from_string(self, compressed_string: str) -> None:
        data = bytearray(compressed_string.encode("latin-1"))
        offset = 0

        merge_count = ByteUtils.unpack_u32(data, offset)
        offset += 4

        # Store merges in creation order
        merges = []
        for _ in range(merge_count):
            t1 = ByteUtils.unpack_u16(data, offset)
            offset += 2
            t2 = ByteUtils.unpack_u16(data, offset)
            offset += 2
            merged = ByteUtils.unpack_u16(data, offset)
            offset += 2
            merges.append((merged, t1, t2))

        token_count = ByteUtils.unpack_u32(data, offset)
        offset += 4

        tokens = []
        for _ in range(token_count):
            tokens.append(ByteUtils.unpack_u16(data, offset))
            offset += 2

        # Expand in REVERSE creation order
        for merged_token, t1, t2 in reversed(merges):
            new_tokens = []
            for t in tokens:
                if t == merged_token:
                    new_tokens.append(t1)
                    new_tokens.append(t2)
                else:
                    new_tokens.append(t)
            tokens = new_tokens

        self.xml_string = ''.join(chr(t) for t in tokens)

"""