"""Process SNAP Twitter dataset for import."""
import random

print("Loading Twitter dataset...")

# Read all edges
edges = []
users = set()

with open('twitter_combined.txt', 'r') as f:
    for i, line in enumerate(f):
        if i > 0 and i % 500000 == 0:
            print(f"Read {i:,} edges...")
        parts = line.strip().split()
        if len(parts) == 2:
            src, dst = parts
            edges.append((src, dst))
            users.add(src)
            users.add(dst)

print(f"Total: {len(edges):,} edges, {len(users):,} users")

# Sample ~2000 users by taking users with most connections
print("\nFinding most connected users...")
user_connections = {}
for src, dst in edges:
    user_connections[src] = user_connections.get(src, 0) + 1
    user_connections[dst] = user_connections.get(dst, 0) + 1

# Get top 2000 most connected users
top_users = sorted(user_connections.items(), key=lambda x: -x[1])[:2000]
selected_users = set(u for u, _ in top_users)
print(f"Selected {len(selected_users)} most connected users")

# Filter edges to only include selected users
filtered_edges = [(s, d) for s, d in edges if s in selected_users and d in selected_users]
print(f"Filtered to {len(filtered_edges):,} edges")

# Create user CSV
print("\nWriting users.csv...")
with open('processed/users.csv', 'w') as f:
    f.write("user_id,username,display_name,follower_count,following_count\n")
    for user_id in selected_users:
        username = f"user_{user_id[-6:]}"  # Use last 6 digits as username
        display_name = f"Twitter User {user_id[-6:]}"
        followers = sum(1 for s, d in filtered_edges if d == user_id)
        following = sum(1 for s, d in filtered_edges if s == user_id)
        f.write(f"{user_id},{username},{display_name},{followers},{following}\n")

# Create edges CSV
print("Writing edges.csv...")
with open('processed/edges.csv', 'w') as f:
    f.write("source,target\n")
    for src, dst in filtered_edges:
        f.write(f"{src},{dst}\n")

print(f"\nDone! Created:")
print(f"  - processed/users.csv ({len(selected_users)} users)")
print(f"  - processed/edges.csv ({len(filtered_edges)} edges)")
