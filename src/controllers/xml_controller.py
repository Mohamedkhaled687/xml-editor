import textwrap  # Imported to handle clean text wrapping

from typing import List

class XMLController:
    """
    Main controller class for parsing, formatting with text-wrapping,
    and minifying XML strings.
    """
    def __init__(self, xml: str = None):
        self.xml_string: str = xml

    # --- 1. HELPER METHOD (Setter, Getter, Tokenizer) ---
    def set_xml_string(self, xml_string: str):
        self.xml_string = xml_string

    def get_xml_string(self) -> str:
        return self.xml_string
    
    def _get_tokens(self) -> List:
        """
        Parses a raw XML string into a structured list of tokens.
        """
        tokens = []
        i = 0
        length = len(self.xml_string)

        while i < length:
            if self.xml_string[i] == '<':
                j = self.xml_string.find('>', i)
                if j == -1: break
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

    # --- 2. FORMAT METHOD (With Wrap Logic) ---
    def format(self) -> str:
        """
        Reconstructs the XML.
        - Short text nodes stay on one line: <name>Value</name>
        - Long text nodes (like <body>) are wrapped across multiple lines
          and indented correctly.
        """
        tokens = self._get_tokens()
        formatted = []
        level = 0
        indentation = "    "
        k = 0

        # Configuration for text wrapping
        MAX_WIDTH = 80  # Max characters per line for text content

        while k < len(tokens):
            token = tokens[k]

            # --- Scenario A: Closing Tag ---
            if token.startswith('</'):
                level = max(0, level - 1)
                formatted.append((indentation * level) + token)

            # --- Scenario B: Opening Tag ---
            elif token.startswith('<') and not token.startswith('</'):

                # Check for "Leaf Node" (Open -> Text -> Close)
                if (k + 2 < len(tokens) and
                        not tokens[k + 1].startswith('<') and
                        tokens[k + 2].startswith('</')):

                    # 1. Get and Clean Text
                    # We remove existing newlines to treat it as one text block first
                    text_content = tokens[k + 1]
                    clean_text = " ".join(text_content.split())

                    # 2. DECISION: Wrap or Inline?
                    if len(clean_text) > MAX_WIDTH:
                        # --- LONG TEXT LOGIC (Wrap) ---

                        # A. Append Opening Tag (Normal Indent)
                        formatted.append((indentation * level) + tokens[k])

                        # B. Wrap the text
                        # using textwrap to break text nicely at spaces
                        wrapper = textwrap.TextWrapper(width=MAX_WIDTH, break_long_words=False)
                        wrapped_lines = wrapper.wrap(clean_text)

                        # C. Append Wrapped Lines (Indent + 1 Level)
                        for line in wrapped_lines:
                            formatted.append((indentation * (level + 1)) + line)

                        # D. Append Closing Tag (Normal Indent, on new line)
                        formatted.append((indentation * level) + tokens[k + 2])

                    else:
                        # --- SHORT TEXT LOGIC (Inline) ---
                        # Keep <tag>text</tag> on a single line
                        line = (indentation * level) + tokens[k] + clean_text + tokens[k + 2]
                        formatted.append(line)

                    # Skip the next two tokens (text and close tag)
                    k += 2

                else:
                    # Parent Tag
                    formatted.append((indentation * level) + token)
                    level += 1

            # --- Scenario C: Loose Text (Fallback) ---
            else:
                formatted.append((indentation * level) + token.strip())

            k += 1

        return "\n".join(formatted)

    # --- 3. MINIFY METHOD ---
    def minify(self) -> str:
        tokens = self._get_tokens()
        return "".join(tokens)