#!/usr/bin/env python3
"""
Data import script for Social Network Bottleneck Detector.

Imports user and edge data from CSV files into Neo4j.

Usage:
    python import_data.py --users data/raw/users.csv --edges data/raw/edges.csv
    python import_data.py --sample  # Generate and import sample data
"""

import argparse
import csv
import logging
import random
import string
import sys
from pathlib import Path
from typing import Optional

from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


class DataImporter:
    """Import data into Neo4j."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared existing data")
    
    def import_users(self, filepath: Path, batch_size: int = 1000):
        """Import users from CSV file."""
        logger.info(f"Importing users from {filepath}")
        
        users = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append({
                    'id': row.get('user_id') or row.get('id'),
                    'username': row.get('username') or row.get('screen_name') or row.get('id'),
                    'display_name': row.get('display_name') or row.get('name'),
                    'bio': row.get('bio') or row.get('description'),
                    'follower_count': int(row.get('follower_count') or row.get('followers_count') or 0),
                    'following_count': int(row.get('following_count') or row.get('friends_count') or 0),
                    'tweet_count': int(row.get('tweet_count') or row.get('statuses_count') or 0),
                    'verified': row.get('verified', '').lower() == 'true',
                })
        
        # Batch import
        with self.driver.session() as session:
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                session.run("""
                    UNWIND $users AS user
                    MERGE (u:User {id: user.id})
                    SET u.username = user.username,
                        u.display_name = user.display_name,
                        u.bio = user.bio,
                        u.follower_count = user.follower_count,
                        u.following_count = user.following_count,
                        u.tweet_count = user.tweet_count,
                        u.verified = user.verified
                """, users=batch)
                logger.info(f"Imported users {i+1} to {min(i+batch_size, len(users))}")
        
        logger.info(f"Successfully imported {len(users)} users")
        return len(users)
    
    def import_edges(self, filepath: Path, batch_size: int = 5000):
        """Import edges from CSV file."""
        logger.info(f"Importing edges from {filepath}")
        
        edges = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edges.append({
                    'source': row.get('source_id') or row.get('source') or row.get('follower_id'),
                    'target': row.get('target_id') or row.get('target') or row.get('followed_id'),
                })
        
        # Batch import
        with self.driver.session() as session:
            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]
                session.run("""
                    UNWIND $edges AS edge
                    MATCH (source:User {id: edge.source})
                    MATCH (target:User {id: edge.target})
                    MERGE (source)-[:FOLLOWS]->(target)
                """, edges=batch)
                logger.info(f"Imported edges {i+1} to {min(i+batch_size, len(edges))}")
        
        logger.info(f"Successfully imported {len(edges)} edges")
        return len(edges)
    
    def generate_sample_data(self, num_users: int = 100, avg_connections: int = 5):
        """Generate sample data for testing."""
        logger.info(f"Generating sample data: {num_users} users")
        
        # Generate users
        users = []
        for i in range(num_users):
            users.append({
                'id': f'user_{i}',
                'username': f'user{i}',
                'display_name': f'User {i}',
                'bio': f'Sample user {i} for testing',
                'follower_count': random.randint(10, 10000),
                'following_count': random.randint(10, 1000),
                'tweet_count': random.randint(0, 5000),
                'verified': random.random() < 0.1,
            })
        
        # Create users
        with self.driver.session() as session:
            session.run("""
                UNWIND $users AS user
                MERGE (u:User {id: user.id})
                SET u.username = user.username,
                    u.display_name = user.display_name,
                    u.bio = user.bio,
                    u.follower_count = user.follower_count,
                    u.following_count = user.following_count,
                    u.tweet_count = user.tweet_count,
                    u.verified = user.verified
            """, users=users)
        
        # Generate edges with community structure
        # Create 3-5 communities
        num_communities = random.randint(3, 5)
        community_size = num_users // num_communities
        
        edges = []
        for i in range(num_users):
            # Determine community
            community = i // community_size
            
            # More connections within community
            num_connections = random.randint(2, avg_connections * 2)
            for _ in range(num_connections):
                if random.random() < 0.8:  # 80% within community
                    target = random.randint(
                        community * community_size,
                        min((community + 1) * community_size - 1, num_users - 1)
                    )
                else:  # 20% to other communities
                    target = random.randint(0, num_users - 1)
                
                if target != i:
                    edges.append({'source': f'user_{i}', 'target': f'user_{target}'})
        
        # Remove duplicates
        unique_edges = list({(e['source'], e['target']): e for e in edges}.values())
        
        # Create edges
        with self.driver.session() as session:
            for i in range(0, len(unique_edges), 1000):
                batch = unique_edges[i:i + 1000]
                session.run("""
                    UNWIND $edges AS edge
                    MATCH (source:User {id: edge.source})
                    MATCH (target:User {id: edge.target})
                    MERGE (source)-[:FOLLOWS]->(target)
                """, edges=batch)
        
        logger.info(f"Generated {len(users)} users and {len(unique_edges)} edges")
        return len(users), len(unique_edges)
    
    def get_stats(self):
        """Get database statistics."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)
                WITH count(u) as users
                MATCH ()-[r:FOLLOWS]->()
                RETURN users, count(r) as edges
            """)
            record = result.single()
            return {
                'users': record['users'],
                'edges': record['edges']
            }


def main():
    parser = argparse.ArgumentParser(description='Import data into Neo4j')
    parser.add_argument('--users', type=Path, help='Path to users CSV file')
    parser.add_argument('--edges', type=Path, help='Path to edges CSV file')
    parser.add_argument('--sample', action='store_true', help='Generate sample data')
    parser.add_argument('--sample-size', type=int, default=100, help='Number of sample users')
    parser.add_argument('--clear', action='store_true', help='Clear database before import')
    parser.add_argument('--uri', default=NEO4J_URI, help='Neo4j URI')
    parser.add_argument('--user', default=NEO4J_USER, help='Neo4j username')
    parser.add_argument('--password', default=NEO4J_PASSWORD, help='Neo4j password')
    
    args = parser.parse_args()
    
    if not args.sample and not (args.users and args.edges):
        parser.error("Either --sample or both --users and --edges are required")
    
    importer = DataImporter(args.uri, args.user, args.password)
    
    try:
        if args.clear:
            importer.clear_database()
        
        if args.sample:
            importer.generate_sample_data(args.sample_size)
        else:
            if args.users:
                importer.import_users(args.users)
            if args.edges:
                importer.import_edges(args.edges)
        
        stats = importer.get_stats()
        logger.info(f"Final stats: {stats['users']} users, {stats['edges']} edges")
        
    finally:
        importer.close()


if __name__ == '__main__':
    main()
