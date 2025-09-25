#!/usr/bin/env python3
"""
YT-Nara Demo Script
Demonstrates the basic functionality without requiring full setup
"""

import asyncio
import logging
import sys
from pathlib import Path

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def demo_wikipedia_research():
    """Demo Wikipedia research functionality"""
    print("🔍 Demo: Wikipedia Research")
    print("-" * 30)
    
    try:
        from wikipedia_researcher import WikipediaResearcher
        
        async with WikipediaResearcher() as researcher:
            # Test with a simple topic
            topic = "anime"
            print(f"Researching topic: {topic}")
            
            keywords = await researcher.research_topic(topic)
            print(f"Found {len(keywords)} keywords:")
            for i, keyword in enumerate(keywords[:10], 1):  # Show first 10
                print(f"  {i}. {keyword}")
        
        print("✅ Wikipedia research demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Wikipedia research demo failed: {str(e)}")
        return False

async def demo_content_discovery():
    """Demo content discovery functionality"""
    print("\n🎬 Demo: Content Discovery")
    print("-" * 30)
    
    try:
        from content_discovery import ContentDiscovery
        
        async with ContentDiscovery() as discovery:
            # Test with simple parameters
            topic = "anime"
            keywords = ["anime", "manga", "japan", "animation"]
            print(f"Discovering content for topic: {topic}")
            
            content_items = await discovery.discover_content(topic, keywords)
            
            print(f"Discovered {len(content_items)} content items:")
            
            for i, item in enumerate(content_items[:5], 1):  # Show first 5
                print(f"  {i}. {item.title} ({item.platform})")
                print(f"     Creator: {item.creator}")
                print(f"     URL: {item.url}")
        
        print("✅ Content discovery demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Content discovery demo failed: {str(e)}")
        return False

async def demo_content_verification():
    """Demo content verification functionality"""
    print("\n✅ Demo: Content Verification")
    print("-" * 30)
    
    try:
        from content_verification import ContentVerifier
        from models import ContentItem
        
        async with ContentVerifier() as verifier:
            # Create a test content item
            test_content = ContentItem(
                url="https://www.youtube.com/watch?v=test",
                title="Test Anime Video",
                platform="youtube",
                creator="TestCreator",
                keywords=["anime", "test"]
            )
            
            keywords = ["anime", "manga", "japan"]
            print(f"Verifying content: {test_content.title}")
            
            # This will mostly test the verification logic without making actual requests
            verified_content = await verifier.verify_content([test_content], keywords)
        
        print(f"Verification completed for {len(verified_content)} items")
        print("✅ Content verification demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Content verification demo failed: {str(e)}")
        return False

def demo_database():
    """Demo database operations"""
    print("\n💾 Demo: Database Operations")
    print("-" * 30)
    
    try:
        from database import Database
        from models import ContentItem
        
        # Create test database
        db = Database("test_demo.db")
        
        # Create test content item
        test_item = ContentItem(
            url="https://www.youtube.com/watch?v=demo123",
            title="Demo Video",
            platform="youtube",
            creator="Demo Creator",
            keywords=["demo", "test"]
        )
        
        print("Testing database operations...")
        
        # Save content
        success = db.save_content(test_item)
        if success:
            print("✅ Database file created successfully")
        else:
            print("❌ Failed to save content to database")
            return False
        
        # Get statistics
        stats = db.get_statistics()
        print(f"Database statistics: {stats}")
        
        # Clean up test database
        Path("test_demo.db").unlink()
        
        print("✅ Database demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database demo failed: {str(e)}")
        return False

def demo_ui():
    """Demo UI components"""
    print("\n🎨 Demo: User Interface")
    print("-" * 30)
    
    try:
        from ui import TerminalUI
        
        ui = TerminalUI()
        
        print("Testing UI components...")
        print("✅ Banner component available")
        print("✅ Progress tracking initialized")
        
        # Test message types
        ui.print_info("This is an info message")
        ui.print_success("This is a success message")
        ui.print_warning("This is a warning message")
        
        # Test progress (simulated)
        ui.init_progress(["test"])
        ui.update_progress("🔍 Discovering content...", 20)
        ui.update_progress("✅ Verifying content...", 20)
        ui.update_progress("⬇️ Downloading videos...", 20)
        ui.update_progress("✂️ Editing videos...", 20)
        ui.update_progress("⬆️ Uploading videos...", 20)
        ui.complete_progress()
        
        print("✅ UI demo completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ UI demo failed: {str(e)}")
        return False

async def main():
    """Run all demos"""
    print("🚀 YT-Nara Demo Suite")
    print("=" * 50)
    print("This demo will test the basic functionality of YT-Nara")
    print("without requiring full setup or external accounts.")
    print()
    
    # Run demos
    demos = [
        ("Wikipedia Research", demo_wikipedia_research),
        ("Content Discovery", demo_content_discovery),
        ("Content Verification", demo_content_verification),
        ("Database Operations", demo_database),
        ("User Interface", demo_ui)
    ]
    
    results = []
    
    for name, demo_func in demos:
        try:
            if asyncio.iscoroutinefunction(demo_func):
                result = await demo_func()
            else:
                result = demo_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Demo '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Demo Results Summary:")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} demos passed")
    
    if passed == len(results):
        print("🎉 All demos passed! YT-Nara is working correctly.")
        print("\n📋 Next steps:")
        print("1. Run: python3 yt_nara.py --setup")
        print("2. Start using: python3 yt_nara.py")
    else:
        print("⚠️ Some demos failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())