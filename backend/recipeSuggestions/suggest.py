# backend/recipeSuggestions/suggest.py

from typing import List, Dict, Any
import random



RECIPES: List[Dict[str, Any]] = [
    # BREAKFAST 
    {
        "name": "High-Protein Berry Oatmeal",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["No Preference", "Vegetarian"],
        "meal_type": "Breakfast",
        "calories": 400,
        "cook_time_min": 10,
        "ingredients": ["oats", "protein powder", "berries", "almond milk"],
        "instructions": "Cook oats in almond milk, stir in protein powder, top with berries."
    },
    {
        "name": "Veggie Egg Scramble with Toast",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "Vegetarian"],
        "meal_type": "Breakfast",
        "calories": 500,
        "cook_time_min": 15,
        "ingredients": ["eggs", "spinach", "peppers", "olive oil", "toast"],
        "instructions": "Scramble eggs with veggies in olive oil, serve with toast."
    },
    {
        "name": "Avocado Toast with Poached Eggs",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "Vegetarian"],
        "meal_type": "Breakfast",
        "calories": 450,
        "cook_time_min": 12,
        "ingredients": ["avocado", "eggs", "whole grain bread", "cherry tomatoes"],
        "instructions": "Mash avocado on toasted bread, top with poached eggs and tomatoes."
    },
    {
        "name": "Protein Pancakes with Berries",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "Vegetarian", "High Protein"],
        "meal_type": "Breakfast",
        "calories": 520,
        "cook_time_min": 18,
        "ingredients": ["protein powder", "banana", "eggs", "oats", "berries"],
        "instructions": "Blend ingredients, cook pancakes, top with fresh berries."
    },
    {
        "name": "Vegan Protein Smoothie Bowl",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Vegan", "Vegetarian"],
        "meal_type": "Breakfast",
        "calories": 350,
        "cook_time_min": 8,
        "ingredients": ["banana", "spinach", "vegan protein powder", "almond milk", "chia seeds"],
        "instructions": "Blend all ingredients until smooth, top with chia seeds and fresh fruit."
    },
    {
        "name": "Keto Breakfast Scramble",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Keto", "No Preference"],
        "meal_type": "Breakfast",
        "calories": 420,
        "cook_time_min": 12,
        "ingredients": ["eggs", "cheese", "bacon", "spinach", "butter"],
        "instructions": "Cook bacon, scramble eggs with cheese and spinach in butter."
    },
    {
        "name": "Overnight Oats with Nut Butter",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Breakfast",
        "calories": 380,
        "cook_time_min": 5,
        "ingredients": ["oats", "almond milk", "peanut butter", "maple syrup"],
        "instructions": "Mix all ingredients and refrigerate overnight. Enjoy cold in the morning."
    },

    # LUNCH 
    {
        "name": "Chicken Rice Power Bowl",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Lunch",
        "calories": 600,
        "cook_time_min": 25,
        "ingredients": ["chicken", "rice", "broccoli", "olive oil"],
        "instructions": "Grill chicken, steam broccoli, serve over rice with olive oil."
    },
    {
        "name": "Tofu Quinoa Bowl",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["Vegetarian", "Vegan", "High Protein"],
        "meal_type": "Lunch",
        "calories": 550,
        "cook_time_min": 25,
        "ingredients": ["tofu", "quinoa", "spinach", "tomato"],
        "instructions": "Pan-fry tofu, cook quinoa, mix with veggies."
    },
    {
        "name": "Turkey & Avocado Wrap",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Lunch",
        "calories": 480,
        "cook_time_min": 10,
        "ingredients": ["turkey breast", "avocado", "whole wheat tortilla", "lettuce", "tomato"],
        "instructions": "Layer turkey, sliced avocado, lettuce, and tomato in tortilla and wrap."
    },
    {
        "name": "Mediterranean Chickpea Salad",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Lunch",
        "calories": 420,
        "cook_time_min": 12,
        "ingredients": ["chickpeas", "cucumber", "tomatoes", "feta cheese", "olive oil"],
        "instructions": "Toss chickpeas with chopped veggies, feta, and olive oil dressing."
    },
    {
        "name": "Grilled Salmon Caesar Salad",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Lunch",
        "calories": 520,
        "cook_time_min": 20,
        "ingredients": ["salmon", "romaine lettuce", "parmesan", "caesar dressing"],
        "instructions": "Grill salmon, toss lettuce with dressing and parmesan, top with salmon."
    },
    {
        "name": "Veggie Stir-Fry with Brown Rice",
        "goal": ["Maintenance", "Cutting"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Lunch",
        "calories": 490,
        "cook_time_min": 20,
        "ingredients": ["mixed vegetables", "brown rice", "soy sauce", "ginger", "garlic"],
        "instructions": "Stir-fry veggies with ginger and garlic, serve over brown rice with soy sauce."
    },
    {
        "name": "Tuna Poke Bowl",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Lunch",
        "calories": 540,
        "cook_time_min": 15,
        "ingredients": ["tuna", "rice", "edamame", "avocado", "seaweed"],
        "instructions": "Dice tuna, serve over rice with edamame, avocado, and seaweed."
    },
    {
        "name": "Black Bean & Sweet Potato Bowl",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Lunch",
        "calories": 580,
        "cook_time_min": 28,
        "ingredients": ["black beans", "sweet potato", "quinoa", "corn", "lime"],
        "instructions": "Roast sweet potato, cook quinoa, mix with black beans and corn, squeeze lime."
    },

    # DINNER 
    {
        "name": "Salmon, Sweet Potato & Asparagus",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Dinner",
        "calories": 700,
        "cook_time_min": 30,
        "ingredients": ["salmon", "sweet potato", "asparagus", "olive oil"],
        "instructions": "Roast salmon and veggies with olive oil; bake sweet potato."
    },
    {
        "name": "Lentil Pasta with Marinara",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Dinner",
        "calories": 650,
        "cook_time_min": 20,
        "ingredients": ["lentil pasta", "tomato sauce", "garlic"],
        "instructions": "Cook lentil pasta and mix with heated marinara sauce."
    },
    {
        "name": "Grilled Chicken with Roasted Vegetables",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Dinner",
        "calories": 620,
        "cook_time_min": 35,
        "ingredients": ["chicken breast", "bell peppers", "zucchini", "carrots", "olive oil"],
        "instructions": "Grill chicken, roast vegetables with olive oil and herbs."
    },
    {
        "name": "Beef Stir-Fry with Vegetables",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Dinner",
        "calories": 720,
        "cook_time_min": 25,
        "ingredients": ["beef", "mixed vegetables", "soy sauce", "rice", "ginger"],
        "instructions": "Stir-fry beef with veggies and ginger, serve over rice with soy sauce."
    },
    {
        "name": "Vegetarian Buddha Bowl",
        "goal": ["Maintenance", "Cutting"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Dinner",
        "calories": 560,
        "cook_time_min": 25,
        "ingredients": ["chickpeas", "quinoa", "kale", "tahini", "sweet potato"],
        "instructions": "Roast chickpeas and sweet potato, serve over quinoa with kale and tahini dressing."
    },
    {
        "name": "Keto Zucchini Noodles with Pesto",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Keto", "Vegetarian"],
        "meal_type": "Dinner",
        "calories": 480,
        "cook_time_min": 18,
        "ingredients": ["zucchini", "pesto", "parmesan", "pine nuts", "cherry tomatoes"],
        "instructions": "Spiralize zucchini, sauté lightly, toss with pesto, top with parmesan and tomatoes."
    },
    {
        "name": "Shrimp Taco Bowl",
        "goal": ["Maintenance", "Cutting"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Dinner",
        "calories": 580,
        "cook_time_min": 22,
        "ingredients": ["shrimp", "cauliflower rice", "black beans", "salsa", "avocado"],
        "instructions": "Sauté shrimp with spices, serve over cauliflower rice with beans, salsa, and avocado."
    },
    {
        "name": "Stuffed Bell Peppers",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
        "meal_type": "Dinner",
        "calories": 640,
        "cook_time_min": 40,
        "ingredients": ["bell peppers", "ground turkey", "quinoa", "tomatoes", "cheese"],
        "instructions": "Stuff peppers with cooked turkey-quinoa mixture, top with cheese, bake until tender."
    },
    {
        "name": "Quick Veggie Quesadilla Bowl",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian"],
        "meal_type": "Dinner",
        "calories": 680,
        "cook_time_min": 12,
        "ingredients": ["tortilla", "black beans", "cheese", "avocado", "salsa", "sour cream"],
        "instructions": "Heat tortilla with beans and cheese, top with avocado, salsa, and sour cream."
    },
    {
        "name": "Microwave Veggie Burrito Bowl",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian"],
        "meal_type": "Dinner",
        "calories": 720,
        "cook_time_min": 10,
        "ingredients": ["rice", "black beans", "cheese", "corn", "avocado", "salsa"],
        "instructions": "Microwave rice and beans, top with cheese, corn, avocado, and salsa."
    },
    {
        "name": "Speedy Pesto Pasta with Veggies",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian"],
        "meal_type": "Dinner",
        "calories": 690,
        "cook_time_min": 13,
        "ingredients": ["pasta", "pesto", "cherry tomatoes", "mozzarella", "pine nuts"],
        "instructions": "Cook pasta, toss with pesto, add halved tomatoes, mozzarella, and pine nuts."
    },
    {
        "name": "Quick Chickpea Curry",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Dinner",
        "calories": 650,
        "cook_time_min": 14,
        "ingredients": ["chickpeas", "curry sauce", "spinach", "rice", "coconut milk"],
        "instructions": "Heat curry sauce with chickpeas and spinach, serve over microwaved rice."
    },
    {
        "name": "Fast Veggie Fried Rice",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Dinner",
        "calories": 710,
        "cook_time_min": 12,
        "ingredients": ["rice", "mixed vegetables", "soy sauce", "sesame oil", "tofu"],
        "instructions": "Stir-fry cooked rice with veggies, crumbled tofu, soy sauce, and sesame oil."
    },

    # SNACK 
    {
        "name": "Greek Yogurt with Banana & PB",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "High Protein", "Vegetarian"],
        "meal_type": "Snack",
        "calories": 300,
        "cook_time_min": 5,
        "ingredients": ["greek yogurt", "banana", "peanut butter"],
        "instructions": "Slice banana over yogurt and add peanut butter."
    },
    {
        "name": "Apple & Almonds",
        "goal": ["Bulking", "Maintenance", "Cutting"],
        "diet": ["No Preference", "Vegetarian", "Vegan", "Keto"],
        "meal_type": "Snack",
        "calories": 200,
        "cook_time_min": 5,
        "ingredients": ["apple", "almonds"],
        "instructions": "Slice apple and eat with almonds."
    },
    {
        "name": "Protein Energy Balls",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Snack",
        "calories": 280,
        "cook_time_min": 10,
        "ingredients": ["oats", "peanut butter", "honey", "chocolate chips"],
        "instructions": "Mix all ingredients, roll into balls, refrigerate for 30 minutes."
    },
    {
        "name": "Hummus with Veggie Sticks",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Snack",
        "calories": 180,
        "cook_time_min": 5,
        "ingredients": ["hummus", "carrots", "celery", "cucumber"],
        "instructions": "Cut vegetables into sticks and serve with hummus."
    },
    {
        "name": "Cheese & Crackers with Grapes",
        "goal": ["Maintenance", "Bulking"],
        "diet": ["Vegetarian", "No Preference"],
        "meal_type": "Snack",
        "calories": 250,
        "cook_time_min": 5,
        "ingredients": ["cheese", "whole grain crackers", "grapes"],
        "instructions": "Arrange cheese, crackers, and grapes on a plate."
    },
    {
        "name": "Trail Mix",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["Vegetarian", "Vegan", "No Preference"],
        "meal_type": "Snack",
        "calories": 320,
        "cook_time_min": 5,
        "ingredients": ["mixed nuts", "dried fruit", "dark chocolate chips"],
        "instructions": "Mix nuts, dried fruit, and chocolate chips in a bowl."
    },
    {
        "name": "Cottage Cheese with Berries",
        "goal": ["Cutting", "Maintenance"],
        "diet": ["Vegetarian", "High Protein"],
        "meal_type": "Snack",
        "calories": 220,
        "cook_time_min": 5,
        "ingredients": ["cottage cheese", "mixed berries", "honey"],
        "instructions": "Top cottage cheese with fresh berries and a drizzle of honey."
    },
    {
        "name": "Rice Cakes with Almond Butter",
        "goal": ["Maintenance", "Cutting"],
        "diet": ["Vegetarian", "Vegan"],
        "meal_type": "Snack",
        "calories": 240,
        "cook_time_min": 5,
        "ingredients": ["rice cakes", "almond butter", "banana"],
        "instructions": "Spread almond butter on rice cakes, top with banana slices."
    },
]


def _normalize_list_field(field: str) -> List[str]:
    if not field:
        return []
    return [x.strip().lower() for x in field.split(",") if x.strip()]


def generate_day_plan(
    goal: str,
    diet: str,
    meal_type: str,
    calorie_target: str,
    cooking_time: str,
    have_ingredients: str,
    avoid_ingredients: str,
    max_daily_calories: int = 2000,
) -> Dict[str, Any]:
    """
    Build a meal plan given preferences.
    If meal_type is specified, only returns recipes for that meal type.
    Returns dict: {"meals": [...], "total_calories": int}
    """
    goal = (goal or "No Preference").strip()
    diet = (diet or "No Preference").strip()
    meal_type = (meal_type or "").strip()

    have_list = _normalize_list_field(have_ingredients)
    avoid_list = _normalize_list_field(avoid_ingredients)

    # Map the UI's cooking time button to minutes
    max_time = 999
    if cooking_time == "quick":
        max_time = 15
    elif cooking_time == "medium":
        max_time = 30
    elif cooking_time == "long":
        max_time = 120

    # Optional per-meal target from UI (300, 500, etc.)
    per_meal_target = None
    if calorie_target:
        try:
            per_meal_target = int(calorie_target)
        except ValueError:
            per_meal_target = None

    # ---- Filter recipes based on basic prefs ----
    def recipe_ok(r: Dict[str, Any]) -> bool:
        if goal != "No Preference" and goal not in r["goal"]:
            return False
        if diet != "No Preference" and diet not in r["diet"]:
            return False
        if r["cook_time_min"] > max_time:
            return False
        # Must not contain avoided ingredients
        if avoid_list and any(a in r["ingredients"] for a in avoid_list):
            return False
        # Filter by meal type if specified
        if meal_type and r["meal_type"].lower() != meal_type.lower():
            return False
        return True

    candidates = [r for r in RECIPES if recipe_ok(r)]

    # Determine which meal types to include
    if meal_type:
        # User selected a specific meal type - only return that type
        meal_types_to_include = [meal_type.capitalize()]
    else:
        # No specific meal type - return full day plan
        meal_types_to_include = ["Breakfast", "Lunch", "Dinner", "Snack"]

    # Group by meal type
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for r in candidates:
        grouped.setdefault(r["meal_type"], []).append(r)

    # Sort each group by closeness to per-meal calorie target (if provided)
    if per_meal_target:
        for mt in grouped:
            grouped[mt].sort(key=lambda r: abs(r["calories"] - per_meal_target))
    else:
        for mt in grouped:
            random.shuffle(grouped[mt])

    # Build the plan based on selected meal types
    plan_meals: List[Dict[str, Any]] = []
    total_cal = 0
    
    for meal_type_name in meal_types_to_include:
        options = grouped.get(meal_type_name, [])
        if not options:
            continue
        for recipe in options:
            if total_cal + recipe["calories"] <= max_daily_calories:
                plan_meals.append(recipe)
                total_cal += recipe["calories"]
                break  # move to next meal_type

    return {"meals": plan_meals, "total_calories": total_cal}
