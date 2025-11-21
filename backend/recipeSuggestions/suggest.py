# backend/recipeSuggestions/suggest.py

from typing import Dict, Any
import os
import json
from openai import OpenAI

# Let the client read OPENAI_API_KEY from the environment itself
client = OpenAI()   # no api_key=..., it reads from env


def generate_day_plan(
    goal: str,
    diet: str,
    calorie_target: str,
    cooking_time: str,
    have_ingredients: str,
    avoid_ingredients: str,
    max_daily_calories: int = 2000,  # kept for compatibility
) -> Dict[str, Any]:
    """
    Generate ONE meal using the OpenAI API based on user preferences.
    Returns: {"meals": [recipe_dict], "total_calories": calories_of_that_meal}
    """

    goal = (goal or "").lower()
    diet = (diet or "none").lower()
    cooking_time = (cooking_time or "long").lower()
    have_ingredients = have_ingredients or ""
    avoid_ingredients = avoid_ingredients or ""

    goal_text = {
        "bulking": "bulking (higher calories, high protein)",
        "cutting": "cutting (calorie deficit, high protein)",
        "maintenance": "maintenance (moderate calories)",
    }.get(goal, "general fitness")

    diet_text = {
        "none": "no specific diet",
        "vegetarian": "vegetarian",
        "vegan": "vegan",
        "keto": "keto",
        "highprotein": "high protein",
        "glutenfree": "gluten-free",
    }.get(diet, "no specific diet")

    time_text = {
        "quick": "under 15 minutes",
        "medium": "15–30 minutes",
        "long": "up to 60 minutes",
    }.get(cooking_time, "up to 60 minutes")

    per_meal_cal = None
    if calorie_target:
        try:
            per_meal_cal = int(calorie_target)
        except ValueError:
            per_meal_cal = None

    calorie_sentence = (
        f" Aim for roughly {per_meal_cal} calories for this meal."
        if per_meal_cal
        else " Aim for a reasonable calorie amount for this meal, not exceeding 1000 calories."
    )

    user_prompt = f"""
Generate ONE realistic, college-student-friendly meal recipe.

Constraints:
- Goal: {goal_text}
- Dietary preference: {diet_text}
- Cooking time: {time_text}
- Ingredients the user has (optional): {have_ingredients if have_ingredients.strip() else "user did not specify"}
- Ingredients / allergens to avoid: {avoid_ingredients if avoid_ingredients.strip() else "none specified"}
- The meal should be something a student could reasonably cook in a small college kitchen.
- Use common ingredients that are not extremely expensive.
-{calorie_sentence}

Output format (VERY IMPORTANT):
Return ONLY a single JSON object, no extra text, matching this structure exactly:

{{
  "name": "string",
  "meal_type": "breakfast | lunch | dinner | snack",
  "calories": 600,
  "ingredients": ["list", "of", "ingredients"],
  "instructions": "step-by-step instructions as a single string"
}}
    """.strip()

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrition and fitness assistant that designs practical recipes.",
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )
    except Exception as e:
        # Bubble up a clear error so the route can see it
        raise RuntimeError(f"OpenAI API call failed: {e}")

    raw_content = completion.choices[0].message.content
    try:
        recipe = json.loads(raw_content)
    except json.JSONDecodeError:
        recipe = {
            "name": "Fallback Meal",
            "meal_type": "meal",
            "calories": per_meal_cal or 600,
            "ingredients": [],
            "instructions": "Recipe generation failed. Please try again.",
        }

    calories = int(recipe.get("calories", per_meal_cal or 600))

    return {
        "meals": [recipe],
        "total_calories": calories,
    }
