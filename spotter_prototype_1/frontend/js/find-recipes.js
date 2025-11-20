// Find Recipes Page JavaScript

let selectedMealType = null;
let selectedFitnessGoal = null;

document.addEventListener('DOMContentLoaded', function() {
    const mealTypeButtons = document.querySelectorAll('.meal-type-btn');
    const fitnessGoalButtons = document.querySelectorAll('.fitness-goal-btn');
    const getRecipesBtn = document.getElementById('getRecipesBtn');

    // Meal type selection
    mealTypeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            mealTypeButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedMealType = this.dataset.meal;
        });
    });

    // Fitness goal selection
    fitnessGoalButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            fitnessGoalButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedFitnessGoal = this.dataset.goal;
        });
    });

    // Get recipes button
    if (getRecipesBtn) {
        getRecipesBtn.addEventListener('click', async function() {
            if (!selectedMealType) {
                showError('errorMessage', 'Please select a type of meal');
                return;
            }

            if (!selectedFitnessGoal) {
                showError('errorMessage', 'Please select your fitness goals');
                return;
            }

            try {
                getRecipesBtn.disabled = true;
                getRecipesBtn.textContent = 'LOADING...';

                const result = await apiCall('/recipe-suggestion', 'POST', {
                    meal_type: selectedMealType,
                    fitness_goal: selectedFitnessGoal
                });

                displayRecipeResults(result.recipe);
                document.getElementById('errorMessage').style.display = 'none';
            } catch (error) {
                showError('errorMessage', error.message);
            } finally {
                getRecipesBtn.disabled = false;
                getRecipesBtn.textContent = 'GET RECIPES';
            }
        });
    }
});

function displayRecipeResults(recipe) {
    const resultsContainer = document.getElementById('recipeResults');
    const recipeDetails = document.getElementById('recipeDetails');

    if (!recipe) {
        showError('errorMessage', 'No recipe found matching your criteria');
        return;
    }

    recipeDetails.innerHTML = `
        <h4>${recipe.name}</h4>
        <p><strong>Meal Type:</strong> ${recipe.meal_type.toUpperCase()}</p>
        <p><strong>Fitness Goal:</strong> ${recipe.fitness_goal.replace('_', ' ').toUpperCase()}</p>
        
        <h5>INGREDIENTS</h5>
        <ul>
            ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
        </ul>
        
        <h5>INSTRUCTIONS</h5>
        <ol>
            ${recipe.instructions.map(inst => `<li>${inst}</li>`).join('')}
        </ol>
        
        <h5>NUTRITION INFORMATION</h5>
        <ul>
            <li><strong>Calories:</strong> ${recipe.nutrition_info.calories}</li>
            <li><strong>Protein:</strong> ${recipe.nutrition_info.protein}</li>
            <li><strong>Carbs:</strong> ${recipe.nutrition_info.carbs}</li>
            <li><strong>Fats:</strong> ${recipe.nutrition_info.fats}</li>
        </ul>
    `;

    resultsContainer.style.display = 'block';
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

