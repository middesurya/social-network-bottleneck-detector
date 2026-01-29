"""Process SNAP Twitter dataset for import - fast version."""

print("Loading first 50,000 edges from Twitter dataset...")

edges = []
users = set()
MAX_EDGES = 50000

with open('twitter_combined.txt', 'r') as f:
    for i, line in enumerate(f):
        if i >= MAX_EDGES:
            break
        parts = line.strip().split()
        if len(parts) == 2:
            src, dst = parts
            edges.append((src, dst))
            users.add(src)
            users.add(dst)

print(f"Loaded: {len(edges):,} edges, {len(users):,} users")

# Count connections
user_connections = {}
for src, dst in edges:
    user_connections[src] = user_connections.get(src, 0) + 1
    user_connections[dst] = user_connections.get(dst, 0) + 1

# Create user CSV
print("Writing users.csv...")
with open('processed/users.csv', 'w') as f:
    f.write("user_id,username,display_name,follower_count,following_count\n")
    for user_id in users:
        username = f"tw_{user_id[-8:]}"
        display_name = f"Twitter {user_id[-8:]}"
        followers = sum(1 for s, d in edges if d == user_id)
        following = sum(1 for s, d in edges if s == user_id)
        f.write(f"{user_id},{username},{display_name},{followers},{following}\n")

# Create edges CSV
print("Writing edges.csv...")
with open('processed/edges.csv', 'w') as f:
    f.write("source,target\n")
    for src, dst in edges:
        f.write(f"{src},{dst}\n")

print(f"\nDone! Created:")
print(f"  - processed/users.csv ({len(users)} users)")
print(f"  - processed/edges.csv ({len(edges)} edges)")
