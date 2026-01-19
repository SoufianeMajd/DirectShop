// AJAX functionality for home page without full page reload
document.addEventListener('DOMContentLoaded', function() {
    const productsContainer = document.getElementById('products-container');
    const categoryLinks = document.querySelectorAll('.category-list a');
    const searchForm = document.querySelector('form[action*="request.path"]');
    const sortButtons = document.querySelectorAll('.sort-btn');
    
    let currentParams = {
        query: '',
        category_id: null,
        sorting: 'name_asc'
    };

    // Initialize current parameters from URL
    function initializeParams() {
        const urlParams = new URLSearchParams(window.location.search);
        currentParams.query = urlParams.get('query') || '';
        currentParams.category_id = urlParams.get('category_id') || null;
        currentParams.sorting = urlParams.get('sorting') || 'name_asc';
    }

    // Show loading indicator
    function showLoading() {
        if (productsContainer) {
            productsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Chargement...</span>
                    </div>
                    <p class="mt-2 text-muted">Chargement des produits...</p>
                </div>
            `;
        }
    }

    // Update products display
    function updateProducts(data) {
        if (!productsContainer) return;

        if (data.itemData && data.itemData.length > 0) {
            let html = '';
            data.itemData.forEach(group => {
                group.forEach(row => {
                    html += `
                        <div class="col">
                            <div class="card card-product h-100 shadow-sm">
                                <a href="/productDescription?productId=${row[0]}">
                                    <img src="/static/uploads/${row[4]}" 
                                         class="card-img-top" alt="${row[1]}">
                                </a>
                                <div class="card-body">
                                    <h6 class="card-title">${row[1]}</h6>
                                    <p class="fw-bold text-success">${row[2]} €</p>
                                    <p class="text-muted mb-0">Stock : ${row[5]}</p>
                                </div>
                            </div>
                        </div>
                    `;
                });
            });
            productsContainer.innerHTML = html;
        } else {
            productsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">Aucun produit trouvé.</div>
                </div>
            `;
        }
    }

    // Fetch products via AJAX
    function fetchProducts() {
        showLoading();
        
        const params = new URLSearchParams();
        if (currentParams.query) params.append('query', currentParams.query);
        if (currentParams.category_id) params.append('category_id', currentParams.category_id);
        if (currentParams.sorting) params.append('sorting', currentParams.sorting);

        // Construire l'URL avec le tri si nécessaire
        let url = '/';
        if (currentParams.sorting && currentParams.sorting !== 'name_asc') {
            url = `/${currentParams.sorting}`;
        }
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                updateProducts(data);
                updateActiveStates();
            })
            .catch(error => {
                console.error('Error fetching products:', error);
                productsContainer.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-danger">Erreur lors du chargement des produits.</div>
                    </div>
                `;
            });
    }

    // Update active states for categories and sorting
    function updateActiveStates() {
        // Update category active states
        categoryLinks.forEach(link => {
            link.classList.remove('active');
            const categoryId = link.getAttribute('href').includes('category_id=') ? 
                link.getAttribute('href').split('category_id=')[1].split('&')[0] : null;
            
            if ((!currentParams.category_id && !categoryId) || 
                (currentParams.category_id && categoryId == currentParams.category_id)) {
                link.classList.add('active');
            }
        });

        // Update sorting active states
        sortButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.sort === currentParams.sorting) {
                btn.classList.add('active');
            }
        });
    }

    // Handle category clicks
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = new URL(this.href);
            const categoryId = url.searchParams.get('category_id');
            
            currentParams.category_id = categoryId;
            currentParams.query = url.searchParams.get('query') || '';
            
            fetchProducts();
            
            // Update URL without reload
            const newUrl = new URL(window.location);
            if (categoryId) {
                newUrl.searchParams.set('category_id', categoryId);
            } else {
                newUrl.searchParams.delete('category_id');
            }
            if (currentParams.query) {
                newUrl.searchParams.set('query', currentParams.query);
            } else {
                newUrl.searchParams.delete('query');
            }
            history.pushState({}, '', newUrl);
        });
    });

    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const queryInput = this.querySelector('input[name="query"]');
            currentParams.query = queryInput.value.trim();
            
            fetchProducts();
            
            // Update URL without reload
            const newUrl = new URL(window.location);
            if (currentParams.query) {
                newUrl.searchParams.set('query', currentParams.query);
            } else {
                newUrl.searchParams.delete('query');
            }
            history.pushState({}, '', newUrl);
        });
    }

    // Handle sorting buttons
    sortButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            currentParams.sorting = this.dataset.sort;
            fetchProducts();
            
            // Update URL without reload
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('sorting', currentParams.sorting);
            history.pushState({}, '', newUrl);
        });
    });

    // Initialize
    initializeParams();
    
    // Only fetch if we're on the home page and have a products container
    if (productsContainer && window.location.pathname === '/') {
        fetchProducts();
    }
});
