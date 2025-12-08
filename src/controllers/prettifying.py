class XMLcontroller:
    def format(self, xml_string): 
        # TOKENIZATION
        # Convert raw string into a list of "Tokens" (Tags and Text)
        
        tokens = []  # Using a list as a Dynamic Array to store tokens
        i = 0
        length = len(xml_string)
        
        # Iterate through the entire XML string character by character
        while i < length:
            
            # Found an XML Tag (starts with '<') ---
            if xml_string[i] == '<':
                # Find the closing angle bracket '>' for this tag
                j = xml_string.find('>', i)
                
                # Safety check: if no closing bracket is found, stop parsing
                if j == -1: break 
                
                # Extract the tag string (e.g., "<user>" or "</id>")
                tag = xml_string[i:j+1]
                tokens.append(tag)
                
                # Move the main pointer 'i' past this tag
                i = j + 1
                
            # Found Text Content (between tags) ---
            else:
                # Look ahead until we find the start of the next tag
                j = i
                while j < length and xml_string[j] != '<':
                    j += 1
                
                # Extract the text between the tags
                raw_text = xml_string[i:j]
                
                # Check if the text is just empty whitespace (formatting)
                # If it is empty, we skip it to clean up the XML
                if not raw_text.strip():
                    i = j
                    continue
                
                # If text exists, strip surrounding whitespace and add to tokens
                tokens.append(raw_text.strip())
                
                # Move pointer 'i' to the start of the next tag
                i = j

        # FORMATTING (PRETTIFYING)
        # Rebuild the string with correct indentation
        
        formatted = []
        level = 0               # Tracks the depth of indentation
        indentation = "    "    # indentation
        k = 0
        
        # Iterate through the list of tokens we created
        while k < len(tokens):
            token = tokens[k]
            
            # Closing Tag (e.g., </user>) ---
            if token.startswith('</'):
                # Decrease indentation level (move left)
                # max(0, ...) prevents level from going negative if XML is bad
                level = max(0, level - 1)
                formatted.append((indentation * level) + token)
                
            # Opening Tag (e.g., <user>) ---
            elif token.startswith('<') and not token.startswith('</'):
                
                # SPECIAL LOGIC: "Leaf Node" Detection
                # We want simple data like <id>1</id> to stay on ONE line.
                # Conditions:
                # 1. Check if we have at least 2 more tokens ahead (k+2)
                # 2. Next token is NOT a tag (it is text)
                # 3. Token after that IS a closing tag
                # 4. Text is short (< 70 chars)
                # 5. Text does not contain newlines
                if (k + 2 < len(tokens) and 
                    not tokens[k+1].startswith('<') and 
                    tokens[k+2].startswith('</') and 
                    len(tokens[k+1]) < 70 and 
                    '\n' not in tokens[k+1]): 
                    
                    # Combine Open + Text + Close into one single line
                    line = (indentation * level) + tokens[k] + tokens[k+1] + tokens[k+2]
                    formatted.append(line)
                    
                    # Skip the next 2 tokens since we just used them
                    k += 2 
                    
                else:
                    # It is a parent tag or long content:
                    # Print tag on its own line and increase indentation level (move right)
                    formatted.append((indentation * level) + token)
                    level += 1
            
            # Text Content (Multi-line handling) 
            # This handles long paragraphs (like the <body> tag)
            else:
                # Split the text by newlines so we can indent each line individually
                lines = token.split('\n')
                aligned_lines = []
                
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line:
                        # Add current indentation level to this line of text
                        aligned_lines.append((indentation * level) + stripped_line)
                
                # Join the indented lines back together
                formatted.append("\n".join(aligned_lines))
            
            # Move to the next token
            k += 1
            
        # Join all formatted lines with newlines to create the final string
        return "\n".join(formatted)

# --- Test ---
input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<users>
<user>
<id>1</id>
<name>Ahmed Ali</name>
<posts>
<post>
<body>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
</body>
<topics>
<topic>
economy
</topic>
<topic>
finance
</topic>
</topics>
</post>
<post>
<body>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
</body>
<topics>
<topic>
solar_energy
</topic>
</topics>
</post>
</posts>
<followers>
<follower>
<id>2</id>
</follower>
<follower>
<id>3</id>
</follower>
</followers>
<followings>
<following>
<id>2</id>
</following>
<following>
<id>3</id>
</following>
</followings>
</user>
<user>
<id>2</id>
<name>Yasser Ahmed</name>
<posts>
<post>
<body>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
</body>
<topics>
<topic>
education
</topic>
</topics>
</post>
</posts>
<followers>
<follower>
<id>1</id>
</follower>
</followers>
<followings>
<following>
<id>1</id>
</following>
</followings>
</user>
<user>
<id>3</id>
<name>Mohamed Sherif</name>
<posts>
<post>
<body>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
</body>
<topics>
<topic>
sports
</topic>
</topics>
</post>
</posts>
<followers>
<follower>
<id>1</id>
</follower>
</followers>
<followings>
<following>
<id>1</id>
</following>
</followings>
</user>
</users>"""
formatter = XMLcontroller()
print(formatter.format(input_xml))