from flask import Blueprint, jsonify, request, session  # session added for auth
from flask import Flask
import sqlite3
import os
import bcrypt
import jwt
import re
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS


api_bp = Blueprint('api', __name__)
app = Flask(__name__)
app.secret_key = 'ef4072ab74fab1912276e53ff09198eb82ed8f0a4f470dfd60d68bb1a596ee12'  # import secrets; print(secrets.token_hex(x))
CORS(app, expose_headers='Authorization')

# JWT Configuration
SECRET_KEY = 'ef4072ab74fab1912276e53ff09198eb82ed8f0a4f470dfd60d68bb1a596ee12'  # Use the same as app.secret_key
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_SECONDS = 1800 #0 Token validity in seconds (e.g., 1800 for 30 minutes)

# SQL Injection Protection Functions
def sanitize_input(input_string):
    """
    Sanitize input to prevent SQL injection attacks.
    This is an additional layer of protection alongside parameterized queries.
    """
    if not isinstance(input_string, str):
        return input_string
    
    # Remove or escape potentially dangerous characters
    dangerous_patterns = [
        r"[';\"\\]",  # Single quotes, double quotes, backslashes
        r"--",        # SQL comments
        r"/\*.*?\*/", # Multi-line comments
        r"\bUNION\b", r"\bSELECT\b", r"\bINSERT\b", r"\bUPDATE\b", 
        r"\bDELETE\b", r"\bDROP\b", r"\bCREATE\b", r"\bALTER\b",
        r"\bEXEC\b", r"\bEXECUTE\b"
    ]
    
    sanitized = input_string
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_field_name(field_name):
    """
    Validate that field names are safe for dynamic query building.
    Only allow alphanumeric characters and underscores.
    """
    if not isinstance(field_name, str):
        return False
    
    # Only allow alphanumeric characters and underscores
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', field_name))

def validate_email(email):
    """
    Validate email format to prevent injection through email field.
    """
    if not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_numeric_input(value, min_val=None, max_val=None):
    """
    Validate numeric inputs to prevent injection and ensure data integrity.
    """
    try:
        num_value = float(value)
        if min_val is not None and num_value < min_val:
            return False
        if max_val is not None and num_value > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

# JWT Helper Functions
def generate_access_token(user_id, email, user_type):
    payload = {
        'user_id': user_id,
        'email': email,
        'type': user_type,
        'exp': datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Accept both "Authorization: Bearer <token>" and raw token in the Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = ''
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        else:
            token = auth_header.strip()

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        payload = decode_access_token(token)
        if isinstance(payload, dict) and payload.get('error'):
            return jsonify({'error': payload['error']}), 401

        # Optionally, attach payload to request context for use in views
        # from flask import g
        # g.jwt_payload = payload

        return f(*args, **kwargs)
    return decorated

# Helper function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# api_get_products
@api_bp.route('/api/products', methods=['GET'])
@token_required  # <-- Requires a valid token
def api_get_products():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(products)

@api_bp.route('/api/orders', methods=['GET'])
@token_required  # <-- Requires a valid token
def api_get_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    orders = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(orders)

@api_bp.route('/api/users', methods=['GET'])
@token_required  # <-- Requires a valid token
def api_get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(users)

@api_bp.route('/api/categories', methods=['GET'])
@token_required  # <-- Requires a valid token
def api_get_categories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT categoryId, name FROM categories")
    categories = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(categories)

# DELETE endpoints
@api_bp.route('/api/deleteOrder/<int:orderId>', methods=['DELETE'])
@token_required  # <-- Requires a valid token
def api_delete_order(orderId):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE orderId = ?", (orderId,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'deleted_id': orderId})

@api_bp.route('/api/deleteUser/<int:userId>', methods=['DELETE'])
@token_required  # <-- Requires a valid token
def api_delete_user(userId):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE userId = ?", (userId,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'deleted_id': userId})

@api_bp.route('/api/deleteProduct/<int:product_id>', methods=['DELETE'])
@token_required  # <-- Requires a valid token
def delete_product(product_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Check if product exists
    cur.execute("SELECT productId FROM products WHERE productId = ?", (product_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    # Delete product
    cur.execute("DELETE FROM products WHERE productId = ?", (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'deleted_id': product_id})

# LOGIN API - Now using secure bcrypt password verification with input validation
@api_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format'}), 400

    # Sanitize inputs (additional protection)
    email = sanitize_input(email)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT userId, email, password, type FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = generate_access_token(user['userId'], user['email'], user['type'])
        return jsonify({
            'success': True,
            'userId': user['userId'],
            'email': user['email'],
            'type': user['type'],
            'access_token': token
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

# SIGNUP API - Now using secure bcrypt password hashing with input validation
@api_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    required_fields = ['email', 'password', 'firstName', 'lastName']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    email = data['email']
    firstName = data['firstName']
    lastName = data['lastName']
    
    # Validate email format
    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format'}), 400
    
    # Sanitize inputs (additional protection)
    email = sanitize_input(email)
    firstName = sanitize_input(firstName)
    lastName = sanitize_input(lastName)
    
    # Hash password with bcrypt for security
    password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_type = 'admin'
    acceptation = 1

    # Default empty for optional fields
    address1 = address2 = zipcode = city = state = country = phone = ''

    conn = get_db_connection()
    cur = conn.cursor()
    # Check if email already exists
    cur.execute('SELECT userId FROM users WHERE email = ?', (email,))
    if cur.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Email already registered'}), 409

    cur.execute('''
        INSERT INTO users (
            type, password, email, firstName, lastName,
            address1, address2, zipcode, city, state, country,
            phone, acceptation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_type, password, email, firstName, lastName,
        address1, address2, zipcode, city, state, country,
        phone, acceptation
    ))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return jsonify({'success': True, 'userId': user_id, 'email': email, 'type': user_type})

# Upload Product Image API
@api_bp.route('/api/uploadProductImage/<int:productId>', methods=['POST'])
@token_required  # <-- Requires a valid token
def upload_product_image(productId):
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    # Sanitize filename to prevent path traversal attacks
    filename = sanitize_input(file.filename)
    filename = f'product_{productId}_{filename}'
    
    # Save image to static/product_images/
    upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'product_images')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # Save relative path in DB
    image_path = f'static/product_images/{filename}'
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE products SET image = ? WHERE productId = ?", (image_path, productId))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'image_path': image_path})

# Add Product API with input validation
@api_bp.route('/api/addProduct', methods=['POST'])
@token_required  # <-- Requires a valid token
def api_add_product():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    required_fields = ['name', 'price', 'description', 'stock', 'categoryId']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate numeric inputs
    if not validate_numeric_input(data['price'], min_val=0):
        return jsonify({"error": "Invalid price value"}), 400
    
    if not validate_numeric_input(data['stock'], min_val=0):
        return jsonify({"error": "Invalid stock value"}), 400
    
    if not validate_numeric_input(data['categoryId'], min_val=1):
        return jsonify({"error": "Invalid category ID"}), 400

    try:
        # Sanitize string inputs
        name = sanitize_input(data['name'])
        description = sanitize_input(data['description'])
        image_url = sanitize_input(data.get('image', 'default_product.png'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # For now, using a placeholder or make maker optional
        maker_id = data.get('maker', 1)

        cursor.execute('''INSERT INTO products 
                         (name, price, description, image, stock, categoryId, maker)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (name, data['price'], description,
                      image_url, data['stock'], data['categoryId'], maker_id))

        product_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Product added successfully",
            "productId": product_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Edit Product API with secure dynamic query building
@api_bp.route('/api/editProduct/<int:productId>', methods=['PUT'])
@token_required  # <-- Requires a valid token
def api_edit_product(productId):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM products WHERE productId = ?', (productId,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return jsonify({"error": "Product not found"}), 404

        # Define allowed fields for security
        allowed_fields = {'name', 'price', 'description', 'stock', 'categoryId', 'image'}
        update_fields = []
        update_values = []

        for field, value in data.items():
            if field in allowed_fields and value is not None:
                # Validate field name for security
                if not validate_field_name(field):
                    conn.close()
                    return jsonify({"error": f"Invalid field name: {field}"}), 400
                
                # Validate numeric fields
                if field in ['price', 'stock', 'categoryId']:
                    if not validate_numeric_input(value, min_val=0):
                        conn.close()
                        return jsonify({"error": f"Invalid {field} value"}), 400
                
                # Sanitize string fields
                if field in ['name', 'description', 'image']:
                    value = sanitize_input(str(value))
                
                update_fields.append(f"{field} = ?")
                update_values.append(value)

        if not update_fields:
            conn.close()
            return jsonify({"error": "No valid fields to update"}), 400

        # Build secure query with validated field names
        update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE productId = ?"
        update_values.append(productId)

        cursor.execute(update_query, update_values)
        conn.commit()

        # Get updated product
        cursor.execute('SELECT * FROM products WHERE productId = ?', (productId,))
        updated_product = cursor.fetchone()

        product_dict = dict(updated_product) if updated_product else None
        conn.close()

        if not product_dict:
            return jsonify({"error": "Product not found after update"}), 500

        return jsonify({
            "message": "Product updated successfully",
            "product": product_dict
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# REMOVED: Invalid main block for Blueprint
# Blueprints don't have app.run() - that belongs in your main app file