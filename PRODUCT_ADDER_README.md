# Automatic Product Adder

This tool automatically adds products with relevant images to your e-commerce database from external APIs.

## 🚀 Quick Start

### Option 1: Use the Batch File (Windows)
1. Double-click `run_product_adder.bat`
2. Choose between Simple (recommended) or Advanced version
3. Follow the prompts

### Option 2: Manual Installation
1. Install requirements:
   ```bash
   pip install -r requirements_products.txt
   ```

2. Run the simple version:
   ```bash
   python simple_product_adder.py
   ```

3. Or run the advanced version:
   ```bash
   python auto_add_products.py
   ```

4. If you have issues with images not showing, run the fix script:
   ```bash
   python fix_image_paths.py
   ```

## 📋 Available Scripts

### 1. Simple Product Adder (`simple_product_adder.py`)
**Recommended for beginners**

- ✅ Uses reliable FakeStore API
- ✅ Adds up to 20 products
- ✅ Automatic image download
- ✅ Category mapping
- ✅ Duplicate detection
- ✅ Easy to use

**Features:**
- Fetches products from https://fakestoreapi.com
- Downloads product images automatically
- Maps API categories to your database categories
- Prevents duplicate products
- Adds random stock quantities (10-100)

### 2. Advanced Product Adder (`auto_add_products.py`)
**For advanced users who want more products**

- ✅ Multiple API sources (FakeStore, DummyJSON, Platzi)
- ✅ Up to 100+ products
- ✅ Better category distribution
- ✅ More product variety
- ✅ Advanced error handling
- ✅ Detailed progress reporting

**API Sources:**
- **FakeStore API**: Electronics, clothing, jewelry
- **DummyJSON**: Smartphones, laptops, skincare, furniture
- **Platzi Fake Store**: Electronics, clothes, shoes, furniture

## 🗂️ Category Mapping

The scripts automatically map API categories to your database categories:

| Database Category | API Categories |
|------------------|----------------|
| Électronique | electronics, smartphones, laptops |
| Vêtements | men's clothing, women's clothing, clothes |
| Chaussures | shoes, footwear |
| Accessoires | jewelery, bags, watches |
| Cosmétiques | skincare, beauty, makeup |
| Meubles | furniture |
| Alimentation | groceries, food |
| Sport | sports accessories |
| Automobile | automotive |
| Informatique | laptops, computers |

## 📁 File Structure

After running the scripts, you'll have:

```
PROJECT/
├── database.db (updated with new products)
├── static/
│   └── uploads/
│       ├── Product_Name_12345678.jpg
│       ├── Another_Product_87654321.jpg
│       └── ...
├── simple_product_adder.py
├── auto_add_products.py
├── fix_image_paths.py
├── run_product_adder.bat
└── requirements_products.txt
```

## 🛡️ Security Features

- ✅ **SQL Injection Protection**: Uses parameterized queries
- ✅ **Input Validation**: Validates all product data
- ✅ **File Security**: Sanitizes image filenames
- ✅ **Duplicate Prevention**: Checks existing products
- ✅ **Error Handling**: Graceful error recovery

## ⚙️ Configuration

### Simple Product Adder Settings
```python
DATABASE_PATH = 'database.db'
IMAGES_FOLDER = 'static/product_images'
API_URL = 'https://fakestoreapi.com/products'
```

### Advanced Product Adder Settings
```python
MAX_PRODUCTS_PER_CATEGORY = 5  # Limit per category
DELAY_BETWEEN_REQUESTS = 0.5   # Seconds between API calls
```

## 🔧 Customization

### Adding New API Sources
To add a new API source to the advanced script:

1. Add API configuration to `API_SOURCES`:
```python
'your_api': {
    'url': 'https://your-api.com/products',
    'category_field': 'category',
    'categories': {
        'Électronique': 'electronics',
        # ... more mappings
    }
}
```

2. Create a fetch function:
```python
def fetch_products_from_your_api(self):
    # Implementation here
    pass
```

3. Add to `fetch_all_products()` method

### Modifying Categories
Edit the `CATEGORY_MAPPING` dictionary to change how API categories map to your database categories.

## 📊 What Gets Added

Each product includes:
- **Name**: Product title from API
- **Price**: Original price from API
- **Description**: Full product description
- **Image**: Downloaded and stored locally
- **Stock**: Random quantity (10-100)
- **Category**: Mapped to your database categories
- **Maker**: Default admin user

## 🚨 Troubleshooting

### Common Issues

**"No products fetched from APIs"**
- Check internet connection
- APIs might be temporarily down
- Try the simple version first

**"Error downloading image"**
- Some image URLs might be invalid
- Script continues with default image
- Check `static/product_images/` folder permissions

**"Database error"**
- Ensure `database.db` exists
- Run `python database.py` first
- Check database permissions

**"Duplicate products"**
- Script automatically skips duplicates
- Based on name and price matching
- This is normal behavior

### Debug Mode
Add this to see more details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

### Simple Script
- ~20 products in 1-2 minutes
- ~1-5 MB of images downloaded
- Minimal API requests

### Advanced Script
- ~100 products in 5-10 minutes
- ~10-50 MB of images downloaded
- Multiple API sources

## 🔄 Updates

To update the scripts:
1. Download latest versions
2. Check for new API sources
3. Update category mappings if needed
4. Test with small batches first

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify internet connection
3. Ensure database exists and is accessible
4. Try the simple version first
5. Check file permissions for image folder

## 🎯 Best Practices

1. **Start Small**: Use simple script first
2. **Test Database**: Backup before running
3. **Check Images**: Verify image folder permissions
4. **Monitor Progress**: Watch console output
5. **Regular Updates**: Keep scripts updated

## 📝 Example Usage

### Simple Script Example
```bash
$ python simple_product_adder.py
🛍️  Simple Product Adder
How many products to add? (default: 20): 10
Add 10 products? (y/N): y

🚀 Starting simple product addition...
🔄 Fetching products from FakeStore API...
✅ Fetched 20 products
📥 Downloading image for: Fjallraven - Foldsack No. 1...
✅ Added: Fjallraven - Foldsack No. 1 Backpack | $109.95 | Accessoires

📊 SUMMARY
✅ Products added: 10
⏭️  Products skipped: 0
❌ Errors: 0
🎉 Done! 10 products added to your store.
```

This tool makes it easy to populate your e-commerce store with realistic products and images!