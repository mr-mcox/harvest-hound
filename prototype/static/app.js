// Harvest Hound Prototype - Frontend Logic
// No frameworks, just vanilla JS for rapid iteration

let currentStoreId = null;
let eventSource = null;

// Store type change handler
document.getElementById('storeType').addEventListener('change', (e) => {
    const defField = document.getElementById('storeDefinition');
    if (e.target.value === 'definition') {
        defField.style.display = 'block';
    } else {
        defField.style.display = 'none';
    }
});

// Load stores on page load
window.addEventListener('load', () => {
    loadStores();
});

async function loadStores() {
    try {
        const response = await fetch('/stores');
        const stores = await response.json();
        
        const storesList = document.getElementById('storesList');
        storesList.innerHTML = '';
        
        stores.forEach(store => {
            const storeDiv = document.createElement('div');
            storeDiv.className = 'store-item';
            storeDiv.innerHTML = `
                <strong>${store.name}</strong> (${store.type})
                <br><small>${store.description || 'No description'}</small>
            `;
            storeDiv.onclick = () => selectStore(store.id);
            storesList.appendChild(storeDiv);
        });
    } catch (error) {
        updateStatus('Failed to load stores: ' + error.message, 'error');
    }
}

async function createStore() {
    const name = document.getElementById('storeName').value;
    const storeType = document.getElementById('storeType').value;
    const definition = document.getElementById('storeDefinition').value;
    
    if (!name) {
        alert('Please enter a store name');
        return;
    }
    
    try {
        const response = await fetch('/stores', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: name,
                store_type: storeType,
                definition: storeType === 'definition' ? definition : null
            })
        });
        
        if (response.ok) {
            updateStatus('Store created successfully!', 'success');
            document.getElementById('storeName').value = '';
            document.getElementById('storeDefinition').value = '';
            loadStores();
        }
    } catch (error) {
        updateStatus('Failed to create store: ' + error.message, 'error');
    }
}

async function selectStore(storeId) {
    currentStoreId = storeId;
    document.getElementById('inventorySection').style.display = 'block';
    
    // Highlight selected store
    document.querySelectorAll('.store-item').forEach(item => {
        item.style.background = '#f8f8f8';
    });
    event.currentTarget.style.background = '#e0f2e0';
    
    // Load inventory
    await loadInventory();
}

async function loadInventory() {
    if (!currentStoreId) return;
    
    try {
        const response = await fetch(`/stores/${currentStoreId}/inventory`);
        const items = await response.json();
        
        const inventoryList = document.getElementById('inventoryList');
        if (items.length === 0) {
            inventoryList.innerHTML = '<p>No inventory items yet</p>';
        } else {
            inventoryList.innerHTML = items.map(item => `
                <div style="padding: 5px; margin: 2px 0; background: #f8f8f8;">
                    ${item.quantity} ${item.unit} ${item.ingredient}
                </div>
            `).join('');
        }
    } catch (error) {
        updateStatus('Failed to load inventory: ' + error.message, 'error');
    }
}

async function addInventory() {
    if (!currentStoreId) {
        alert('Please select a store first');
        return;
    }
    
    const ingredient = document.getElementById('ingredientName').value;
    const quantity = parseFloat(document.getElementById('quantity').value);
    const unit = document.getElementById('unit').value;
    
    if (!ingredient || !quantity || !unit) {
        alert('Please fill all fields');
        return;
    }
    
    try {
        const response = await fetch(`/stores/${currentStoreId}/inventory`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ingredient_name: ingredient,
                quantity: quantity,
                unit: unit
            })
        });
        
        if (response.ok) {
            updateStatus('Inventory added!', 'success');
            document.getElementById('ingredientName').value = '';
            document.getElementById('quantity').value = '';
            document.getElementById('unit').value = '';
            loadInventory();
        }
    } catch (error) {
        updateStatus('Failed to add inventory: ' + error.message, 'error');
    }
}

async function generateRecipes() {
    const additionalContext = document.getElementById('additionalContext').value;

    // Clear previous recipes
    const recipesList = document.getElementById('recipesList');
    recipesList.innerHTML = '<div class="recipe-card streaming">Generating recipes...</div>';

    // Close previous SSE connection if exists
    if (eventSource) {
        eventSource.close();
    }

    // Create SSE connection with GET params
    const params = new URLSearchParams({
        additional_context: additionalContext || "",
        num_recipes: 3
    });
    eventSource = new EventSource('/generate-recipes?' + params);

    let recipesReceived = [];

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Handle completion
        if (data.complete) {
            updateStatus('Recipe generation complete!', 'success');
            eventSource.close();
            return;
        }

        // Handle errors
        if (data.error) {
            updateStatus('Error: ' + data.message, 'error');
            eventSource.close();
            recipesList.innerHTML = '<p>Failed to generate recipes. Try again.</p>';
            return;
        }

        // Handle recipe data
        if (data.recipe) {
            recipesReceived.push(data.recipe);

            // Update UI with streaming effect
            recipesList.innerHTML = recipesReceived.map((recipe, i) => `
                <div class="recipe-card ${i === recipesReceived.length - 1 ? 'streaming' : ''}">
                    <h4>${recipe.name}</h4>
                    <p><strong>Ingredients:</strong><br>${recipe.ingredients.join('<br>')}</p>
                    <p><strong>Instructions:</strong><br>${recipe.instructions.replace(/\n/g, '<br>')}</p>
                    <p><strong>Time:</strong> ${recipe.active_time} min active${recipe.passive_time ? ' + ' + recipe.passive_time + ' min passive' : ''}</p>
                    <p><strong>Servings:</strong> ${recipe.servings}</p>
                    ${recipe.notes ? `<p><strong>Notes:</strong> ${recipe.notes}</p>` : ''}
                    <button onclick="acceptRecipe('${recipe.name}')">Accept Recipe</button>
                    <button onclick="claimIngredients('${recipe.name}')">Claim Ingredients</button>
                </div>
            `).join('');
        }
    };

    eventSource.onerror = (error) => {
        updateStatus('Connection error generating recipes', 'error');
        eventSource.close();
        recipesList.innerHTML = '<p>Failed to generate recipes. Check console for details.</p>';
        console.error('SSE Error:', error);
    };
}

async function acceptRecipe(recipeName) {
    updateStatus(`Accepted recipe: ${recipeName}`, 'success');
    // TODO: Add to meal plan
}

async function claimIngredients(recipeName) {
    // TODO: Implement claiming logic
    const response = await fetch(`/claim-ingredients/test-recipe-id`, {
        method: 'POST'
    });
    
    const result = await response.json();
    
    if (result.success) {
        updateStatus(`Claimed: ${result.claimed.join(', ')}. Missing: ${result.missing.join(', ')}`, 'info');
    }
}

function updateStatus(message, type = 'info') {
    const status = document.getElementById('status');
    status.textContent = message;
    
    // Style based on type
    const colors = {
        success: '#e8f5e9',
        error: '#ffebee',
        info: '#e3f2fd'
    };
    
    status.style.background = colors[type] || colors.info;
    
    // Auto-clear after 5 seconds
    setTimeout(() => {
        status.textContent = 'Ready...';
        status.style.background = '#e8f5e9';
    }, 5000);
}