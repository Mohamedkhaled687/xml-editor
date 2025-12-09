"""
XML Validator - Stack-based validation with error detection
Detects structural and semantic errors in social network XML files
"""
import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

@dataclass
class XMLError:
    """Represents an XML validation error"""
    line: int
    description: str
    error_type: str  # 'syntax', 'semantic', 'structure'
    
    def __str__(self):
        return f"Line {self.line}: {self.description}"

class XMLValidator:
    """Stack-based XML validator for social network data"""
    
    def __init__(self):
        self.errors: List[XMLError] = []
        self.tag_stack: List[Tuple[str, int]] = []  # (tag_name, line_number)
        self.user_ids: Set[str] = set()
        self.all_user_ids: Set[str] = set()
        self.current_line: int = 0
        
    def validate_file(self, file_path: str) -> Dict:
        """
        Validate XML file and return results
        
        Returns:
        {
            'is_valid': bool,
            'error_count': int,
            'errors': [{'line': int, 'description': str, 'type': str}, ...]
        }
        """
        self.errors = []
        self.tag_stack = []
        self.user_ids = set()
        self.all_user_ids = set()
        self.current_line = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # First pass - collect all user IDs
            self._collect_user_ids(content)
            
            # Second pass - validate structure and semantics
            self._validate_content(content)
            
            # Check for unclosed tags
            if self.tag_stack:
                for tag, line in self.tag_stack:
                    self.errors.append(XMLError(
                        line=line,
                        description=f"Unclosed tag '<{tag}>'",
                        error_type='structure'
                    ))
            
            return {
                'is_valid': len(self.errors) == 0,
                'error_count': len(self.errors),
                'errors': [
                    {
                        'line': e.line,
                        'description': e.description,
                        'type': e.error_type
                    }
                    for e in sorted(self.errors, key=lambda x: x.line)
                ]
            }
            
        except FileNotFoundError:
            return {
                'is_valid': False,
                'error_count': 1,
                'errors': [{
                    'line': 0,
                    'description': f"File not found: {file_path}",
                    'type': 'file'
                }]
            }
        except Exception as e:
            return {
                'is_valid': False,
                'error_count': 1,
                'errors': [{
                    'line': 0,
                    'description': f"Error reading file: {str(e)}",
                    'type': 'file'
                }]
            }
    
    def _collect_user_ids(self, content: str) -> None:
        """First pass: collect all user IDs for reference checking"""
        lines = content.split('\n')
        in_user = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if '<user>' in line:
                in_user = True
            elif '</user>' in line:
                in_user = False
            elif in_user and '<id>' in line:
                # Extract ID
                match = re.search(r'<id>(.+?)</id>', line)
                if match:
                    self.all_user_ids.add(match.group(1).strip())
    
    def _validate_content(self, content: str) -> None:
        """Main validation logic using stack-based parsing"""
        lines = content.split('\n')
        
        current_user_id = None
        follower_ids = []
        
        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            original_line = line
            line = line.strip()
            
            if not line:
                continue
            
            # Check for basic XML syntax errors
            if '<' in line and '>' not in line:
                self.errors.append(XMLError(
                    line=line_num,
                    description="Malformed tag: missing closing '>'",
                    error_type='syntax'
                ))
                continue
            
            if '>' in line and '<' not in line:
                self.errors.append(XMLError(
                    line=line_num,
                    description="Malformed tag: missing opening '<'",
                    error_type='syntax'
                ))
                continue
            
            # Process opening tags
            opening_tags = re.findall(r'<([a-zA-Z_][a-zA-Z0-9_]*)[^/>]*>', line)
            for tag in opening_tags:
                # Skip if it's a self-closing or has closing tag on same line
                if not re.search(rf'<{tag}[^/>]*/>|<{tag}[^>]*>.*?</{tag}>', line):
                    self.tag_stack.append((tag, line_num))
            
            # Process closing tags
            closing_tags = re.findall(r'</([a-zA-Z_][a-zA-Z0-9_]*)>', line)
            for tag in closing_tags:
                if not self.tag_stack:
                    self.errors.append(XMLError(
                        line=line_num,
                        description=f"Closing tag '</{tag}>' without matching opening tag",
                        error_type='structure'
                    ))
                elif self.tag_stack[-1][0] != tag:
                    expected = self.tag_stack[-1][0]
                    self.errors.append(XMLError(
                        line=line_num,
                        description=f"Mismatched tags: expected '</{expected}>' but found '</{tag}>'",
                        error_type='structure'
                    ))
                    self.tag_stack.pop()
                else:
                    self.tag_stack.pop()
            
            # Semantic validation - check user IDs
            if '<id>' in line and len(self.tag_stack) >= 2:
                parent = self.tag_stack[-1][0] if self.tag_stack else None
                
                match = re.search(r'<id>(.+?)</id>', line)
                if match:
                    user_id = match.group(1).strip()
                    
                    if not user_id:
                        self.errors.append(XMLError(
                            line=line_num,
                            description="Empty user ID",
                            error_type='semantic'
                        ))
                    elif parent == 'user':
                        # This is a user's main ID
                        if user_id in self.user_ids:
                            self.errors.append(XMLError(
                                line=line_num,
                                description=f"Duplicate user ID '{user_id}'",
                                error_type='semantic'
                            ))
                        else:
                            self.user_ids.add(user_id)
                            current_user_id = user_id
                    elif parent == 'follower':
                        # This is a follower reference
                        follower_ids.append((user_id, line_num))
            
            # Check for empty required fields
            if '<name></name>' in line or '<name> </name>' in line:
                self.errors.append(XMLError(
                    line=line_num,
                    description="Empty user name",
                    error_type='semantic'
                ))
            
            if '<body></body>' in line or '<body> </body>' in line:
                self.errors.append(XMLError(
                    line=line_num,
                    description="Empty post body",
                    error_type='semantic'
                ))
        
        # Check follower references
        for follower_id, line_num in follower_ids:
            if follower_id not in self.all_user_ids:
                self.errors.append(XMLError(
                    line=line_num,
                    description=f"Invalid follower reference: user ID '{follower_id}' does not exist",
                    error_type='semantic'
                ))
    
    def validate_string(self, xml_string: str) -> Dict:
        """Validate XML from string instead of file"""
        self.errors = []
        self.tag_stack = []
        self.user_ids = set()
        self.all_user_ids = set()
        
        # First pass - collect all user IDs
        self._collect_user_ids(xml_string)
        
        # Second pass - validate
        self._validate_content(xml_string)
        
        # Check for unclosed tags
        if self.tag_stack:
            for tag, line in self.tag_stack:
                self.errors.append(XMLError(
                    line=line,
                    description=f"Unclosed tag '<{tag}>'",
                    error_type='structure'
                ))
        
        return {
            'is_valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'errors': [
                {
                    'line': e.line,
                    'description': e.description,
                    'type': e.error_type
                }
                for e in sorted(self.errors, key=lambda x: x.line)
            ]
        }