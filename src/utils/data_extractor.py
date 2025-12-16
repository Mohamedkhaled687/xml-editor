"""
Data Extractor - Handles extracting structured data from XML elements.
Provides utilities for parsing users, followers, and graph relationships.
"""

from typing import Dict, List, Tuple, Optional
from .xml_tree import XMLNode


class DataExtractor:
    """Utility class for extracting data from XML elements."""
    
    @staticmethod
    def extract_users(xml_data: XMLNode) -> Dict[str, str]:
        """
        Extract user nodes from XML data.
        
        Args:
            xml_data: XML root element (XMLNode)
            
        Returns:
            dict: {user_id: user_name}
        """
        nodes = {}
        users = xml_data.findall('.//user')
        
        for user in users:
            # Get user ID - try different possible structures
            user_id = user.get('id')
            if user_id is None:
                id_elem = user.find('id')
                if id_elem is not None:
                    user_id = id_elem.text
            
            if user_id is None:
                continue
            
            # Get user name
            name_elem = user.find('name')
            user_name = name_elem.text if name_elem is not None else f"User {user_id}"
            nodes[user_id] = user_name
        
        return nodes
    
    @staticmethod
    def extract_edges(xml_data: XMLNode) -> List[Tuple[str, str]]:
        """
        Extract relationship edges from XML data.
        Handles both follower and connection-based structures.
        
        Args:
            xml_data: XML root element (XMLNode)
            
        Returns:
            list: [(from_id, to_id)] where from_id follows to_id
        """
        edges = []
        users = xml_data.findall('.//user')
        
        for user in users:
            # Get user ID
            user_id = user.get('id')
            if user_id is None:
                id_elem = user.find('id')
                if id_elem is not None:
                    user_id = id_elem.text
            
            if user_id is None:
                continue
            
            # Structure 1: <followers><follower><id>V</id></follower></followers>
            followers_elem = user.find('followers')
            if followers_elem is not None:
                for follower in followers_elem.findall('follower'):
                    follower_id_elem = follower.find('id')
                    if follower_id_elem is not None and follower_id_elem.text:
                        follower_id = follower_id_elem.text.strip()
                        edges.append((user_id, follower_id))  # U → V (U follows V)
            
            # Structure 2: <connections><friend user_id="V"/></connections>
            connections_elem = user.find('connections')
            if connections_elem is not None:
                for friend in connections_elem.findall('friend'):
                    friend_id = friend.get('user_id')
                    if friend_id:
                        edges.append((user_id, friend_id))  # U → V (U follows V)
        
        return edges
    
    @staticmethod
    def extract_user_posts(user_elem: XMLNode) -> List[Dict]:
        """
        Extract posts from a user element.
        
        Args:
            user_elem: User XML element (XMLNode)
            
        Returns:
            list: List of post dictionaries with content and topics
        """
        posts = []
        
        for post_elem in user_elem.findall('.//post'):
            post_dict = {}
            
            # Post ID
            post_dict['id'] = post_elem.get('id')
            
            # Post content/body
            content_elem = post_elem.find('body')
            post_dict['content'] = content_elem.text.strip() if content_elem is not None and content_elem.text else ""
            
            # Post topics
            topics = []
            for topic_elem in post_elem.findall('.//topics/topic'):
                if topic_elem is not None and topic_elem.text:
                    topics.append(topic_elem.text.strip())
            post_dict['topics'] = topics
            
            posts.append(post_dict)
        
        return posts
    
    @staticmethod
    def extract_user_followers(user_elem: XMLNode) -> List[str]:
        """
        Extract follower IDs from a user element.
        
        Args:
            user_elem: User XML element (XMLNode)
            
        Returns:
            list: List of follower user IDs
        """
        followers = []
        
        # Handle <followers><follower><id>X</id></follower></followers>
        followers_elem = user_elem.find('followers')
        if followers_elem is not None:
            for follower in followers_elem.findall('follower'):
                follower_id_elem = follower.find('id')
                if follower_id_elem is not None and follower_id_elem.text:
                    followers.append(follower_id_elem.text.strip())
        
        return followers
    
    @staticmethod
    def extract_user_following(user_elem: XMLNode) -> List[str]:
        """
        Extract following IDs from a user element.
        
        Args:
            user_elem: User XML element (XMLNode)
            
        Returns:
            list: List of user IDs this user is following
        """
        following = []
        
        # Handle <followings><following><id>X</id></following></followings>
        followings_elem = user_elem.find('followings')
        if followings_elem is not None:
            for f in followings_elem.findall('following'):
                following_id_elem = f.find('id')
                if following_id_elem is not None and following_id_elem.text:
                    following.append(following_id_elem.text.strip())
        
        return following
    
    @staticmethod
    def extract_graph_data(xml_data: XMLNode) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
        """
        Extract complete graph data (nodes and edges) from XML.
        
        Args:
            xml_data: XML root element (XMLNode)
            
        Returns:
            tuple: (nodes_dict, edges_list)
        """
        nodes = DataExtractor.extract_users(xml_data)
        edges = DataExtractor.extract_edges(xml_data)
        return nodes, edges
    
    @staticmethod
    def extract_user_degree_info(user_elem: XMLNode, user_id: str) -> Dict:
        """
        Extract degree information (followers and following count) for a user.
        
        Args:
            user_elem: User XML element (XMLNode)
            user_id: User ID
            
        Returns:
            dict: {user_id, followers_count, following_count}
        """
        followers = DataExtractor.extract_user_followers(user_elem)
        following = DataExtractor.extract_user_following(user_elem)
        
        return {
            'user_id': user_id,
            'followers_count': len(followers),
            'following_count': len(following),
            'followers': followers,
            'following': following
        }
