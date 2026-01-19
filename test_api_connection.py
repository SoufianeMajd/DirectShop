#!/usr/bin/env python3
"""
Test script to verify API connections and basic functionality
"""

import requests
import sqlite3
import os

def test_api_connection():
    """Test connection to FakeStore API"""
    try:
        print("🔄 Testing FakeStore API connection...")
        response = requests.get('https://fakestoreapi.com/products?limit=5', timeout=10)
        response.raise_for_status()
        products = response.json()
        
        print(f"✅ API Connection successful!")
        print(f"📦 Sample products received: {len(products)}")
        
        for i, product in enumerate(products[:3], 1):
            print(f"   {i}. {product['title'][:40]} - ${product['price']}")
        
        return True
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        return False

def test_database_connection():
    """Test database connection and structure"""
    try:
        print("\n🔄 Testing database connection...")
        
        if not os.path.exists('database.db'):
            print("❌ Database file not found. Run 'python database.py' first.")
            return False
        
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        
        # Test categories table
        cur.execute("SELECT COUNT(*) FROM categories")
        category_count = cur.fetchone()[0]
        
        # Test products table
        cur.execute("SELECT COUNT(*) FROM products")
        product_count = cur.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Database connection successful!")
        print(f"📂 Categories in database: {category_count}")
        print(f"📦 Products in database: {product_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_image_folder():
    """Test image folder creation"""
    try:
        print("\n🔄 Testing image folder...")
        
        folder_path = 'static/uploads'  # Changed to match Flask app expectations
        os.makedirs(folder_path, exist_ok=True)
        
        # Test write permissions
        test_file = os.path.join(folder_path, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        os.remove(test_file)
        
        print(f"✅ Image folder ready: {folder_path}")
        return True
    except Exception as e:
        print(f"❌ Image folder test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Product Adder Prerequisites")
    print("=" * 50)
    
    api_ok = test_api_connection()
    db_ok = test_database_connection()
    folder_ok = test_image_folder()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"API Connection: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Image Folder: {'✅ PASS' if folder_ok else '❌ FAIL'}")
    
    if all([api_ok, db_ok, folder_ok]):
        print("\n🎉 All tests passed! You can run the product adder scripts.")
        print("\nNext steps:")
        print("1. Run: python simple_product_adder.py")
        print("2. Or double-click: run_product_adder.bat")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        if not db_ok:
            print("   - Run 'python database.py' to create the database")
        if not api_ok:
            print("   - Check your internet connection")
        if not folder_ok:
            print("   - Check folder permissions")

if __name__ == "__main__":
    main()