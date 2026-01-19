#!/usr/bin/env python3
"""
Script to fix image paths for products added with the old scripts
Moves images from static/product_images to static/uploads and updates database
"""

import sqlite3
import os
import shutil

def fix_image_paths():
    """Fix image paths in database and move files"""
    print("🔧 Fixing image paths for Flask compatibility...")
    print("=" * 50)
    
    # Check if old folder exists
    old_folder = 'static/product_images'
    new_folder = 'static/uploads'
    
    if not os.path.exists(old_folder):
        print("✅ No old product_images folder found. Nothing to fix.")
        return
    
    # Create new folder if it doesn't exist
    os.makedirs(new_folder, exist_ok=True)
    
    # Get database connection
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Find products with old image paths
    cur.execute("SELECT productId, name, image FROM products WHERE image LIKE 'static/product_images/%'")
    products_to_fix = cur.fetchall()
    
    if not products_to_fix:
        print("✅ No products with old image paths found.")
        conn.close()
        return
    
    print(f"📦 Found {len(products_to_fix)} products with old image paths")
    
    moved_count = 0
    updated_count = 0
    error_count = 0
    
    for product_id, name, old_image_path in products_to_fix:
        try:
            # Extract filename from old path
            filename = os.path.basename(old_image_path)
            old_file_path = old_image_path
            new_file_path = os.path.join(new_folder, filename)
            
            # Move file if it exists
            if os.path.exists(old_file_path):
                shutil.move(old_file_path, new_file_path)
                moved_count += 1
                print(f"📁 Moved: {filename}")
            
            # Update database with just the filename
            cur.execute("UPDATE products SET image = ? WHERE productId = ?", (filename, product_id))
            updated_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"❌ Error fixing {name}: {e}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    # Try to remove old folder if empty
    try:
        if os.path.exists(old_folder) and not os.listdir(old_folder):
            os.rmdir(old_folder)
            print(f"🗑️  Removed empty folder: {old_folder}")
    except:
        pass
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"📁 Files moved: {moved_count}")
    print(f"📝 Database records updated: {updated_count}")
    print(f"❌ Errors: {error_count}")
    
    if updated_count > 0:
        print(f"\n✅ Fixed! Product images should now display correctly on your website.")
    else:
        print(f"\n✅ No fixes needed.")

def main():
    """Main function"""
    print("🛠️  Image Path Fixer")
    print("This will fix image paths for products added with old scripts")
    print()
    
    try:
        # Check if database exists
        if not os.path.exists('database.db'):
            print("❌ Database not found. Make sure you're in the correct directory.")
            return
        
        # Confirm
        confirm = input("Fix image paths? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Cancelled")
            return
        
        # Start fixing
        fix_image_paths()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()