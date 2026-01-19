# DirectShop

DirectShop is an e-commerce platform that connects buyers and sellers. It features product management, shopping cart functionality, order processing, and user reviews.

![DirectShop Screenshot](static/images/screenshot.png)

## Class Diagram

```mermaid
erDiagram
    USERS {
        int userId PK
        string type
        string password
        string email
        string firstName
        string lastName
        string address1
        string address2
        string zipcode
        string city
        string state
        string country
        string phone
        string avatar
        string IP
        int acceptation
        string vendor_cert_path
        string cin_path
        string photo_path
    }
    CATEGORIES {
        int categoryId PK
        string name
    }
    PRODUCTS {
        int productId PK
        string name
        real price
        string description
        string image
        int stock
        int categoryId FK
        int maker FK
    }
    KART {
        int userId FK
        int productId FK
    }
    ORDERS {
        int orderId PK
        int userId FK
        string orderDate
        real total
    }
    ORDER_ITEMS {
        int id PK
        int orderId FK
        int productId FK
        int quantity
    }
    AVIS {
        int avisId PK
        int userId FK
        int productId FK
        string commentaire
        int note
        string date
    }
    RATING_SELLERS {
        int ratingSellerId PK
        int sellerId FK
        int raterId FK
        string commentaire
        int rating
        string date
    }
    PRODUCT_MEDIA {
        int mediaId PK
        int productId FK
        string url
        string mediaType
    }
    PRODUCT_TYPES {
        int productId PK
        string type
        string livraisonType
        real fraisLivraison
    }
    PRODUITS_DETAILS {
        int detailId PK
        int productId FK
        string cle
        string valeur
    }
    CATEGORY_ATTRIBUTES {
        int attrId PK
        int categoryId FK
        string cle
    }
    PRODUCT_CATEGORY_ATTRIBUTES {
        int productId FK
        int attrId FK
        string valeur
    }
    MESSAGES {
        int id PK
        string sender
        string receiver
        string content
        string file_path
        string file_type
        datetime timestamp
    }

    USERS ||--o{ PRODUCTS : "makes (seller)"
    USERS ||--o{ ORDERS : "places"
    USERS ||--o{ KART : "has items in"
    USERS ||--o{ AVIS : "posts"
    USERS ||--o{ RATING_SELLERS : "is rated (seller)"
    USERS ||--o{ RATING_SELLERS : "rates (buyer)"

    CATEGORIES ||--o{ PRODUCTS : "contains"
    CATEGORIES ||--o{ CATEGORY_ATTRIBUTES : "defines"

    PRODUCTS ||--o{ KART : "is in"
    PRODUCTS ||--o{ ORDER_ITEMS : "is in"
    PRODUCTS ||--o{ AVIS : "has"
    PRODUCTS ||--o{ PRODUCT_MEDIA : "has"
    PRODUCTS ||--|{ PRODUCT_TYPES : "has type"
    PRODUCTS ||--o{ PRODUITS_DETAILS : "has details"
    PRODUCTS ||--o{ PRODUCT_CATEGORY_ATTRIBUTES : "has attributes"

    ORDERS ||--|{ ORDER_ITEMS : "contains"
    
    CATEGORY_ATTRIBUTES ||--o{ PRODUCT_CATEGORY_ATTRIBUTES : "defines values for"
```

## Running the Application

### Prequisites
- Python 3.x
- Flask
- SQLite3

### Installation

1. Install dependencies:
   ```bash
   pip install flask flask-cors
   ```

2. Run the application:
   ```bash
   python main.py
   ```

The application will start on `http://localhost:5000`.
