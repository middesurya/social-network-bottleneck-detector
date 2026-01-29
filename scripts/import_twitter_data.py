"""Import real Twitter data into Neo4j."""
import csv
from neo4j import GraphDatabase
import argparse

def main():
    parser = argparse.ArgumentParser(description='Import Twitter data into Neo4j')
    parser.add_argument('--uri', default='neo4j+s://adb1a905.databases.neo4j.io')
    parser.add_argument('--user', default='neo4j')
    parser.add_argument('--password', required=True)
    parser.add_argument('--clear', action='store_true', help='Clear existing data first')
    args = parser.parse_args()
    
    print(f"Connecting to Neo4j at {args.uri}...")
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    
    with driver.session() as session:
        if args.clear:
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            print("Cleared!")
        
        # Load users
        print("\nLoading users from CSV...")
        users = []
        with open('../data/processed/users.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
        
        print(f"Creating {len(users)} users...")
        # Batch insert users
        batch_size = 500
        for i in range(0, len(users), batch_size):
            batch = users[i:i+batch_size]
            session.run("""
                UNWIND $users AS u
                CREATE (user:User {
                    id: u.user_id,
                    username: u.username,
                    display_name: u.display_name,
                    follower_count: toInteger(u.follower_count),
                    following_count: toInteger(u.following_count),
                    verified: false,
                    bio: 'Real Twitter user from SNAP dataset',
                    tweet_count: 0
                })
            """, {"users": batch})
            print(f"  Created {min(i+batch_size, len(users))}/{len(users)} users")
        
        # Create index
        print("\nCreating index on User.id...")
        session.run("CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)")
        
        # Load edges
        print("\nLoading edges from CSV...")
        edges = []
        with open('../data/processed/edges.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edges.append(row)
        
        print(f"Creating {len(edges)} FOLLOWS relationships...")
        # Batch insert edges
        batch_size = 2000
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i+batch_size]
            session.run("""
                UNWIND $edges AS e
                MATCH (src:User {id: e.source})
                MATCH (dst:User {id: e.target})
                CREATE (src)-[:FOLLOWS]->(dst)
            """, {"edges": batch})
            print(f"  Created {min(i+batch_size, len(edges))}/{len(edges)} relationships")
        
        # Get final stats
        result = session.run("""
            MATCH (u:User) WITH count(u) as users
            MATCH ()-[r:FOLLOWS]->() WITH users, count(r) as edges
            RETURN users, edges
        """)
        stats = result.single()
        print(f"\n✅ Import complete!")
        print(f"   Users: {stats['users']}")
        print(f"   Edges: {stats['edges']}")
    
    driver.close()

if __name__ == "__main__":
    main()
