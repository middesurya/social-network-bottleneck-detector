// Social Network Bottleneck Detector - Neo4j Schema
// Run this file to initialize the database schema

// =====================================================
// CONSTRAINTS - Ensure data integrity
// =====================================================

// User constraints
CREATE CONSTRAINT user_id IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT user_username IF NOT EXISTS  
FOR (u:User) REQUIRE u.username IS UNIQUE;

// Tweet constraints
CREATE CONSTRAINT tweet_id IF NOT EXISTS
FOR (t:Tweet) REQUIRE t.id IS UNIQUE;

// Community constraints
CREATE CONSTRAINT community_id IF NOT EXISTS
FOR (c:Community) REQUIRE c.id IS UNIQUE;

// Hashtag constraints
CREATE CONSTRAINT hashtag_tag IF NOT EXISTS
FOR (h:Hashtag) REQUIRE h.tag IS UNIQUE;


// =====================================================
// INDEXES - Optimize query performance
// =====================================================

// User indexes for common queries
CREATE INDEX user_follower_count IF NOT EXISTS
FOR (u:User) ON (u.follower_count);

CREATE INDEX user_bottleneck_score IF NOT EXISTS
FOR (u:User) ON (u.bottleneck_score);

CREATE INDEX user_community_id IF NOT EXISTS
FOR (u:User) ON (u.community_id);

CREATE INDEX user_pagerank IF NOT EXISTS
FOR (u:User) ON (u.pagerank);

CREATE INDEX user_betweenness IF NOT EXISTS
FOR (u:User) ON (u.betweenness_centrality);

CREATE INDEX user_is_bottleneck IF NOT EXISTS
FOR (u:User) ON (u.is_bottleneck);

// Tweet indexes
CREATE INDEX tweet_user_id IF NOT EXISTS
FOR (t:Tweet) ON (t.user_id);

CREATE INDEX tweet_created_at IF NOT EXISTS
FOR (t:Tweet) ON (t.created_at);

// Community indexes
CREATE INDEX community_member_count IF NOT EXISTS
FOR (c:Community) ON (c.member_count);


// =====================================================
// NODE LABELS - Documentation
// =====================================================

// User Node Properties:
// - id: string (unique identifier)
// - username: string (Twitter handle)
// - display_name: string (display name)
// - bio: string (user bio)
// - follower_count: integer
// - following_count: integer
// - tweet_count: integer
// - verified: boolean
// - created_at: string (ISO date)
// - pagerank: float (calculated)
// - betweenness_centrality: float (calculated)
// - degree_centrality: float (calculated)
// - bottleneck_score: float (calculated)
// - bridge_score: float (calculated)
// - is_bottleneck: boolean (calculated)
// - community_id: string (calculated)

// Tweet Node Properties:
// - id: string (unique identifier)
// - user_id: string (author's user id)
// - text: string (tweet content)
// - created_at: string (ISO datetime)
// - retweet_count: integer
// - like_count: integer
// - reply_count: integer
// - quote_count: integer
// - is_retweet: boolean
// - is_reply: boolean
// - engagement_score: float (calculated)

// Community Node Properties:
// - id: string (unique identifier)
// - name: string (optional label)
// - member_count: integer
// - internal_edges: integer
// - external_edges: integer
// - modularity_contribution: float
// - avg_betweenness: float
// - avg_pagerank: float

// Hashtag Node Properties:
// - tag: string (hashtag without #)
// - usage_count: integer


// =====================================================
// RELATIONSHIPS
// =====================================================

// (:User)-[:FOLLOWS]->(:User)
// Properties: created_at, weight

// (:User)-[:POSTED]->(:Tweet)

// (:Tweet)-[:MENTIONS]->(:User)

// (:Tweet)-[:REPLY_TO]->(:Tweet)

// (:Tweet)-[:RETWEET_OF]->(:Tweet)

// (:Tweet)-[:USES]->(:Hashtag)

// (:User)-[:MEMBER_OF]->(:Community)


// =====================================================
// SAMPLE DATA - For testing
// =====================================================

// Create sample users
MERGE (u1:User {id: 'user_1', username: 'alice', display_name: 'Alice Johnson', follower_count: 1500, following_count: 300, tweet_count: 500, verified: false})
MERGE (u2:User {id: 'user_2', username: 'bob', display_name: 'Bob Smith', follower_count: 2500, following_count: 150, tweet_count: 800, verified: true})
MERGE (u3:User {id: 'user_3', username: 'carol', display_name: 'Carol Williams', follower_count: 800, following_count: 400, tweet_count: 300, verified: false})
MERGE (u4:User {id: 'user_4', username: 'david', display_name: 'David Brown', follower_count: 5000, following_count: 200, tweet_count: 1200, verified: true})
MERGE (u5:User {id: 'user_5', username: 'eve', display_name: 'Eve Davis', follower_count: 300, following_count: 500, tweet_count: 150, verified: false})
MERGE (u6:User {id: 'user_6', username: 'frank', display_name: 'Frank Miller', follower_count: 1200, following_count: 350, tweet_count: 400, verified: false})
MERGE (u7:User {id: 'user_7', username: 'grace', display_name: 'Grace Wilson', follower_count: 3500, following_count: 180, tweet_count: 900, verified: true})
MERGE (u8:User {id: 'user_8', username: 'henry', display_name: 'Henry Taylor', follower_count: 600, following_count: 600, tweet_count: 250, verified: false})

// Create follow relationships forming distinct communities with bridges
// Community A: alice, bob, carol
MERGE (u1)-[:FOLLOWS]->(u2)
MERGE (u2)-[:FOLLOWS]->(u1)
MERGE (u1)-[:FOLLOWS]->(u3)
MERGE (u3)-[:FOLLOWS]->(u1)
MERGE (u2)-[:FOLLOWS]->(u3)
MERGE (u3)-[:FOLLOWS]->(u2)

// Community B: david, eve, frank  
MERGE (u4)-[:FOLLOWS]->(u5)
MERGE (u5)-[:FOLLOWS]->(u4)
MERGE (u4)-[:FOLLOWS]->(u6)
MERGE (u6)-[:FOLLOWS]->(u4)
MERGE (u5)-[:FOLLOWS]->(u6)
MERGE (u6)-[:FOLLOWS]->(u5)

// Community C: grace, henry
MERGE (u7)-[:FOLLOWS]->(u8)
MERGE (u8)-[:FOLLOWS]->(u7)

// Bridge connections (bottleneck nodes)
// Bob bridges Community A and B
MERGE (u2)-[:FOLLOWS]->(u4)
MERGE (u4)-[:FOLLOWS]->(u2)

// Frank bridges Community B and C
MERGE (u6)-[:FOLLOWS]->(u7)
MERGE (u7)-[:FOLLOWS]->(u6)

// Carol also bridges A and C (secondary bridge)
MERGE (u3)-[:FOLLOWS]->(u8)

// Set initial community IDs
MATCH (u:User) WHERE u.id IN ['user_1', 'user_2', 'user_3']
SET u.community_id = 'community_a';

MATCH (u:User) WHERE u.id IN ['user_4', 'user_5', 'user_6']
SET u.community_id = 'community_b';

MATCH (u:User) WHERE u.id IN ['user_7', 'user_8']
SET u.community_id = 'community_c';

// Return sample data info
MATCH (u:User) RETURN count(u) as users;
MATCH ()-[r:FOLLOWS]->() RETURN count(r) as relationships;
