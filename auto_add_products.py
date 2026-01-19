#!/usr/bin/env python3
"""
Script to automatically add products with relevant images from e-commerce APIs
Supports multiple APIs: FakeStore API, DummyJSON, and Platzi Fake Store API
"""

import requests
import sqlite3
import os
import random
import time
from urllib.parse import urlparse
import uuid
from datetime import datetime

# Configuration
DATABASE_PATH = 'database.db'
IMAGES_FOLDER = 'static/uploads'  # Changed to match Flask app expectations
MAX_PRODUCTS_PER_CATEGORY = 5
DELAY_BETWEEN_REQUESTS = 0.5  # seconds

# Multiple API sources for better product variety
API_SOURCES = {
    'fakestore': {
        'url': 'https://fakestoreapi.com/products',
        'category_field': 'category',
        'categories': {
            'Électronique': 'electronics',
            'Vêtements': "women's clothing",
            'Chaussures': "men's clothing",
            'Accessoires': 'jewelery',
            'Cosmétiques': "women's clothing",
            'Sport': "men's clothing",
            'Informatique': 'electronics'
        }
    },
    'dummyjson': {
        'url': 'https://dummyjson.com/products',
        'category_field': 'category',
        'categories': {
            'Électronique': 'smartphones',
            'Informatique': 'laptops',
            'Cosmétiques': 'skincare',
            'Meubles': 'furniture',
            'Alimentation': 'groceries',
            'Automobile': 'automotive',
            'Vêtements': 'womens-dresses',
            'Chaussures': 'womens-shoes',
            'Accessoires': 'womens-bags',
            'Sport': 'sports-accessories'
        }
    },
    'platzi': {
        'url': 'https://api.escuelajs.co/api/v1/products',
        'category_field': 'category',
        'categories': {
            'Électronique': 'Electronics',
            'Vêtements': 'Clothes',
            'Chaussures': 'Shoes',
            'Meubles': 'Furniture',
            'Jouets': 'Miscellaneous'
        }
    }
}

class ProductAutoAdder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_categories(self):
        """Get all categories from database"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = {row['name']: row['categoryId'] for row in cur.fetchall()}
        conn.close()
        return categories
    
    def get_default_maker_id(self):
        """Get or create a default admin user for products"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Try to find an admin user
        cur.execute("SELECT userId FROM users WHERE type = 'admin' LIMIT 1")
        admin = cur.fetchone()
        
        if admin:
            conn.close()
            return admin['userId']
        
        # Create a default admin user if none exists
        cur.execute("""
            INSERT INTO users (type, email, firstName, lastName, password, acceptation)
            VALUES ('admin', 'system@admin.com', 'System', 'Admin', 'default_hash', 1)
        """)
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return user_id
    
    def download_image(self, image_url, product_name):
        """Download image from URL and save locally"""
        try:
            # Create images folder if it doesn't exist
            os.makedirs(IMAGES_FOLDER, exist_ok=True)
            
            # Generate unique filename
            file_extension = '.jpg'
            parsed_url = urlparse(image_url)
            if parsed_url.path:
                original_ext = os.path.splitext(parsed_url.path)[1]
                if original_ext.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    file_extension = '.jpg'  # Standardize to jpg
            
            # Clean product name for filename
            clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')[:30]  # Limit length
            
            filename = f"{clean_name}_{uuid.uuid4().hex[:8]}{file_extension}"
            filepath = os.path.join(IMAGES_FOLDER, filename)
            
            # Download image
            response = self.session.get(image_url, timeout=15, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Return just the filename for database (Flask expects uploads/filename format)
            return filename
            
        except Exception as e:
            print(f"❌ Error downloading image from {image_url}: {e}")
            return None
    
    def fetch_products_from_fakestore(self):
        """Fetch products from FakeStore API"""
        try:
            response = self.session.get(API_SOURCES['fakestore']['url'], timeout=10)
            response.raise_for_status()
            products = response.json()
            
            formatted_products = []
            for product in products:
                formatted_products.append({
                    'name': product.get('title', 'Product'),
                    'price': float(product.get('price', 0)),
                    'description': product.get('description', 'No description'),
                    'image_url': product.get('image', ''),
                    'category': product.get('category', ''),
                    'source': 'fakestore'
                })
            
            return formatted_products
        except Exception as e:
            print(f"❌ Error fetching from FakeStore API: {e}")
            return []
    
    def fetch_products_from_dummyjson(self):
        """Fetch products from DummyJSON API"""
        try:
            response = self.session.get(f"{API_SOURCES['dummyjson']['url']}?limit=100", timeout=10)
            response.raise_for_status()
            data = response.json()
            products = data.get('products', [])
            
            formatted_products = []
            for product in products:
                # Use first image if available
                image_url = ''
                if product.get('images') and len(product['images']) > 0:
                    image_url = product['images'][0]
                elif product.get('thumbnail'):
                    image_url = product['thumbnail']
                
                formatted_products.append({
                    'name': product.get('title', 'Product'),
                    'price': float(product.get('price', 0)),
                    'description': product.get('description', 'No description'),
                    'image_url': image_url,
                    'category': product.get('category', ''),
                    'source': 'dummyjson'
                })
            
            return formatted_products
        except Exception as e:
            print(f"❌ Error fetching from DummyJSON API: {e}")
            return []
    
    def fetch_products_from_platzi(self):
        """Fetch products from Platzi Fake Store API"""
        try:
            response = self.session.get(f"{API_SOURCES['platzi']['url']}?offset=0&limit=100", timeout=10)
            response.raise_for_status()
            products = response.json()
            
            formatted_products = []
            for product in products:
                # Use first image if available
                image_url = ''
                if product.get('images') and len(product['images']) > 0:
                    image_url = product['images'][0]
                
                category_name = ''
                if product.get('category') and isinstance(product['category'], dict):
                    category_name = product['category'].get('name', '')
                
                formatted_products.append({
                    'name': product.get('title', 'Product'),
                    'price': float(product.get('price', 0)),
                    'description': product.get('description', 'No description'),
                    'image_url': image_url,
                    'category': category_name,
                    'source': 'platzi'
                })
            
            return formatted_products
        except Exception as e:
            print(f"❌ Error fetching from Platzi API: {e}")
            return []
    
    def fetch_all_products(self):
        """Fetch products from all available APIs"""
        all_products = []
        
        print("🔄 Fetching products from FakeStore API...")
        all_products.extend(self.fetch_products_from_fakestore())
        time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print("🔄 Fetching products from DummyJSON API...")
        all_products.extend(self.fetch_products_from_dummyjson())
        time.sleep(DELAY_BETWEEN_REQUESTS)
        
        print("🔄 Fetching products from Platzi API...")
        all_products.extend(self.fetch_products_from_platzi())
        
        print(f"✅ Total products fetched: {len(all_products)}")
        return all_products
    
    def map_product_to_category(self, product, db_categories):
        """Map API product to database category"""
        product_category = product['category'].lower()
        source = product['source']
        
        # Try direct mapping first
        for db_cat, api_cat in API_SOURCES[source]['categories'].items():
            if api_cat.lower() in product_category or product_category in api_cat.lower():
                if db_cat in db_categories:
                    return db_categories[db_cat]
        
        # Fallback mapping based on keywords
        category_keywords = {
            'Électronique': ['electronic', 'phone', 'smartphone', 'laptop', 'computer', 'tech'],
            'Vêtements': ['clothing', 'dress', 'shirt', 'clothes', 'fashion', 'apparel'],
            'Chaussures': ['shoe', 'footwear', 'sneaker', 'boot'],
            'Accessoires': ['jewelry', 'jewelery', 'bag', 'watch', 'accessory'],
            'Cosmétiques': ['beauty', 'skincare', 'cosmetic', 'makeup'],
            'Meubles': ['furniture', 'chair', 'table', 'home'],
            'Alimentation': ['food', 'grocery', 'groceries'],
            'Sport': ['sport', 'fitness', 'athletic'],
            'Automobile': ['automotive', 'car', 'vehicle'],
            'Informatique': ['laptop', 'computer', 'tech', 'software']
        }
        
        for db_cat, keywords in category_keywords.items():
            if db_cat in db_categories:
                for keyword in keywords:
                    if keyword in product_category:
                        return db_categories[db_cat]
        
        # Default to first available category
        return list(db_categories.values())[0] if db_categories else 1
    
    def product_exists(self, name, price):
        """Check if product already exists in database"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productId FROM products WHERE name = ? AND price = ?", (name, price))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    
    def add_product_to_db(self, product_data, category_id, maker_id, image_path):
        """Add product to database"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO products (name, price, description, image, stock, categoryId, maker)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product_data['name'][:255],  # Limit name length
                product_data['price'],
                product_data['description'][:1000],  # Limit description length
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
    
    def add_products_automatically(self, max_products=100):
        """Main function to add products automatically"""
        print("🚀 Starting automatic product addition...")
        print("=" * 60)
        
        # Get database categories and maker ID
        db_categories = self.get_categories()
        maker_id = self.get_default_maker_id()
        
        print(f"📂 Found {len(db_categories)} categories in database")
        print(f"👤 Using maker ID: {maker_id}")
        
        # Fetch products from APIs
        all_products = self.fetch_all_products()
        
        if not all_products:
            print("❌ No products fetched from APIs")
            return
        
        # Shuffle products for variety
        random.shuffle(all_products)
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        # Track products per category
        category_counts = {cat: 0 for cat in db_categories.keys()}
        
        print(f"\n🔄 Processing products (max: {max_products})...")
        print("-" * 60)
        
        for i, product in enumerate(all_products[:max_products * 2]):  # Process more to account for skips
            if added_count >= max_products:
                break
                
            try:
                # Skip if product already exists
                if self.product_exists(product['name'], product['price']):
                    skipped_count += 1
                    continue
                
                # Map to database category
                category_id = self.map_product_to_category(product, db_categories)
                category_name = next((name for name, id in db_categories.items() if id == category_id), 'Unknown')
                
                # Limit products per category
                if category_counts[category_name] >= MAX_PRODUCTS_PER_CATEGORY:
                    continue
                
                # Download image
                image_path = None
                if product['image_url']:
                    print(f"📥 Downloading image for: {product['name'][:30]}...")
                    image_path = self.download_image(product['image_url'], product['name'])
                
                # Add product to database
                product_id = self.add_product_to_db(product, category_id, maker_id, image_path)
                
                added_count += 1
                category_counts[category_name] += 1
                
                print(f"✅ Added: {product['name'][:40]} | ${product['price']} | {category_name} | {product['source']}")
                
                # Small delay to be respectful to APIs
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error adding product {product['name'][:30]}: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"✅ Products added: {added_count}")
        print(f"⏭️  Products skipped (duplicates): {skipped_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📂 Products per category:")
        for category, count in category_counts.items():
            if count > 0:
                print(f"   - {category}: {count}")
        
        print(f"\n🎉 Process completed! {added_count} products added to your store.")

def main():
    """Main function"""
    try:
        adder = ProductAutoAdder()
        
        # Ask user for number of products
        try:
            max_products = int(input("How many products do you want to add? (default: 50): ") or "50")
        except ValueError:
            max_products = 50
        
        print(f"\n🎯 Target: {max_products} products")
        
        # Confirm before starting
        confirm = input("Do you want to proceed? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Operation cancelled.")
            return
        
        # Start the process
        adder.add_products_automatically(max_products)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()