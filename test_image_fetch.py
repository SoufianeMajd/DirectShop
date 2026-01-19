#!/usr/bin/env python3
"""
Script de test pour vérifier que la récupération et téléchargement d'images depuis l'API e-commerce fonctionne correctement
"""

import requests
import random
import os

# Configuration pour l'API Fake Store (API e-commerce réaliste)
FAKE_STORE_API_URL = "https://fakestoreapi.com/products"

# Dossier de destination pour les images
UPLOAD_FOLDER = "static/uploads"

# Mapping des catégories locales vers les catégories de l'API Fake Store
CATEGORY_MAPPING = {
    'Électronique': 'electronics',
    'Vêtements': "women's clothing",
    'Jouets': 'jewelery',
    'Meubles': 'jewelery',
    'Livres': 'jewelery',
    'Chaussures': "men's clothing",
    'Accessoires': 'jewelery',
    'Cosmétiques': "women's clothing",
    'Sport': "men's clothing",
    'Alimentation': 'jewelery',
    'Bricolage': 'electronics',
    'Jardinage': 'electronics',
    'Informatique': 'electronics',
    'Automobile': 'electronics',
    'Musique': 'electronics',
    'Art': 'electronics',
    'Santé': 'electronics',
    'Bébés': 'electronics',
    'Papeterie': 'electronics',
    'Décoration': 'electronics'
}

def download_image(image_url, filename):
    """Télécharge une image depuis une URL et la sauvegarde localement"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Sauvegarder l'image
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return filename  # Retourner seulement le nom du fichier
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image {image_url}: {e}")
        return None

def fetch_products_from_api():
    """Récupère tous les produits depuis l'API Fake Store"""
    try:
        print("Récupération des produits depuis l'API Fake Store...")
        response = requests.get(FAKE_STORE_API_URL, timeout=10)
        response.raise_for_status()
        products = response.json()
        print(f"✅ {len(products)} produits récupérés depuis l'API")
        return products
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des produits: {e}")
        return []

def get_product_data(category_name):
    """Récupère les données d'un produit (nom, prix, description, image) depuis l'API Fake Store"""
    products = fetch_products_from_api()
    if not products:
        return None
    
    # Mapper la catégorie locale vers la catégorie de l'API
    api_category = CATEGORY_MAPPING.get(category_name, 'electronics')
    
    # Filtrer les produits par catégorie
    category_products = [p for p in products if p.get('category') == api_category]
    
    # Si pas de produits dans cette catégorie, prendre un produit aléatoire
    if not category_products:
        category_products = products
    
    # Choisir un produit aléatoire
    product = random.choice(category_products)
    
    return {
        'name': product.get('title', 'Produit'),
        'price': product.get('price', 0),
        'description': product.get('description', 'Description du produit'),
        'image_url': product.get('image', '')
    }

def test_image_fetching():
    """Teste la récupération et téléchargement d'images depuis l'API e-commerce"""
    test_categories = ['Électronique', 'Vêtements', 'Chaussures', 'Accessoires', 'Cosmétiques']
    
    print("Test de récupération et téléchargement d'images depuis l'API e-commerce...")
    print("=" * 70)
    
    # Test de l'API d'abord
    products = fetch_products_from_api()
    if not products:
        print("❌ Impossible de récupérer les produits depuis l'API")
        return
    
    print(f"✅ API fonctionnelle - {len(products)} produits disponibles")
    
    for i, category in enumerate(test_categories):
        print(f"\nTest pour la catégorie: {category}")
        
        # Récupérer les données du produit depuis l'API
        product_data = get_product_data(category)
        
        if product_data:
            print(f"✅ Produit trouvé: {product_data['name']}")
            print(f"   Prix: ${product_data['price']}")
            print(f"   Description: {product_data['description'][:50]}...")
            print(f"   URL image: {product_data['image_url']}")
            
            # Test du téléchargement
            filename = f"test_{i+1}_{category.lower().replace(' ', '_').replace('é', 'e')}.jpg"
            downloaded_file = download_image(product_data['image_url'], filename)
            
            if downloaded_file:
                print(f"✅ Image téléchargée avec succès: {downloaded_file}")
                
                # Vérifier que le fichier existe
                file_path = os.path.join(UPLOAD_FOLDER, downloaded_file)
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"✅ Fichier créé: {file_size} bytes")
                else:
                    print("❌ Fichier non trouvé après téléchargement")
            else:
                print("❌ Échec du téléchargement")
        else:
            print("❌ Aucun produit trouvé pour cette catégorie")
    
    print("\n" + "=" * 70)
    print("Test terminé!")
    
    # Afficher les fichiers téléchargés
    if os.path.exists(UPLOAD_FOLDER):
        files = os.listdir(UPLOAD_FOLDER)
        print(f"\nFichiers dans {UPLOAD_FOLDER}: {len(files)} fichiers")
        for file in files[:5]:  # Afficher les 5 premiers
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... et {len(files) - 5} autres fichiers")

if __name__ == "__main__":
    test_image_fetching()
