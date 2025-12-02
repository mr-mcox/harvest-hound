// Harvest Hound Prototype - Frontend Logic
// No frameworks, just vanilla JS for rapid iteration

let currentStoreId = null;
let eventSource = null;
let selectedPitches = new Set();
let pitchesData = [];
let currentInventory = null;  // Track inventory state across flesh-outs
let invalidPitches = new Set();  // Track pitches that can't be made anymore

// Store type change handler
document.getElementById('storeType').addEventListener('change', (e) => {
    const defField = document.getElementById('storeDefinition');
    if (e.target.value === 'definition') {
        defField.style.display = 'block';
    } else {
        defField.style.display = 'none';
    }
});

// Load stores and planned recipes on page load
window.addEventListener('load', () => {
    loadStores();
    loadPlannedRecipes();
    loadFlatInventory();
    loadShoppingList();
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

            // Build definition section if it's a definition-based store
            let definitionSection = '';
            if (store.type === 'definition') {
                definitionSection = `
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd;" onclick="event.stopPropagation()">
                        <textarea id="def-${store.id}" placeholder="Store definition..." style="width: 100%; height: 60px; font-size: 11px;">${store.definition || ''}</textarea>
                        <button onclick="updateStoreDefinition('${store.id}')">Update Definition</button>
                    </div>
                `;
            }

            storeDiv.innerHTML = `
                <div onclick="selectStore('${store.id}')">
                    <strong>${store.name}</strong> (${store.type})
                    <br><small>${store.description || 'No description'}</small>
                </div>
                ${definitionSection}
                <div onclick="event.stopPropagation()" style="margin-top: 5px;">
                    <button class="delete-btn" onclick="deleteStore('${store.id}')">Delete Store</button>
                </div>
            `;

            storesList.appendChild(storeDiv);
        });
    } catch (error) {
        updateStatus('Failed to load stores: ' + error.message, 'error');
    }
}

async function deleteStore(storeId) {
    if (!confirm('Delete this store and all its inventory?')) return;

    try {
        const response = await fetch(`/stores/${storeId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            updateStatus('Store deleted', 'success');
            if (currentStoreId === storeId) {
                currentStoreId = null;
                document.getElementById('inventorySection').style.display = 'none';
            }
            loadStores();
        }
    } catch (error) {
        updateStatus('Failed to delete store: ' + error.message, 'error');
    }
}

async function updateStoreDefinition(storeId) {
    const definition = document.getElementById(`def-${storeId}`).value;

    try {
        const response = await fetch(`/stores/${storeId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ definition: definition })
        });

        if (response.ok) {
            updateStatus('Store definition updated', 'success');
        }
    } catch (error) {
        updateStatus('Failed to update definition: ' + error.message, 'error');
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
        item.style.borderLeft = 'none';
    });

    // Find and highlight the clicked store
    const storeItems = document.querySelectorAll('.store-item');
    storeItems.forEach(item => {
        if (item.querySelector(`[onclick*="${storeId}"]`)) {
            item.style.background = '#e0f2e0';
            item.style.borderLeft = '4px solid #4CAF50';
        }
    });

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
                <div class="inventory-item">
                    <span>${item.quantity} ${item.unit} ${item.ingredient}</span>
                    <div>
                        <input type="number" id="qty-${item.id}" value="${item.quantity}" step="0.1" style="width: 60px; display: inline-block;">
                        <button onclick="updateQuantity('${item.id}')">Update</button>
                        <button class="delete-btn" onclick="deleteInventoryItem('${item.id}')">Delete</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        updateStatus('Failed to load inventory: ' + error.message, 'error');
    }
}

async function addBulkInventory() {
    const freeText = document.getElementById('bulkIngredients').value;

    if (!freeText) {
        alert('Please enter some ingredients');
        return;
    }

    // Get or create a default store for adding ingredients
    let storeId = currentStoreId;

    if (!storeId) {
        // Try to find an existing explicit store
        const storesResponse = await fetch('/stores');
        const stores = await storesResponse.json();
        const explicitStore = stores.find(s => s.type === 'explicit');

        if (explicitStore) {
            storeId = explicitStore.id;
        } else {
            // Create a default "My Inventory" store
            const createResponse = await fetch('/stores', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: 'My Inventory',
                    store_type: 'explicit',
                    description: 'Default inventory'
                })
            });
            const newStore = await createResponse.json();
            storeId = newStore.id;
            loadStores();  // Refresh store list
        }
    }

    try {
        updateStatus('Parsing ingredients...', 'info');
        const response = await fetch(`/stores/${storeId}/inventory/bulk`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ free_text: freeText })
        });

        const result = await response.json();

        if (result.success) {
            const parseResults = document.getElementById('parseResults');
            parseResults.style.display = 'block';

            let message = `Added ${result.total} items!`;
            if (result.skipped.length > 0) {
                message += `\n\nSkipped: ${result.skipped.join(', ')}`;
            }

            parseResults.innerHTML = `
                <strong>Parsed Successfully:</strong><br>
                ${result.added.join('<br>')}
                ${result.skipped.length > 0 ? `<br><br><strong>Skipped:</strong><br>${result.skipped.join('<br>')}` : ''}
                ${result.notes ? `<br><br><strong>Notes:</strong><br>${result.notes}` : ''}
            `;

            updateStatus(message, 'success');
            document.getElementById('bulkIngredients').value = '';
            loadInventory();
            loadFlatInventory();  // Refresh flat view
        } else {
            updateStatus('Failed to parse: ' + result.error, 'error');
        }
    } catch (error) {
        updateStatus('Failed to add bulk inventory: ' + error.message, 'error');
    }
}

async function deleteInventoryItem(itemId) {
    if (!confirm('Delete this item?')) return;

    try {
        const response = await fetch(`/inventory/${itemId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            updateStatus('Item deleted', 'success');
            loadInventory();
            loadFlatInventory();  // Refresh flat view
        }
    } catch (error) {
        updateStatus('Failed to delete: ' + error.message, 'error');
    }
}

async function updateQuantity(itemId) {
    const newQty = parseFloat(document.getElementById(`qty-${itemId}`).value);

    if (!newQty || newQty <= 0) {
        alert('Please enter a valid quantity');
        return;
    }

    try {
        const response = await fetch(`/inventory/${itemId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ quantity: newQty })
        });

        if (response.ok) {
            updateStatus('Quantity updated', 'success');
            loadInventory();
            loadFlatInventory();  // Refresh flat view
        }
    } catch (error) {
        updateStatus('Failed to update: ' + error.message, 'error');
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

async function generatePitches() {
    const additionalContext = document.getElementById('additionalContext').value;

    // Show pitch section
    document.getElementById('pitchSection').style.display = 'block';
    const pitchesList = document.getElementById('pitchesList');

    // Determine if this is first batch or adding more
    const isFirstBatch = pitchesData.length === 0;

    if (isFirstBatch) {
        // First batch: reset everything
        selectedPitches.clear();
        pitchesData = [];
        currentInventory = null;
        invalidPitches.clear();
        updateStatus('Generating pitches...', 'info');
        pitchesList.innerHTML = '<div style="padding: 20px; text-align: center;">Generating pitches...</div>';
    } else {
        // Adding more: keep existing pitches, append new ones
        updateStatus('Generating more pitches with updated inventory...', 'info');
        pitchesList.innerHTML += '<div style="padding: 20px; text-align: center; border-top: 2px solid #ccc;">Loading more...</div>';
    }

    // Close previous SSE connection if exists
    if (eventSource) {
        eventSource.close();
    }

    // Create SSE connection with GET params
    const params = new URLSearchParams({
        additional_context: additionalContext || "",
        num_pitches: 10,
        available_inventory_json: currentInventory ? JSON.stringify(currentInventory) : ""
    });
    eventSource = new EventSource('/generate-pitches?' + params);

    const startingIndex = pitchesData.length;  // Track where new pitches start

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Handle completion
        if (data.complete) {
            updateStatus(`${isFirstBatch ? 'Pitch generation' : 'More pitches'} complete! Click pitches to select.`, 'success');
            eventSource.close();
            return;
        }

        // Handle errors
        if (data.error) {
            updateStatus('Error: ' + data.message, 'error');
            eventSource.close();
            if (isFirstBatch) {
                pitchesList.innerHTML = '<p>Failed to generate pitches. Try again.</p>';
            }
            return;
        }

        // Handle pitch data
        if (data.pitch) {
            pitchesData.push(data.pitch);
            renderPitches();
        }
    };

    eventSource.onerror = (error) => {
        updateStatus('Connection error generating pitches', 'error');
        eventSource.close();
        if (isFirstBatch) {
            pitchesList.innerHTML = '<p>Failed to generate pitches. Check console for details.</p>';
        }
        console.error('SSE Error:', error);
    };
}

function checkPitchValidity(pitch, inventory) {
    // Check if a pitch's ingredients are still available in the inventory
    if (!pitch.explicit_ingredients || pitch.explicit_ingredients.length === 0) {
        return true;  // No explicit ingredients, always valid
    }

    if (!inventory) {
        return true;  // No inventory tracking yet, assume valid
    }

    // Check each ingredient
    for (const ing of pitch.explicit_ingredients) {
        let found = false;
        let sufficient = false;

        for (const storeName in inventory) {
            const items = inventory[storeName];
            if (ing.name in items) {
                found = true;
                const [availableQty, availableUnit] = items[ing.name];
                // Simple check: is there enough quantity? (ignoring unit conversion for now)
                if (availableQty >= ing.quantity) {
                    sufficient = true;
                    break;
                }
            }
        }

        if (!found || !sufficient) {
            return false;  // At least one ingredient is missing or insufficient
        }
    }

    return true;  // All ingredients available
}

function renderPitches() {
    const pitchesList = document.getElementById('pitchesList');

    // Check validity and update invalid set
    invalidPitches.clear();
    pitchesData.forEach((pitch, i) => {
        if (!checkPitchValidity(pitch, currentInventory)) {
            invalidPitches.add(i);
        }
    });

    // Show status if there are invalid pitches
    const invalidCount = invalidPitches.size;
    const statusMsg = invalidCount > 0
        ? `<div style="padding: 10px; background: #fff3cd; border: 1px solid #ffc107; margin-bottom: 10px; border-radius: 4px;">⚠️ ${invalidCount} pitch${invalidCount > 1 ? 'es' : ''} no longer possible with remaining inventory (marked grayed out)</div>`
        : '';

    pitchesList.innerHTML = statusMsg + pitchesData.map((pitch, i) => {
        // Format explicit ingredients for display
        const explicitIngDisplay = pitch.explicit_ingredients && pitch.explicit_ingredients.length > 0
            ? pitch.explicit_ingredients.map(ing => `${ing.quantity} ${ing.unit} ${ing.name}`).join(', ')
            : 'None specified';

        const isInvalid = invalidPitches.has(i);
        const invalidClass = isInvalid ? ' invalid' : '';
        const invalidStyle = isInvalid ? ' style="opacity: 0.5; background: #f5f5f5; pointer-events: none;"' : '';

        return `
            <div class="pitch-card ${selectedPitches.has(i) ? 'selected' : ''}${invalidClass}" onclick="togglePitchSelection(${i})"${invalidStyle}>
                <h4>${pitch.name}${isInvalid ? ' <span style="color: #999; font-size: 0.8em;">(unavailable)</span>' : ''}</h4>
                <div class="blurb">${pitch.blurb}</div>
                <div style="margin: 8px 0; font-size: 0.85em; color: #666;">
                    <strong>Claims:</strong> ${explicitIngDisplay}
                </div>
                <div style="margin: 8px 0; font-size: 0.9em;">
                    <strong>Why:</strong> ${pitch.why_make_this} · <strong>Time:</strong> ~${pitch.active_time} min
                </div>
            </div>
        `;
    }).join('');
}

function togglePitchSelection(index) {
    if (selectedPitches.has(index)) {
        selectedPitches.delete(index);
    } else {
        selectedPitches.add(index);
    }
    renderPitches();
}

async function fleshOutSelected() {
    if (selectedPitches.size === 0) {
        alert('Please select at least one pitch');
        return;
    }

    updateStatus(`Fleshing out ${selectedPitches.size} selected pitches...`, 'info');

    const additionalContext = document.getElementById('additionalContext').value;
    const recipesList = document.getElementById('recipesList');

    // Clear old recipes
    recipesList.innerHTML = '';

    let recipeCount = 0;
    for (const pitchIndex of selectedPitches) {
        const pitch = pitchesData[pitchIndex];
        recipeCount++;

        // Show what's being claimed
        const claimingDisplay = pitch.explicit_ingredients && pitch.explicit_ingredients.length > 0
            ? pitch.explicit_ingredients.map(ing => `${ing.quantity} ${ing.unit} ${ing.name}`).join(', ')
            : 'no explicit ingredients';

        // Add loading state
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'recipe-card streaming';
        loadingDiv.innerHTML = `<h4>Fleshing out ${recipeCount}/${selectedPitches.size}: ${pitch.name}</h4><p style="font-size: 0.9em; color: #666;">Claiming: ${claimingDisplay}...</p>`;
        recipesList.appendChild(loadingDiv);

        try {
            const response = await fetch('/flesh-out-pitch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    pitch_name: pitch.name,
                    additional_context: additionalContext,
                    explicit_ingredients: pitch.explicit_ingredients || [],
                    available_inventory: currentInventory || {}
                })
            });

            const result = await response.json();

            if (result.success) {
                const recipe = result.recipe;

                // Update inventory state for next recipe
                currentInventory = result.updated_inventory;

                // Show claimed ingredients
                const claimedDisplay = result.claimed_ingredients && result.claimed_ingredients.length > 0
                    ? result.claimed_ingredients.map(ing => `${ing.quantity} ${ing.unit} ${ing.name}`).join(', ')
                    : 'none';

                loadingDiv.className = 'recipe-card';
                loadingDiv.innerHTML = `
                    <h4>${recipe.name}</h4>
                    <p style="font-size: 0.85em; color: #28a745;"><strong>✓ Claimed:</strong> ${claimedDisplay}</p>
                    <p><strong>Ingredients:</strong><br>${recipe.ingredients.join('<br>')}</p>
                    <p><strong>Instructions:</strong><br>${recipe.instructions.replace(/\n/g, '<br>')}</p>
                    <p><strong>Time:</strong> ${recipe.active_time} min active${recipe.passive_time ? ' + ' + recipe.passive_time + ' min passive' : ''}</p>
                    <p><strong>Servings:</strong> ${recipe.servings}</p>
                    ${recipe.notes ? `<p><strong>Notes:</strong> ${recipe.notes}</p>` : ''}
                    <button onclick="acceptRecipe('${recipe.name}')">Accept Recipe</button>
                `;
            } else {
                loadingDiv.innerHTML = `<p>Failed to flesh out ${pitch.name}: ${result.error}</p>`;
            }
        } catch (error) {
            loadingDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    }

    updateStatus('Fleshing out complete! Recipes saved to meal plan.', 'success');

    // Reload available inventory from backend (accounts for newly saved claims)
    try {
        const invResponse = await fetch('/api/inventory/available');
        const invData = await invResponse.json();
        currentInventory = invData.inventory;
    } catch (error) {
        console.error('Failed to reload available inventory:', error);
    }

    // Reload planned recipes to show newly saved recipes
    loadPlannedRecipes();

    // Re-render pitches to mark invalid ones
    renderPitches();
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

async function loadPlannedRecipes() {
    try {
        const response = await fetch('/api/recipes/planned');
        const data = await response.json();

        const plannedList = document.getElementById('plannedRecipesList');

        if (!data.recipes || data.recipes.length === 0) {
            plannedList.innerHTML = '<p style="color: #999; font-style: italic;">No planned recipes yet. Flesh out some pitches to get started!</p>';
            return;
        }

        plannedList.innerHTML = data.recipes.map(recipe => {
            const claimsDisplay = recipe.claims && recipe.claims.length > 0
                ? recipe.claims.map(c => `${c.quantity} ${c.unit} ${c.ingredient}`).join(', ')
                : 'No claims';

            return `
                <div class="planned-recipe" id="planned-${recipe.id}" onclick="togglePlannedRecipe('${recipe.id}')">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${recipe.name}</strong>
                            <div style="font-size: 0.85em; color: #666; margin-top: 4px;">
                                ${recipe.active_time} min · ${recipe.servings} servings
                            </div>
                        </div>
                    </div>
                    <div class="planned-recipe-details">
                        <div style="font-size: 0.9em; color: #666; margin-bottom: 8px;">
                            <strong>Claims:</strong> ${claimsDisplay}
                        </div>
                        <p><strong>Ingredients:</strong><br>${recipe.ingredients.join('<br>')}</p>
                        <p><strong>Instructions:</strong><br>${recipe.instructions.replace(/\n/g, '<br>')}</p>
                        ${recipe.notes ? `<p><strong>Notes:</strong> ${recipe.notes}</p>` : ''}
                        <div class="recipe-actions">
                            <button class="btn-cook" onclick="event.stopPropagation(); cookRecipe('${recipe.id}')">Mark as Cooked</button>
                            <button class="btn-abandon" onclick="event.stopPropagation(); abandonRecipe('${recipe.id}')">Abandon Recipe</button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Failed to load planned recipes:', error);
        updateStatus('Failed to load planned recipes', 'error');
    }
}

function togglePlannedRecipe(recipeId) {
    const recipeDiv = document.getElementById(`planned-${recipeId}`);
    recipeDiv.classList.toggle('expanded');
}

async function cookRecipe(recipeId) {
    if (!confirm('Mark this recipe as cooked? This will decrement your inventory.')) {
        return;
    }

    try {
        const response = await fetch(`/api/recipes/${recipeId}/cook`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            updateStatus(result.message, 'success');

            // Reload available inventory (claims consumed, physical inventory decremented)
            const invResponse = await fetch('/api/inventory/available');
            const invData = await invResponse.json();
            currentInventory = invData.inventory;

            // Reload planned recipes and inventory display
            loadPlannedRecipes();
            loadFlatInventory();  // Refresh flat view
            loadShoppingList();  // Refresh shopping list
            if (currentStoreId) {
                loadInventory();
            }
        } else {
            updateStatus('Failed to mark as cooked: ' + result.error, 'error');
        }
    } catch (error) {
        updateStatus('Error: ' + error.message, 'error');
    }
}

async function abandonRecipe(recipeId) {
    if (!confirm('Abandon this recipe? Claims will be released.')) {
        return;
    }

    try {
        const response = await fetch(`/api/recipes/${recipeId}/abandon`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            updateStatus(result.message, 'success');

            // Reload available inventory (claims released, ingredients available again)
            const invResponse = await fetch('/api/inventory/available');
            const invData = await invResponse.json();
            currentInventory = invData.inventory;

            // Reload planned recipes
            loadPlannedRecipes();
            loadFlatInventory();  // Refresh flat view
            loadShoppingList();  // Refresh shopping list
        } else {
            updateStatus('Failed to abandon: ' + result.error, 'error');
        }
    } catch (error) {
        updateStatus('Error: ' + error.message, 'error');
    }
}

async function loadFlatInventory() {
    try {
        const response = await fetch('/api/inventory/flat');
        const data = await response.json();

        const flatList = document.getElementById('flatInventoryList');

        if (!data.items || data.items.length === 0) {
            flatList.innerHTML = '<p style="color: #999; font-style: italic; padding: 20px; text-align: center;">No ingredients yet. Add some to get started!</p>';
            return;
        }

        flatList.innerHTML = data.items.map(item => {
            const reservedText = item.reserved_quantity > 0
                ? `<span style="color: #999; font-size: 0.85em;">(${item.reserved_quantity} reserved)</span>`
                : '';

            return `
                <div class="flat-inventory-item ${item.priority}">
                    <div style="flex: 1;">
                        <div style="font-weight: 500; margin-bottom: 4px;">
                            ${item.ingredient_name}
                        </div>
                        <div style="font-size: 0.85em; color: #666;">
                            ${item.available_quantity} ${item.unit} available ${reservedText} · <span style="color: #999;">${item.store_name}</span>
                        </div>
                    </div>
                    <div>
                        <span class="priority-badge ${item.priority}" onclick="cyclePriority('${item.id}', '${item.priority}')" title="Click to change priority">
                            ${item.priority}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        console.error('Failed to load flat inventory:', error);
        updateStatus('Failed to load flat inventory', 'error');
    }
}

async function loadShoppingList() {
    try {
        const response = await fetch('/api/claims/by-store');
        const data = await response.json();

        const shoppingSection = document.getElementById('shoppingListSection');
        const groceryList = document.getElementById('groceryList');
        const pantryList = document.getElementById('pantryList');

        // Check if there are any claims
        if (!data.stores || Object.keys(data.stores).length === 0) {
            shoppingSection.style.display = 'none';
            return;
        }

        // Show the shopping list
        shoppingSection.style.display = 'block';

        // Separate stores by type
        const groceryStores = {};
        const pantryStores = {};
        const otherStores = {};

        for (const [storeName, storeData] of Object.entries(data.stores)) {
            if (storeData.type === 'definition' && storeName.toLowerCase().includes('pantry')) {
                pantryStores[storeName] = storeData;
            } else if (storeData.type === 'explicit') {
                // Skip explicit stores (CSA, Freezer) - those are handled via inventory
                continue;
            } else {
                // Grocery or other stores
                groceryStores[storeName] = storeData;
            }
        }

        // Render grocery stores
        if (Object.keys(groceryStores).length > 0) {
            groceryList.innerHTML = Object.entries(groceryStores).map(([storeName, storeData]) => {
                const ingredientsList = Object.entries(storeData.ingredients)
                    .map(([ingName, ingData]) => {
                        const recipesList = ingData.recipes.join(', ');
                        return `
                            <div class="shopping-item">
                                <div>${ingData.total_quantity} ${ingData.unit} ${ingName}</div>
                                <div class="recipes">used in: ${recipesList}</div>
                            </div>
                        `;
                    }).join('');

                // Create plain text version for copying
                const plainText = Object.entries(storeData.ingredients)
                    .map(([ingName, ingData]) => `${ingData.total_quantity} ${ingData.unit} ${ingName}`)
                    .join('\n');

                return `
                    <div class="store-section">
                        <h4>${storeName}</h4>
                        <button class="copy-btn" onclick="copyToClipboard(\`${plainText}\`, '${storeName}')">Copy List</button>
                        ${ingredientsList}
                    </div>
                `;
            }).join('');
        } else {
            groceryList.innerHTML = '<p style="color: #999; font-style: italic;">No grocery items needed</p>';
        }

        // Render pantry verification
        if (Object.keys(pantryStores).length > 0) {
            pantryList.innerHTML = Object.entries(pantryStores).map(([storeName, storeData]) => {
                const ingredientsList = Object.entries(storeData.ingredients)
                    .map(([ingName, ingData]) => {
                        const recipesList = ingData.recipes.join(', ');
                        return `
                            <div class="shopping-item">
                                <div>Check you have ${ingData.total_quantity} ${ingData.unit} ${ingName}</div>
                                <div class="recipes">for: ${recipesList}</div>
                            </div>
                        `;
                    }).join('');

                return `
                    <div class="store-section">
                        <h4>${storeName}</h4>
                        ${ingredientsList}
                    </div>
                `;
            }).join('');
        } else {
            pantryList.innerHTML = '<p style="color: #999; font-style: italic;">No pantry items to verify</p>';
        }

    } catch (error) {
        console.error('Failed to load shopping list:', error);
        updateStatus('Failed to load shopping list', 'error');
    }
}

function copyToClipboard(text, storeName) {
    navigator.clipboard.writeText(text).then(() => {
        updateStatus(`${storeName} list copied to clipboard!`, 'success');
    }).catch(err => {
        updateStatus('Failed to copy to clipboard', 'error');
    });
}

async function cyclePriority(itemId, currentPriority) {
    // Cycle through priorities: low -> medium -> high -> urgent -> low
    const priorities = ['low', 'medium', 'high', 'urgent'];
    const currentIndex = priorities.indexOf(currentPriority);
    const nextPriority = priorities[(currentIndex + 1) % priorities.length];

    try {
        const response = await fetch(`/inventory/${itemId}/priority`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ priority: nextPriority })
        });

        if (response.ok) {
            updateStatus(`Priority updated to ${nextPriority}`, 'success');
            loadFlatInventory();  // Reload to show new priority order
        }
    } catch (error) {
        updateStatus('Failed to update priority: ' + error.message, 'error');
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