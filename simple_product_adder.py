#!/usr/bin/env python3
"""
Simple script to add products automatically from FakeStore API
This is a simplified version that's easier to use and more reliable
"""

import requests
import sqlite3
import os
import random
import time
import uuid
from urllib.parse import urlparse

# Configuration
DATABASE_PATH = 'database.db'
IMAGES_FOLDER = 'static/uploads'  # Changed to match Flask app expectations
API_URL = 'https://fakestoreapi.com/products'

# Category mapping from API to database
CATEGORY_MAPPING = {
    'electronics': 'Électronique',
    "men's clothing": 'Vêtements', 
    "women's clothing": 'Vêtements',
    'jewelery': 'Accessoires'
}

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    """Get all categories from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT categoryId, name FROM categories")
    categories = {row['name']: row['categoryId'] for row in cur.fetchall()}
    conn.close()
    return categories

def get_default_maker_id():
    """Get or create a default admin user for products"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Try to find an admin user
    cur.execute("SELECT userId FROM users WHERE type = 'admin' LIMIT 1")
    admin = cur.fetchone()
    
    if admin:
        conn.close()
        return admin['userId']
    
    # Create a default admin user if none exists
    try:
        cur.execute("""
            INSERT INTO users (type, email, firstName, lastName, password, acceptation)
            VALUES ('admin', 'system@admin.com', 'System', 'Admin', 'default_hash', 1)
        """)
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return user_id
    except:
        # If insertion fails, return 1 as default
        conn.close()
        return 1

def download_image(image_url, product_name):
    """Download image from URL and save locally"""
    try:
        # Create images folder if it doesn't exist
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        
        # Generate unique filename
        clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')[:20]  # Limit length
        filename = f"{clean_name}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        # Download image
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Return just the filename for database (Flask expects uploads/filename format)
        return filename
        
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def fetch_products():
    """Fetch products from FakeStore API"""
    try:
        print("🔄 Fetching products from FakeStore API...")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        products = response.json()
        print(f"✅ Fetched {len(products)} products")
        return products
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return []

def product_exists(name, price):
    """Check if product already exists in database"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT productId FROM products WHERE name = ? AND price = ?", (name, price))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def add_product_to_db(product, category_id, maker_id, image_path):
    """Add product to database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO products (name, price, description, image, stock, categoryId, maker)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            product['title'][:255],  # Limit name length
            float(product['price']),
            product['description'][:1000],  # Limit description length
            image_path or 'default_product.png',
            random.randint(10, 100),  # Random stock
            category_id,
            maker_id
        ))
        
        product_id = cur.lastrowid
        conn.commit()
        conn.close()
        return product_id
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def add_products_simple(max_products=20):
    """Simple function to add products"""
    print("🚀 Starting simple product addition...")
    print("=" * 50)
    
    # Get database info
    db_categories = get_categories()
    maker_id = get_default_maker_id()
    
    print(f"📂 Database categories: {list(db_categories.keys())}")
    print(f"👤 Using maker ID: {maker_id}")
    
    # Fetch products
    api_products = fetch_products()
    if not api_products:
        print("❌ No products to add")
        return
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"\n🔄 Adding up to {max_products} products...")
    print("-" * 50)
    
    for product in api_products:
        if added_count >= max_products:
            break
            
        try:
            # Skip if product already exists
            if product_exists(product['title'], product['price']):
                skipped_count += 1
                print(f"⏭️  Skipped (exists): {product['title'][:30]}")
                continue
            
            # Map category
            api_category = product.get('category', 'electronics')
            db_category_name = CATEGORY_MAPPING.get(api_category, 'Électronique')
            category_id = db_categories.get(db_category_name, list(db_categories.values())[0])
            
            # Download image
            image_path = None
            if product.get('image'):
                print(f"📥 Downloading image for: {product['title'][:30]}...")
                image_path = download_image(product['image'], product['title'])
            
            # Add to database
            product_id = add_product_to_db(product, category_id, maker_id, image_path)
            added_count += 1
            
            print(f"✅ Added: {product['title'][:40]} | ${product['price']} | {db_category_name}")
            
            # Small delay
            time.sleep(0.5)
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error adding {product['title'][:30]}: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"✅ Products added: {added_count}")
    print(f"⏭️  Products skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"\n🎉 Done! {added_count} products added to your store.")

def main():
    """Main function"""
    print("🛍️  Simple Product Adder")
    print("This will add products from FakeStore API to your database")
    print()
    
    try:
        # Ask for number of products
        try:
            max_products = int(input("How many products to add? (default: 20): ") or "20")
            if max_products > 20:
                print("⚠️  Maximum 20 products recommended for this simple version")
                max_products = min(max_products, 20)
        except ValueError:
            max_products = 20
        
        # Confirm
        confirm = input(f"Add {max_products} products? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Cancelled")
            return
        
        # Start
        add_products_simple(max_products)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()