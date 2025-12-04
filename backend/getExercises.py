import json
from openai import OpenAI

client = OpenAI()

# Body parts and associated muscles
BODY_PARTS = {
    "Arms": ["Biceps", "Triceps", "Forearms"],
    "Legs": ["Quads", "Hamstrings", "Calves", "Glutes", "Abductors", "Adductors"],
    "Chest": ["Upper Chest", "Middle Chest", "Lower Chest"],
    "Back": ["Lats", "Traps", "Lower Back", "Rhomboids"],
    "Abs": ["Upper Abs", "Lower Abs", "Obliques"],
    "Shoulders": ["Front Delts", "Side Delts", "Rear Delts"]
}

# Exceptions
class NoBodyPartsSelected(Exception):
    pass

class NoMusclesSelected(Exception):
    pass

class InvalidMuscleSelection(Exception):
    """Raised when selected muscles do not belong to selected body parts."""
    pass


# Displays only the muscles for the selected body parts
def list_muscles_for_body_parts(selected_parts):
    muscles = set()
    for part in selected_parts:
        if part in BODY_PARTS:
            muscles.update(BODY_PARTS[part])
    return sorted(muscles)


# Generates exercises using OpenAI
def generate_exercises(body_parts, muscles):
    """
    Enforces:
        - At least one body part
        - At least one muscle
        - All muscles must belong to selected body parts
    """
    # Validation
    if not body_parts:
        raise NoBodyPartsSelected("At least one body part must be selected.")

    if not muscles:
        raise NoMusclesSelected("At least one muscle must be selected.")

    # Get valid muscles for the selected body parts
    allowed_muscles = list_muscles_for_body_parts(body_parts)

    # Check invalid selections
    invalid_muscles = [m for m in muscles if m not in allowed_muscles]

    if invalid_muscles:
        raise InvalidMuscleSelection(
            f"Invalid muscles for selected body parts: {invalid_muscles}. "
            f"Allowed muscles are: {allowed_muscles}"
        )

    # OpenAI prompt
    prompt = f"""
    Generate a JSON object with an "exercises" key containing a list of 
    weightlifting exercises that target ONLY:
    Body parts: {', '.join(body_parts)}
    Muscles: {', '.join(muscles)}

    For each exercise, include:
    - name
    - primary_muscle
    - secondary_muscles (as a list)
    - equipment
    - instructions (as a list of 2-4 bullet points)

    Return a JSON object with format: {{"exercises": [...]}}
    Return ONLY valid JSON, no additional text.
    """

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("exercises", [])