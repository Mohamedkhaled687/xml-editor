"""
Data Parser - Handles parsing and validation of XML data into structured Python objects.
Provides a robust interface for extracting user data, relationships, and graph structure.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .xml_tree import XMLTree, XMLNode, XMLParseError


@dataclass
class User:
    """Represents a user in the social network."""
    id: str
    name: str
    followers: List[str]
    following: List[str]
    posts: int = 0


class DataParser:
    """Parser for social network XML data."""
    
    def __init__(self, xml_data):
        """
        Initialize parser with XML data.
        
        Args:
            xml_data: Root XMLNode element or XML string
        """
        # Handle both XMLNode and string input
        if isinstance(xml_data, str):
            try:
                self.xml_data = XMLTree.fromstring(xml_data)
            except XMLParseError as e:
                raise ValueError(f"Invalid XML string: {str(e)}")
        else:
            self.xml_data = xml_data
            
        self._users_cache: Optional[Dict[str, User]] = None
        self._nodes_cache: Optional[Dict[str, str]] = None
        self._edges_cache: Optional[List[Tuple[str, str]]] = None
    
    def parse_users(self) -> Dict[str, User]:
        """
        Parse all users from XML into User objects.
        
        Returns:
            dict: {user_id: User object}
        """
        if self._users_cache is not None:
            return self._users_cache
        
        users_dict = {}
        users = self.xml_data.findall('.//user')
        
        for user_elem in users:
            # Extract user ID
            user_id = self._extract_user_id(user_elem)
            if not user_id:
                continue
            
            # Extract user name
            name_elem = user_elem.find('name')
            user_name = name_elem.text.strip() if name_elem is not None and name_elem.text else f"User {user_id}"
            
            # Extract followers
            followers = self._extract_followers(user_elem)
            
            # Extract following
            following = self._extract_following(user_elem)
            
            # Count posts
            posts = len(user_elem.findall('.//post'))
            
            # Create User object
            user = User(
                id=str(user_id),
                name=user_name,
                followers=followers,
                following=following,
                posts=posts
            )
            users_dict[str(user_id)] = user
        
        self._users_cache = users_dict
        return users_dict
    
    def parse_nodes(self) -> Dict[str, str]:
        """
        Parse users as nodes for graph visualization.
        
        Returns:
            dict: {user_id: user_name}
        """
        if self._nodes_cache is not None:
            return self._nodes_cache
        
        users = self.parse_users()
        nodes = {user.id: user.name for user in users.values()}
        self._nodes_cache = nodes
        return nodes
    
    def parse_edges(self) -> List[Tuple[str, str]]:
        """
        Parse user relationships as edges for graph.
        Supports both follower-based and connection-based structures.
        
        Returns:
            list: [(user_id, follower_id)] representing follows relationships
        """
        if self._edges_cache is not None:
            return self._edges_cache
        
        edges = []
        users = self.xml_data.findall('.//user')
        
        for user_elem in users:
            user_id = self._extract_user_id(user_elem)
            if not user_id:
                continue
            
            # Method 1: Parse <followers><follower><id>X</id></follower></followers>
            followers_elem = user_elem.find('followers')
            if followers_elem is not None:
                for follower_elem in followers_elem.findall('follower'):
                    follower_id_elem = follower_elem.find('id')
                    if follower_id_elem is not None and follower_id_elem.text:
                        follower_id = follower_id_elem.text.strip()
                        edges.append((str(user_id), str(follower_id)))
            
            # Method 2: Parse <connections><friend user_id="X"/></connections>
            connections_elem = user_elem.find('connections')
            if connections_elem is not None:
                for friend_elem in connections_elem.findall('friend'):
                    friend_id = friend_elem.get('user_id')
                    if friend_id:
                        edges.append((str(user_id), str(friend_id)))
        
        self._edges_cache = edges
        return edges
    
    def _extract_user_id(self, user_elem: XMLNode) -> Optional[str]:
        """Extract user ID from element (supports both attribute and child element)."""
        # Try attribute first
        user_id = user_elem.get('id')
        if user_id:
            return user_id.strip()
        
        # Try child element
        id_elem = user_elem.find('id')
        if id_elem is not None and id_elem.text:
            return id_elem.text.strip()
        
        return None
    
    def _extract_followers(self, user_elem: XMLNode) -> List[str]:
        """Extract follower IDs from user element."""
        followers = []
        
        followers_elem = user_elem.find('followers')
        if followers_elem is not None:
            for follower_elem in followers_elem.findall('follower'):
                follower_id_elem = follower_elem.find('id')
                if follower_id_elem is not None and follower_id_elem.text:
                    followers.append(follower_id_elem.text.strip())
        
        return followers
    
    def _extract_following(self, user_elem: XMLNode) -> List[str]:
        """Extract following IDs from user element."""
        following = []
        
        # Method 1: <followings><following><id>X</id></following></followings>
        followings_elem = user_elem.find('followings')
        if followings_elem is not None:
            for following_elem in followings_elem.findall('following'):
                following_id_elem = following_elem.find('id')
                if following_id_elem is not None and following_id_elem.text:
                    following.append(following_id_elem.text.strip())
        
        # Method 2: <connections><friend user_id="X"/></connections>
        connections_elem = user_elem.find('connections')
        if connections_elem is not None:
            for friend_elem in connections_elem.findall('friend'):
                friend_id = friend_elem.get('user_id')
                if friend_id:
                    following.append(friend_id.strip())
        
        return following
    
    def get_graph_data(self) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
        """
        Get complete graph data (nodes and edges).
        
        Returns:
            tuple: (nodes_dict, edges_list)
        """
        nodes = self.parse_nodes()
        edges = self.parse_edges()
        return nodes, edges
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get statistics for a specific user.
        
        Args:
            user_id: User ID to get stats for
            
        Returns:
            dict with user stats or None if user not found
        """
        users = self.parse_users()
        if user_id not in users:
            return None
        
        user = users[user_id]
        return {
            'id': user.id,
            'name': user.name,
            'followers_count': len(user.followers),
            'following_count': len(user.following),
            'posts': user.posts
        }
    
    def get_all_users_summary(self) -> List[Dict]:
        """
        Get summary of all users.
        
        Returns:
            list of user summary dictionaries
        """
        users = self.parse_users()
        return [
            {
                'id': user.id,
                'name': user.name,
                'followers': len(user.followers),
                'following': len(user.following),
                'posts': user.posts
            }
            for user in users.values()
        ]
    
    def validate_data(self) -> Tuple[bool, List[str]]:
        """
        Validate parsed data for inconsistencies.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        users = self.parse_users()
        all_user_ids = set(users.keys())
        
        for user_id, user in users.items():
            # Check if followers exist
            for follower_id in user.followers:
                if follower_id not in all_user_ids:
                    errors.append(f"User {user_id} has non-existent follower: {follower_id}")
            
            # Check if following exist
            for following_id in user.following:
                if following_id not in all_user_ids:
                    errors.append(f"User {user_id} is following non-existent user: {following_id}")
        
        return len(errors) == 0, errors
    
    def clear_cache(self):
        """Clear internal caches to force re-parsing."""
        self._users_cache = None
        self._nodes_cache = None
        self._edges_cache = None
