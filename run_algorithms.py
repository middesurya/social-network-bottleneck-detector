"""Run all algorithms on the Twitter data."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://adb1a905.databases.neo4j.io', 
    auth=('neo4j', 'WiyeDT9DsU3k7tdKTKJePuoXGN9Qs5M9ok31qsPBo94')
)

with driver.session() as session:
    print('Running PageRank...')
    session.run('''
        MATCH (u:User)
        WITH count(u) as totalNodes
        MATCH (u:User)
        SET u.pagerank = 1.0 / totalNodes
    ''')
    for i in range(10):
        session.run('''
            MATCH (u:User)
            OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
            WITH u, COALESCE(sum(follower.pagerank), 0) as incomingRank
            SET u.pagerank = 0.15 + 0.85 * incomingRank
        ''')
    print('PageRank done!')
    
    print('Running Community Detection...')
    session.run('MATCH (u:User) SET u.community_id = u.id')
    for i in range(5):
        session.run('''
            MATCH (u:User)-[:FOLLOWS]-(neighbor:User)
            WITH u, neighbor.community_id as neighborCommunity, count(*) as weight
            ORDER BY weight DESC
            WITH u, collect(neighborCommunity)[0] as dominantCommunity
            SET u.community_id = dominantCommunity
        ''')
    print('Communities done!')
    
    print('Setting Betweenness...')
    session.run('''
        MATCH (u:User)
        OPTIONAL MATCH (u)-[r:FOLLOWS]->()
        WITH u, count(r) as outDegree
        OPTIONAL MATCH (u)<-[r2:FOLLOWS]-()
        WITH u, outDegree, count(r2) as inDegree
        WITH u, outDegree, inDegree, outDegree + inDegree as degree
        SET u.betweenness_centrality = CASE WHEN degree > 0 THEN toFloat(outDegree * inDegree) / (degree * degree) ELSE 0.0 END,
            u.out_degree = outDegree,
            u.in_degree = inDegree
    ''')
    print('Betweenness done!')
    
    print('Calculating Bottleneck scores...')
    session.run('''
        MATCH (u:User)
        WHERE u.pagerank IS NOT NULL AND u.betweenness_centrality IS NOT NULL
        OPTIONAL MATCH (u)-[:FOLLOWS]-(neighbor:User)
        WHERE neighbor.community_id IS NOT NULL AND neighbor.community_id <> u.community_id
        WITH u, count(DISTINCT neighbor.community_id) as bridgedCommunities
        WITH u, bridgedCommunities,
             COALESCE(u.betweenness_centrality, 0) as betweenness,
             COALESCE(u.pagerank, 0) as pagerank
        MATCH (all:User)
        WITH u, bridgedCommunities, betweenness, pagerank,
             COALESCE(max(all.betweenness_centrality), 1) as maxBetweenness,
             COALESCE(max(all.pagerank), 1) as maxPagerank
        WITH u,
             CASE WHEN maxBetweenness > 0 THEN betweenness / maxBetweenness ELSE 0 END as normBetweenness,
             CASE WHEN maxPagerank > 0 THEN pagerank / maxPagerank ELSE 0 END as normPagerank,
             toFloat(bridgedCommunities) / 5.0 as bridgeScore
        SET u.bridge_score = bridgeScore,
            u.bottleneck_score = (0.4 * normBetweenness) + (0.3 * normPagerank) + (0.3 * bridgeScore),
            u.is_bottleneck = CASE WHEN (0.4 * normBetweenness) + (0.3 * normPagerank) + (0.3 * bridgeScore) > 0.3 THEN true ELSE false END
    ''')
    print('Bottleneck scores done!')
    
    # Get stats
    result = session.run('''
        MATCH (u:User) 
        RETURN count(u) as users,
               count(DISTINCT u.community_id) as communities,
               sum(CASE WHEN u.is_bottleneck THEN 1 ELSE 0 END) as bottlenecks
    ''')
    stats = result.single()
    print("Stats: {} users, {} communities, {} bottlenecks".format(
        stats["users"], stats["communities"], stats["bottlenecks"]
    ))

driver.close()
print('All algorithms completed!')
