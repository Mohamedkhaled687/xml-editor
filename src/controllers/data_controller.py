"""
Data Controller - Handles data operations like parsing, statistics, error checking, and JSON export.
"""

import json
import xml.etree.ElementTree as ET
from utilities import file_io
from utilities import token_utils
import re

class DataController:
    """Controller for data-related operations."""

    def __init__(self, xml_data=None):
        self.xml_data = xml_data

    def set_xml_data(self, xml_data):
        """Set the XML data root element."""
        self.xml_data = xml_data

    def export_to_json(self, file_path, current_file_path):
        """
        Export XML data to JSON format.
        
        Args:
            file_path: Path to save the JSON file
            current_file_path: Path of the source XML file
            
        Returns:
            tuple: (success: bool, message: str, error: str)
        """
        if self.xml_data is None:
            return False, "", "No data loaded. Please upload and parse an XML file first."

        try:
            users = self.xml_data.findall('.//user')

            # Convert XML to JSON structure - only id, name, posts, and followers list
            json_data = {
                "users": []
            }

            for user in users:
                # Get user ID
                user_id = user.get('id')
                if user_id is None:
                    id_elem = user.find('id')
                    if id_elem is not None:
                        user_id = id_elem.text

                if user_id is None:
                    continue

                # Get username
                name_elem = user.find('name')
                user_name = name_elem.text.strip() if name_elem is not None and name_elem.text else None

                # Build user dict with only required fields
                user_dict = {
                    "id": user_id,
                    "name": user_name,
                    "posts": [],
                    "followers": [],
                    "followings": []

                }

                # Add posts
                for post in user.findall('.//post'):
                    content_elem = post.find('body')
                    content = content_elem.text.strip() if content_elem is not None and content_elem.text else ""

                    topics = []
                    for topic_elem in post.findall('.//topics/topic'):
                        if topic_elem is not None and topic_elem.text:
                            topics.append(topic_elem.text.strip())

                    post_dict = {
                        "id": post.get('id'),
                        "content": content,
                        "topics": topics
                    }
                    user_dict["posts"].append(post_dict)

                # Add followers list - handle both XML structures
                followers_elem = user.find('followers')
                if followers_elem is not None:
                    for follower in followers_elem.findall('follower'):
                        follower_id_elem = follower.find('id')
                        if follower_id_elem is not None and follower_id_elem.text:
                            follower_id = follower_id_elem.text.strip()
                            user_dict["followers"].append(follower_id)

                followings_elem = user.find('followings')
                if followings_elem is not None:
                    for following in followings_elem.findall('following'):
                        following_id_elem = following.find('id')
                        if following_id_elem is not None and following_id_elem.text:
                            following_id = following_id_elem.text.strip()
                            user_dict["followings"].append(following_id)

                json_data["users"].append(user_dict)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            return True, f"Successfully exported {len(users)} users to JSON. File saved: {file_path}", None
        except Exception as e:
            return False, "", f"Failed to export to JSON: {str(e)}"
