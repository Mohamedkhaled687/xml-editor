"""
Network Analyzer - Advanced network analysis and recommendations.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx


class NetworkAnalyzer:
    """Provides advanced network analysis capabilities for social networks."""
    
    def __init__(self, graph: nx.DiGraph, nodes_dict: Dict[str, str]) -> None:
        """
        Initialize the network analyzer.
        
        Args:
            graph: NetworkX directed graph
            nodes_dict: Dictionary mapping user IDs to names
        """
        self.G = graph
        self.nodes_dict = nodes_dict
    
    # =====================
    # Influence Analysis
    # =====================
    
    def get_most_influential_user(self) -> Optional[Dict]:
        """
        Get the user with the most followers (highest in-degree).
        
        Returns:
            Dict with user_id, name, and followers count, or None if graph is empty
        """
        if self.G.number_of_nodes() == 0:
            return None
        
        in_degrees = dict(self.G.in_degree())
        if not in_degrees:
            return None
        
        most_influential_id = max(in_degrees, key=in_degrees.get)
        
        return {
            'user_id': most_influential_id,
            'name': self.nodes_dict.get(most_influential_id, most_influential_id),
            'followers': in_degrees[most_influential_id]
        }
    
    def get_top_influencers(self, n: int = 5) -> List[Dict]:
        """
        Get top N users with most followers.
        
        Args:
            n: Number of top influencers to return
            
        Returns:
            List of dicts with user info, sorted by follower count descending
        """
        if self.G.number_of_nodes() == 0:
            return []
        
        in_degrees = dict(self.G.in_degree())
        sorted_users = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for user_id, followers in sorted_users[:n]:
            result.append({
                'user_id': user_id,
                'name': self.nodes_dict.get(user_id, user_id),
                'followers': followers
            })
        
        return result
    
    # =====================
    # Activity Analysis
    # =====================
    
    def get_most_active_user(self) -> Optional[Dict]:
        """
        Get the user who follows the most people (highest out-degree).
        
        Returns:
            Dict with user_id, name, and following count, or None if graph is empty
        """
        if self.G.number_of_nodes() == 0:
            return None
        
        out_degrees = dict(self.G.out_degree())
        if not out_degrees:
            return None
        
        most_active_id = max(out_degrees, key=out_degrees.get)
        
        return {
            'user_id': most_active_id,
            'name': self.nodes_dict.get(most_active_id, most_active_id),
            'following': out_degrees[most_active_id]
        }
    
    def get_top_active_users(self, n: int = 5) -> List[Dict]:
        """
        Get top N users who follow the most people.
        
        Args:
            n: Number of top active users to return
            
        Returns:
            List of dicts with user info, sorted by following count descending
        """
        if self.G.number_of_nodes() == 0:
            return []
        
        out_degrees = dict(self.G.out_degree())
        sorted_users = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for user_id, following in sorted_users[:n]:
            result.append({
                'user_id': user_id,
                'name': self.nodes_dict.get(user_id, user_id),
                'following': following
            })
        
        return result
    
    # =====================
    # Connection Analysis
    # =====================
    
    def get_mutual_followers(self, user1_id: str, user2_id: str) -> List[Dict]:
        """
        Get followers common to two users.
        
        Args:
            user1_id: First user ID
            user2_id: Second user ID
            
        Returns:
            List of dicts with common followers info
        """
        # Get predecessors (followers) of both users
        user1_followers = set(self.G.predecessors(user1_id)) if user1_id in self.G else set()
        user2_followers = set(self.G.predecessors(user2_id)) if user2_id in self.G else set()
        
        mutual = user1_followers & user2_followers
        
        result = []
        for follower_id in mutual:
            result.append({
                'user_id': follower_id,
                'name': self.nodes_dict.get(follower_id, follower_id)
            })
        
        return result
    
    def get_mutual_followers_between_many(self, user_ids: List[str]) -> List[Dict]:
        """
        Get followers common to multiple users.
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            List of dicts with common followers
        """
        if not user_ids:
            return []
        
        # Start with followers of first user
        mutual_followers = set(self.G.predecessors(user_ids[0])) if user_ids[0] in self.G else set()
        
        # Intersect with followers of remaining users
        for user_id in user_ids[1:]:
            user_followers = set(self.G.predecessors(user_id)) if user_id in self.G else set()
            mutual_followers &= user_followers
        
        result = []
        for follower_id in mutual_followers:
            result.append({
                'user_id': follower_id,
                'name': self.nodes_dict.get(follower_id, follower_id)
            })
        
        return result
    
    # =====================
    # Recommendation System
    # =====================
    
    def suggest_users_to_follow(self, user_id: str, limit: int = 5) -> List[Dict]:
        """
        Suggest users to follow based on followers of followers.
        
        Args:
            user_id: The user ID to get recommendations for
            limit: Maximum number of recommendations
            
        Returns:
            List of suggested users with relevance score
        """
        if user_id not in self.G:
            return []
        
        # Get users that the given user follows
        following = set(self.G.successors(user_id))
        
        # Get users followed by people the given user follows
        recommendations = defaultdict(int)
        for followed_user in following:
            for suggested_user in self.G.successors(followed_user):
                # Don't recommend users already followed or the user themselves
                if suggested_user not in following and suggested_user != user_id:
                    recommendations[suggested_user] += 1
        
        # Sort by relevance score
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for rec_user_id, score in sorted_recs[:limit]:
            result.append({
                'user_id': rec_user_id,
                'name': self.nodes_dict.get(rec_user_id, rec_user_id),
                'relevance_score': score
            })
        
        return result
    
    def suggest_users_batch(self, user_ids: List[str], limit: int = 5) -> Dict[str, List[Dict]]:
        """
        Get recommendations for multiple users.
        
        Args:
            user_ids: List of user IDs
            limit: Maximum recommendations per user
            
        Returns:
            Dict mapping user_id to list of recommendations
        """
        result = {}
        for user_id in user_ids:
            result[user_id] = self.suggest_users_to_follow(user_id, limit)
        
        return result
    
    # =====================
    # User Connection Info
    # =====================
    
    def get_user_connections(self, user_id: str) -> Optional[Dict]:
        """
        Get detailed connection information for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict with followers, following, and mutual connections
        """
        if user_id not in self.G:
            return None
        
        followers = list(self.G.predecessors(user_id))
        following = list(self.G.successors(user_id))
        mutual = [f for f in followers if f in following]
        
        return {
            'user_id': user_id,
            'name': self.nodes_dict.get(user_id, user_id),
            'followers': followers,
            'following': following,
            'mutual_connections': mutual,
            'follower_count': len(followers),
            'following_count': len(following),
            'mutual_count': len(mutual)
        }
    
    # =====================
    # Engagement Metrics
    # =====================
    
    def get_engagement_score(self, user_id: str) -> float:
        """
        Calculate engagement score for a user (0-100).
        Based on followers, following ratio, and mutual connections.
        
        Args:
            user_id: The user ID
            
        Returns:
            Engagement score between 0 and 100
        """
        if user_id not in self.G:
            return 0.0
        
        followers = len(list(self.G.predecessors(user_id)))
        following = len(list(self.G.successors(user_id)))
        mutual = len([f for f in self.G.predecessors(user_id) if f in self.G.successors(user_id)])
        
        # Score components
        follower_score = min(followers * 5, 30)  # Max 30 points
        following_score = min(following * 5, 30)  # Max 30 points
        mutual_score = min(mutual * 5, 40)  # Max 40 points
        
        return float(follower_score + following_score + mutual_score)
    
    def get_top_engaged_users(self, n: int = 5) -> List[Dict]:
        """
        Get top N users by engagement score.
        
        Args:
            n: Number of top users
            
        Returns:
            List of dicts with user info and engagement score
        """
        if self.G.number_of_nodes() == 0:
            return []
        
        scores = {}
        for user_id in self.G.nodes():
            scores[user_id] = self.get_engagement_score(user_id)
        
        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        result = []
        for user_id, score in sorted_users[:n]:
            result.append({
                'user_id': user_id,
                'name': self.nodes_dict.get(user_id, user_id),
                'engagement_score': score
            })
        
        return result
    
    # =====================
    # Network Health Metrics
    # =====================
    
    def get_network_density(self) -> float:
        """
        Calculate network density (0-1).
        
        Returns:
            Network density value
        """
        if self.G.number_of_nodes() <= 1:
            return 0.0
        
        return nx.density(self.G)
    
    def get_network_clustering_coefficient(self) -> float:
        """
        Calculate average clustering coefficient.
        
        Returns:
            Average clustering coefficient
        """
        if self.G.number_of_nodes() == 0:
            return 0.0
        
        return nx.average_clustering(self.G)
    
    def get_average_path_length(self) -> Optional[float]:
        """
        Calculate average shortest path length for connected component.
        
        Returns:
            Average path length or None if graph is disconnected
        """
        if self.G.number_of_nodes() == 0:
            return None
        
        # For directed graphs, convert to undirected for path length
        undirected = self.G.to_undirected()
        
        if not nx.is_connected(undirected):
            # Return for largest connected component
            largest_cc = max(nx.connected_components(undirected), key=len)
            subgraph = undirected.subgraph(largest_cc)
            if len(subgraph) > 1:
                return nx.average_shortest_path_length(subgraph)
            return 0.0
        
        return nx.average_shortest_path_length(undirected)
