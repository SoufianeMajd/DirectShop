#!/usr/bin/env python3
"""
Script de test pour vérifier que l'API AJAX fonctionne correctement
"""

import requests
import json

def test_ajax_endpoints():
    """Teste les différents endpoints AJAX avec routes simples"""
    base_url = "http://localhost:5000"
    ajax_headers = {'X-Requested-With': 'XMLHttpRequest'}
    
    print("Test des routes AJAX pour les produits...")
    print("=" * 50)
    
    # Test 1: Récupérer tous les produits
    print("\n1. Test récupération de tous les produits:")
    try:
        response = requests.get(f"{base_url}/", headers=ajax_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès - {data['totalProducts']} produits récupérés")
            print(f"   Nombre de groupes: {len(data['itemData'])}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 2: Recherche par nom
    print("\n2. Test recherche par nom:")
    try:
        response = requests.get(f"{base_url}/?query=produit", headers=ajax_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès - {data['totalProducts']} produits trouvés pour 'produit'")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Filtrage par catégorie
    print("\n3. Test filtrage par catégorie:")
    try:
        response = requests.get(f"{base_url}/?category_id=1", headers=ajax_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès - {data['totalProducts']} produits dans la catégorie 1")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Tri par prix
    print("\n4. Test tri par prix croissant:")
    try:
        response = requests.get(f"{base_url}/price_asc", headers=ajax_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès - {data['totalProducts']} produits triés par prix croissant")
            if data['itemData'] and data['itemData'][0]:
                first_product = data['itemData'][0][0]
                print(f"   Premier produit: {first_product[1]} - {first_product[2]}€")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 5: Combinaison de filtres
    print("\n5. Test combinaison de filtres:")
    try:
        response = requests.get(f"{base_url}/price_desc?query=produit&category_id=1", headers=ajax_headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès - {data['totalProducts']} produits avec filtres combinés")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("Tests terminés!")

if __name__ == "__main__":
    test_ajax_endpoints()
