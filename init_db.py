"""Initialize Neo4j Aura database with schema and sample data."""
from neo4j import GraphDatabase

# Neo4j Aura credentials
URI = "neo4j+s://adb1a905.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "WiyeDT9DsU3k7tdKTKJePuoXGN9Qs5M9ok31qsPBo94"

def init_database():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    with driver.session() as session:
        # Create constraints
        print("Creating constraints...")
        constraints = [
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE",
            "CREATE CONSTRAINT tweet_id IF NOT EXISTS FOR (t:Tweet) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT community_id IF NOT EXISTS FOR (c:Community) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT hashtag_tag IF NOT EXISTS FOR (h:Hashtag) REQUIRE h.tag IS UNIQUE",
        ]
        for c in constraints:
            try:
                session.run(c)
                print(f"  OK: constraint created")
            except Exception as e:
                print(f"  Skipped: {str(e)[:50]}...")

        # Create indexes
        print("\nCreating indexes...")
        indexes = [
            "CREATE INDEX user_follower_count IF NOT EXISTS FOR (u:User) ON (u.follower_count)",
            "CREATE INDEX user_bottleneck_score IF NOT EXISTS FOR (u:User) ON (u.bottleneck_score)",
            "CREATE INDEX user_community_id IF NOT EXISTS FOR (u:User) ON (u.community_id)",
            "CREATE INDEX user_pagerank IF NOT EXISTS FOR (u:User) ON (u.pagerank)",
            "CREATE INDEX user_betweenness IF NOT EXISTS FOR (u:User) ON (u.betweenness_centrality)",
        ]
        for idx in indexes:
            try:
                session.run(idx)
                print(f"  OK: index created")
            except Exception as e:
                print(f"  Skipped: {str(e)[:50]}...")

        # Create sample users
        print("\nCreating sample users...")
        users = [
            {"id": "user_1", "username": "alice", "display_name": "Alice Johnson", "follower_count": 1500, "following_count": 300, "tweet_count": 500, "verified": False},
            {"id": "user_2", "username": "bob", "display_name": "Bob Smith", "follower_count": 2500, "following_count": 150, "tweet_count": 800, "verified": True},
            {"id": "user_3", "username": "carol", "display_name": "Carol Williams", "follower_count": 800, "following_count": 400, "tweet_count": 300, "verified": False},
            {"id": "user_4", "username": "david", "display_name": "David Brown", "follower_count": 5000, "following_count": 200, "tweet_count": 1200, "verified": True},
            {"id": "user_5", "username": "eve", "display_name": "Eve Davis", "follower_count": 300, "following_count": 500, "tweet_count": 150, "verified": False},
            {"id": "user_6", "username": "frank", "display_name": "Frank Miller", "follower_count": 1200, "following_count": 350, "tweet_count": 400, "verified": False},
            {"id": "user_7", "username": "grace", "display_name": "Grace Wilson", "follower_count": 3500, "following_count": 180, "tweet_count": 900, "verified": True},
            {"id": "user_8", "username": "henry", "display_name": "Henry Taylor", "follower_count": 600, "following_count": 600, "tweet_count": 250, "verified": False},
        ]
        
        for user in users:
            session.run("""
                MERGE (u:User {id: $id})
                SET u.username = $username,
                    u.display_name = $display_name,
                    u.follower_count = $follower_count,
                    u.following_count = $following_count,
                    u.tweet_count = $tweet_count,
                    u.verified = $verified
            """, **user)
            print(f"  Created user: {user['username']}")

        # Create follow relationships
        print("\nCreating follow relationships...")
        follows = [
            # Community A: alice, bob, carol
            ("user_1", "user_2"), ("user_2", "user_1"),
            ("user_1", "user_3"), ("user_3", "user_1"),
            ("user_2", "user_3"), ("user_3", "user_2"),
            # Community B: david, eve, frank
            ("user_4", "user_5"), ("user_5", "user_4"),
            ("user_4", "user_6"), ("user_6", "user_4"),
            ("user_5", "user_6"), ("user_6", "user_5"),
            # Community C: grace, henry
            ("user_7", "user_8"), ("user_8", "user_7"),
            # Bridge connections (bottleneck nodes)
            ("user_2", "user_4"), ("user_4", "user_2"),  # Bob bridges A and B
            ("user_6", "user_7"), ("user_7", "user_6"),  # Frank bridges B and C
            ("user_3", "user_8"),  # Carol also bridges A and C
        ]
        
        for from_id, to_id in follows:
            session.run("""
                MATCH (a:User {id: $from_id}), (b:User {id: $to_id})
                MERGE (a)-[:FOLLOWS]->(b)
            """, from_id=from_id, to_id=to_id)
        print(f"  Created {len(follows)} follow relationships")

        # Set community IDs
        print("\nAssigning communities...")
        session.run("MATCH (u:User) WHERE u.id IN ['user_1', 'user_2', 'user_3'] SET u.community_id = 'community_a'")
        session.run("MATCH (u:User) WHERE u.id IN ['user_4', 'user_5', 'user_6'] SET u.community_id = 'community_b'")
        session.run("MATCH (u:User) WHERE u.id IN ['user_7', 'user_8'] SET u.community_id = 'community_c'")
        print("  Assigned community IDs")

        # Verify
        result = session.run("MATCH (u:User) RETURN count(u) as users")
        users_count = result.single()["users"]
        result = session.run("MATCH ()-[r:FOLLOWS]->() RETURN count(r) as rels")
        rels_count = result.single()["rels"]
        
        print(f"\nDatabase initialized!")
        print(f"   Users: {users_count}")
        print(f"   Relationships: {rels_count}")

    driver.close()

if __name__ == "__main__":
    init_database()
