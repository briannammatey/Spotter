# backend/recipeSuggestions/suggest.py

from typing import List, Dict, Any
import random


# ---- Tiny in-memory "database" of recipes ----
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
        "diet": ["No Preference"],
        "meal_type": "Breakfast",
        "calories": 500,
        "cook_time_min": 15,
        "ingredients": ["eggs", "spinach", "peppers", "olive oil", "toast"],
        "instructions": "Scramble eggs with veggies in olive oil, serve with toast."
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

    # SNACK
    {
        "name": "Greek Yogurt with Banana & PB",
        "goal": ["Bulking", "Maintenance"],
        "diet": ["No Preference", "High Protein"],
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
]


def _normalize_list_field(field: str) -> List[str]:
    if not field:
        return []
    return [x.strip().lower() for x in field.split(",") if x.strip()]


def generate_day_plan(
    goal: str,
    diet: str,
    calorie_target: str,
    cooking_time: str,
    have_ingredients: str,
    avoid_ingredients: str,
    max_daily_calories: int = 2000,
) -> Dict[str, Any]:
    """
    Build a simple 1-day meal plan given preferences.
    Returns dict: {"meals": [...], "total_calories": int}
    """
    goal = (goal or "No Preference").strip()
    diet = (diet or "No Preference").strip()

    have_list = _normalize_list_field(have_ingredients)
    avoid_list = _normalize_list_field(avoid_ingredients)

    # Map the UI's cooking time button to minutes
    max_time = 999
    if cooking_time == "Under 15 min":
        max_time = 15
    elif cooking_time == "15-30 min":
        max_time = 30
    elif cooking_time == "30+ min":
        max_time = 120

    # Optional per-meal target from UI (~300, ~500, etc.)
    per_meal_target = None
    if calorie_target:
        # "~300 cal" -> 300
        try:
            per_meal_target = int(calorie_target.strip(" ~cal"))
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
        # If user listed ingredients they have, prefer recipes that overlap;
        # we don't require it, we just mark them later.
        return True

    candidates = [r for r in RECIPES if recipe_ok(r)]

    # Fallback if over-filtered
    if not candidates:
        candidates = RECIPES.copy()

    # Group by meal type so we can assemble a full day
    grouped: Dict[str, List[Dict[str, Any]]] = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snack": []}
    for r in candidates:
        grouped.setdefault(r["meal_type"], []).append(r)

    # Sort each group by closeness to per-meal calorie target (if provided)
    if per_meal_target:
        for mt in grouped:
            grouped[mt].sort(key=lambda r: abs(r["calories"] - per_meal_target))
    else:
        for mt in grouped:
            random.shuffle(grouped[mt])

    # Build the plan: breakfast, lunch, dinner, snack (if fits)
    plan_meals: List[Dict[str, Any]] = []
    total_cal = 0
    for meal_type in ["Breakfast", "Lunch", "Dinner", "Snack"]:
        options = grouped.get(meal_type, [])
        if not options:
            continue
        for recipe in options:
            if total_cal + recipe["calories"] <= max_daily_calories:
                plan_meals.append(recipe)
                total_cal += recipe["calories"]
                break  # move to next meal_type

    return {"meals": plan_meals, "total_calories": total_cal}
