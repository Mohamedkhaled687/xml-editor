import tempfile
import unittest
import sys
import os
import json

# Add parent directory to system path to allow imports from src folder
# This is necessary when tests are in a separate directory from source code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the XMLController class from the controllers module
# NOTE: Class name is capitalized following Python naming conventions
from src.controllers.xml_controller import XMLController 

class TestXMLController(unittest.TestCase):
    """
    Test suite for XMLController class.
    Tests various XML formatting scenarios including indentation, wrapping, and minification.
    """

    def setUp(self):
        """
        Initialize the controller before each test.
        This method runs automatically before every test method.
        Creates a fresh XMLController instance for isolated testing.
        """
        # Create a new XMLController instance with no initial XML
        self.controller = XMLController()

    def test_basic_formatting_and_indentation(self):
        """
        Test if simple XML is indented correctly (4 spaces per level).
        
        Expected behavior:
        - Opening tag <user> at level 0 (no indent)
        - Child tag <name> at level 1 (4 spaces indent)
        - Closing tag </user> at level 0 (no indent)
        """
        # Simple XML with one parent and one child element
        raw_xml = "<user><name>Ali</name></user>"
        
        # Set the XML string as a class attribute
        # This allows the format() method to access it via self.xml_string
        self.controller.xml_string = raw_xml
        
        # Call format() without arguments (uses self.xml_string internally)
        formatted = self.controller.format()
        
        # Define the expected output with proper indentation
        # \n represents newline characters
        expected_output = (
            "<user>\n"
            "    <name>Ali</name>\n"  # 4 spaces before <name>
            "</user>"
        )
        
        # Assert that formatted output matches expected output exactly
        self.assertEqual(formatted, expected_output)

    def test_leaf_node_inline(self):
        """
        Test that short text (< 80 chars) stays on the same line as tags.
        
        Expected behavior:
        - Text under 80 characters should remain inline: <desc>Text</desc>
        - No line breaks should be inserted
        - Format: <tag>content</tag> all on one line
        """
        # Create short text content (well under 80 character limit)
        short_text = "This is short text"
        raw_xml = f"<desc>{short_text}</desc>"
        
        # Set XML and format it
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        # Verify the entire tag+text+closing tag is on one line
        self.assertIn(f"<desc>{short_text}</desc>", formatted)
        
        # Verify there are no newline characters (count should be 0)
        self.assertEqual(formatted.count('\n'), 0)

    def test_long_text_wrapping(self):
        """
        Test that long text (> 80 chars) wraps to new lines.
        
        Expected behavior:
        - Opening tag on its own line
        - Text content wrapped and indented (one level deeper)
        - Closing tag on its own line
        - Total lines should be at least 3 (open, text, close)
        """
        # Create a long string that exceeds 80 character limit
        # Using 85 'A' characters to ensure wrapping triggers
        long_text = "A" * 85 
        raw_xml = f"<body>{long_text}</body>"
        
        # Set XML and format it
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        # Split the formatted output into individual lines
        lines = formatted.split('\n')
        
        # Verify we have at least 3 lines (open tag, wrapped text, close tag)
        self.assertTrue(len(lines) >= 3, "Long text should result in at least 3 lines")
        
        # Verify structure:
        # Line 0: Opening tag without indentation
        self.assertEqual(lines[0], "<body>")
        
        # Line 1: Text content with 4-space indentation
        self.assertTrue(lines[1].startswith("    "), "Wrapped text should be indented")
        
        # Last line: Closing tag without indentation
        self.assertEqual(lines[-1], "</body>")

    def test_minify(self):
        """
        Test if minification removes all whitespace between tags.
        
        Expected behavior:
        - All newlines removed
        - All indentation removed
        - Tags and content concatenated directly
        - Result is a single continuous string
        """
        # XML with formatting (newlines and indentation)
        formatted_xml = """
        <user>
            <id>1</id>
        </user>
        """
        
        # Set the formatted XML
        self.controller.xml_string = formatted_xml
        
        # Call minify() to remove all whitespace
        minified = self.controller.minify()
        
        # Expected output: all on one line, no spaces/newlines
        expected = "<user><id>1</id></user>"
        
        # Verify minified output matches expected
        self.assertEqual(minified, expected)

    def test_attributes_preservation(self):
        """
        Test that attributes inside tags are preserved correctly.
        
        Expected behavior:
        - Attributes like id="101" should remain unchanged
        - Multiple attributes should all be preserved
        - Attribute order should be maintained
        """
        # XML with attributes in the opening tag
        raw_xml = '<user id="101" type="admin"></user>'
        
        # Set XML and format it
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        # Verify the complete tag with attributes appears in output
        self.assertIn('<user id="101" type="admin">', formatted)

    def test_mixed_content_robustness(self):
        """
        Test how it handles nested structures with multiple children.
        
        Expected behavior:
        - Each child element should be properly indented
        - Sibling elements at same level should have same indentation
        - Parent-child relationships should be clear from indentation
        """
        # XML with multiple child elements at the same level
        raw_xml = "<root><child>Text</child><child>Text2</child></root>"
        
        # Set XML and format it
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        # Verify that child elements are indented with 4 spaces
        expected_fragment = "    <child>Text</child>"
        self.assertIn(expected_fragment, formatted)

    def test_export_to_json(self):
        """
        Test the export_to_json method for correct data transformation
        and file creation using a temporary file.
        """
        # 1. Setup Mock XML Data
        mock_xml = """
            <users>
                <user>
                    <id>1</id>
                    <name>Alice</name>
                    <posts>
                        <post>
                            <body>First post content</body>
                            <topics>
                                <topic>tech</topic>
                                <topic>ai</topic>
                            </topics>
                        </post>
                    </posts>
                    <followers>
                        <follower><id>2</id></follower>
                    </followers>
                    <followings>
                        <following><id>3</id></following>
                    </followings>
                </user>
                <user>
                    <id>2</id>
                    <name>Bob</name>
                    <posts/>
                    <followers/>
                    <followings/>
                </user>
            </users>
            """ 		
        # 2. Set XML string
        self.controller.set_xml_string(mock_xml)
        
        # 3. Use a temporary file path
        # This creates a file path in the system's temp directory
        with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix='.json') as tmp:
            test_file_path = tmp.name
        
        # 4. Execute the method
        # We ensure the custom-coded '_get_tag_info' is defined and called.
        success, message, error = self.controller.export_to_json(test_file_path)

        # 5. Assertions (Verify the result)
        self.assertTrue(success, f"JSON export failed. Message: {message}, Error: {error}")
        self.assertIn("exported 2 users", message)

        # 6. Read the content of the exported file
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
        except Exception as e:
            self.fail(f"Failed to read or parse exported JSON file: {e}")
            
        # 7. Verify JSON Structure and Content
        
        # A. Check total user count
        self.assertEqual(len(json_content.get('users', [])), 2)
        
        # B. Check User 1 data
        user1 = json_content['users'][0]
        self.assertEqual(user1['id'], '1')
        self.assertEqual(user1['name'], 'Alice')
        self.assertEqual(len(user1['posts']), 1)
        self.assertEqual(user1['followers'], [{'id': '2'}]) 
        self.assertEqual(user1['followings'], [{'id': '3'}])

        # C. Check User 1 Post 1 data
        post1 = user1['posts'][0]
        self.assertEqual(post1['content'], 'First post content')
        self.assertEqual(post1['topics'], ['tech', 'ai'])
        
        # *** FIX CONFIRMATION: Assert 'id' is NOT in the post object ***
        self.assertNotIn('id', post1, "Post object should NOT contain an 'id' key.") 
        # -------------------------------------------------------------
        
        # D. Check User 2 data (Should handle empty posts/relations gracefully)
        user2 = json_content['users'][1]
        self.assertEqual(user2['id'], '2')
        self.assertEqual(user2['name'], 'Bob')
        self.assertEqual(user2['posts'], [])
        self.assertEqual(user2['followers'], [])
        self.assertEqual(user2['followings'], [])
        # --------------------------------------
        # 8. Cleanup the temporary file
        os.remove(test_file_path)
        
xml_test = """
<?xml version="1.0" encoding="UTF-8"?>
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
                        sports
                    </topic>
                    <topic>
                        history
                    </topic>
                </topics>
            </post>
            <post>
                <body>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                </body>
                <topics>
                    <topic>
                        food
                    </topic>
                    <topic>
                        health
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
                        sports
                    </topic>
                    <topic>
                        health
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
    <user>
        <id>4</id>
        <name>Fady Faragallah</name>
        <posts>
            <post>
                <body>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                </body>
                <topics>
                    <topic>
                        Data
                    </topic>
                    <topic>
                        Software Engineering
                    </topic>
                </topics>
            </post>
        </posts>
        <followers>
            <follower>
                <id>1</id>
            </follower>
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
    </user>
        </followings>
"""

# Create controller instance
controller_test = XMLController(xml_test)

print("=" * 80)
print("VALIDATION REPORT (BEFORE CORRECTION)")
print("=" * 80)
annotated_xml, error_counts = controller_test.validate()
print(annotated_xml)
print(f"\nError counts: {error_counts}")

print("\n" + "=" * 80)
print("AUTO-CORRECTING XML...")
print("=" * 80)

# Auto-correct the XML (this returns a tuple: corrected XML string and correction counts)
corrected_xml, correction_counts = controller_test.autocorrect()

print("\n✓ Auto-correction completed!")
print(f"Correction counts: {correction_counts}")

# Write corrected XML to file
formatted_filename = "corrected_formatted.xml"
with open(formatted_filename, 'w', encoding='utf-8') as f:
    f.write(corrected_xml)

print(f"✓ Corrected XML written to '{formatted_filename}'")

print("\n" + "=" * 80)
print("VALIDATION REPORT (AFTER CORRECTION)")
print("=" * 80)
annotated_xml_after, error_counts_after = controller_test.validate()
print(annotated_xml_after)
print(f"\nError counts: {error_counts_after}")

# Also write the minified version
minified_xml = controller_test.minify()
minified_filename = "corrected_minified.xml"
with open(minified_filename, 'w', encoding='utf-8') as f:
    f.write(minified_xml)

print(f"\n✓ Minified XML written to '{minified_filename}'")

# Export to JSON
json_filename = "xml_to_json.json"
success, message, error = controller_test.export_to_json(json_filename)

print("\n" + "=" * 80)
if success:
    print(f"JSON EXPORT SUCCESS: {message}")
else:
    print(f"JSON EXPORT FAILED: {error}")
print("=" * 80)
# Standard Python idiom to run tests when script is executed directly
if __name__ == '__main__': #Corrected from '_main_'
    # Run all test methods in this test case
   unittest.main()