import unittest
import sys
import os

# Ensure we can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# IMPORT FIX: Use the new Capitalized class name
from src.controllers.xml_controller import XMLController 

class TestXMLController(unittest.TestCase):

    def setUp(self):
        """Initialize the controller before each test."""
        # NAME FIX: Use XMLController instead of XMLcontroller
        self.controller = XMLController()

    def test_basic_formatting_and_indentation(self):
        """Test if simple XML is indented correctly (4 spaces)."""
        raw_xml = "<user><name>Ali</name></user>"
        
        # LOGIC FIX: Set the attribute, then call format() without arguments
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        expected_output = (
            "<user>\n"
            "    <name>Ali</name>\n"
            "</user>"
        )
        self.assertEqual(formatted, expected_output)

    def test_leaf_node_inline(self):
        """Test that short text (< 80 chars) stays on the same line as tags."""
        short_text = "This is short text"
        raw_xml = f"<desc>{short_text}</desc>"
        
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        self.assertIn(f"<desc>{short_text}</desc>", formatted)
        self.assertEqual(formatted.count('\n'), 0)

    def test_long_text_wrapping(self):
        """Test that long text (> 80 chars) wraps to new lines."""
        long_text = "A" * 85 
        raw_xml = f"<body>{long_text}</body>"
        
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        lines = formatted.split('\n')
        self.assertTrue(len(lines) >= 3, "Long text should result in at least 3 lines")
        self.assertEqual(lines[0], "<body>")
        self.assertTrue(lines[1].startswith("    "), "Wrapped text should be indented")
        self.assertEqual(lines[-1], "</body>")

    def test_minify(self):
        """Test if minification removes all whitespace between tags."""
        formatted_xml = """
        <user>
            <id>1</id>
        </user>
        """
        self.controller.xml_string = formatted_xml
        minified = self.controller.minify()
        
        expected = "<user><id>1</id></user>"
        self.assertEqual(minified, expected)

    def test_attributes_preservation(self):
        """Test that attributes inside tags are preserved correctly."""
        raw_xml = '<user id="101" type="admin"></user>'
        
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        self.assertIn('<user id="101" type="admin">', formatted)

    def test_mixed_content_robustness(self):
        """Test how it handles nested structures."""
        raw_xml = "<root><child>Text</child><child>Text2</child></root>"
        
        self.controller.xml_string = raw_xml
        formatted = self.controller.format()
        
        expected_fragment = "    <child>Text</child>"
        self.assertIn(expected_fragment, formatted)

if __name__ == '__main__':
    unittest.main()