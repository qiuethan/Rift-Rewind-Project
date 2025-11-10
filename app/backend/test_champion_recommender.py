"""
Test script for champion recommendation system
"""
import asyncio
from utils.champion_recommender import get_recommender


async def test_recommender():
    """Test the champion recommender with sample data"""
    
    print("=" * 60)
    print("Testing Champion Recommendation System")
    print("=" * 60)
    
    # Get recommender instance
    recommender = get_recommender()
    
    print(f"\n✓ Loaded graph with {len(recommender.champ_node_data)} champions")
    print(f"✓ Graph has {len(recommender.graph)} champion nodes")
    
    # Test 1: Recommend based on a mage-heavy pool
    print("\n" + "=" * 60)
    print("Test 1: Mage-heavy champion pool")
    print("=" * 60)
    
    mage_pool = ["Ahri", "Lux", "Syndra", "Orianna"]
    print(f"Champion Pool: {', '.join(mage_pool)}")
    
    recommendations = recommender.recommend_from_champion_pool(
        champion_list=mage_pool,
        top_k=5,
        alpha=0.7
    )
    
    print("\nRecommendations:")
    for i, (champ, score) in enumerate(recommendations, 1):
        print(f"  {i}. {champ:15s} - Score: {score:.4f}")
    
    # Test 2: Recommend based on assassin pool
    print("\n" + "=" * 60)
    print("Test 2: Assassin-heavy champion pool")
    print("=" * 60)
    
    assassin_pool = ["Zed", "Talon", "Katarina", "Akali"]
    print(f"Champion Pool: {', '.join(assassin_pool)}")
    
    recommendations = recommender.recommend_from_champion_pool(
        champion_list=assassin_pool,
        top_k=5,
        alpha=0.7
    )
    
    print("\nRecommendations:")
    for i, (champ, score) in enumerate(recommendations, 1):
        print(f"  {i}. {champ:15s} - Score: {score:.4f}")
    
    # Test 3: Mixed pool
    print("\n" + "=" * 60)
    print("Test 3: Mixed champion pool")
    print("=" * 60)
    
    mixed_pool = ["Yasuo", "Ahri", "LeeSin", "Thresh", "Jinx"]
    print(f"Champion Pool: {', '.join(mixed_pool)}")
    
    recommendations = recommender.recommend_from_champion_pool(
        champion_list=mixed_pool,
        top_k=5,
        alpha=0.7
    )
    
    print("\nRecommendations:")
    for i, (champ, score) in enumerate(recommendations, 1):
        # Get playstyle tags
        champ_row = recommender.champ_node_data[
            recommender.champ_node_data['championName'] == champ
        ]
        tags = []
        if not champ_row.empty:
            tag_cols = [col for col in champ_row.columns if col.startswith('tag_')]
            for col in tag_cols:
                if champ_row[col].values[0] == 1:
                    tags.append(col.replace('tag_', ''))
        
        tags_str = ", ".join(tags) if tags else "N/A"
        print(f"  {i}. {champ:15s} - Score: {score:.4f} - Tags: {tags_str}")
    
    # Test 4: Test with filters
    print("\n" + "=" * 60)
    print("Test 4: Recommendations with filters (Mages only)")
    print("=" * 60)
    
    print(f"Champion Pool: {', '.join(mage_pool)}")
    
    recommendations = recommender.recommend_from_champion_pool(
        champion_list=mage_pool,
        top_k=5,
        alpha=0.7,
        filters={"tag_Mage": 1}  # Only recommend mages
    )
    
    print("\nRecommendations (Mages only):")
    for i, (champ, score) in enumerate(recommendations, 1):
        print(f"  {i}. {champ:15s} - Score: {score:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_recommender())
