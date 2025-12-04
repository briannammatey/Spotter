from datetime import datetime
from openai import OpenAI

client = OpenAI()

# Coordinates for searching off-campus classes
BU_LAT = 42.3505
BU_LON = -71.1054

# Fall 2025 FitRec schedule (on-campus drop-in classes)
# Needs to be updated each semester
FITREC_SCHEDULE = {
    "Monday": [
        ("5:30–6:30p", "Vinyasa Yoga"),
        ("5:45–6:30p", "Sunset Spin"),
        ("6:00–7:00p", "Barre Pilates Fusion"),
        ("6:30–7:30p", "Core Intensive Yoga")
    ],
    "Tuesday": [
        ("9:30–10:30a", "Tai Chi"),
        ("5:30–6:30p", "Zumba"),
        ("6:00–7:00p", "Vinyasa Yoga"),
        ("6:45–7:30p", "Pilates Mat")
    ],
    "Wednesday": [
        ("5:30–6:30p", "Hatha Yoga"),
        ("5:45–6:30p", "TRX Circuit"),
        ("6:00–7:00p", "Barre Pilates Fusion"),
        ("6:30–7:30p", "Deep Stretch Yoga")
    ],
    "Thursday": [
        ("9:30–10:30a", "Tai Chi"),
        ("12:00–1pm", "Zen Meditation"),
        ("5:30–6:30p", "Yoga Pilates Fusion"),
        ("5:45–6:30p", "Zumba"),
        ("6:00–6:45p", "Total Body Conditioning")
    ],
    "Friday": [
        ("4:00–4:45p", "Sunset Spin"),
        ("5:00–5:45p", "Strength 45")
    ],
    "Saturday": [
        ("10:30–11:30a", "Yoga Basics"),
        ("11:00–11:45a", "Zumba")
    ],
    "Sunday": [
        ("10:30–11:15a", "Spin the Decades"),
        ("11:00–11:45a", "Total Body Dumbell")
    ]
}

CATEGORIES = [
    "boxing", "cardio", "cycling", "dance", "martial arts",
    "pilates", "strength conditioning", "yoga"
]

# Sorts FitRec classes into the given categories
def infer_category(class_name):
    name = class_name.lower()
    if "yoga" in name or "meditation" in name:
        return "yoga"
    if "pilates" in name or "barre" in name:
        return "pilates"
    if "spin" in name or "cycling" in name:
        return "cycling"
    if "zumba" in name or "dance" in name:
        return "dance"
    if "tai chi" in name or "martial" in name:
        return "martial arts"
    if "strength" in name or "trx" in name or "conditioning" in name:
        return "strength conditioning"
    return "cardio"


def standardize_time(time_str):
    try:
        parts = time_str.replace("–", "-").split("-")
        start = datetime.strptime(parts[0].strip(), "%I:%M%p").strftime("%H:%M")
        end = datetime.strptime(parts[1].strip(), "%I:%M%p").strftime("%H:%M")
        return f"{start}-{end}"
    except:
        return time_str


def format_fitrec_classes():
    formatted = []
    for day, class_list in FITREC_SCHEDULE.items():
        for time_str, name in class_list:
            formatted.append({
                "day": day,
                "name": name,
                "category": infer_category(name),
                "time": standardize_time(time_str),
                "location": "BU FitRec",
                "lat": BU_LAT,
                "lon": BU_LON
            })
    return formatted


# OpenAI prompt for off campus classes

def search_off_campus_exercise(categories):
    """
    categories = list of strings
    Ask OpenAI for multiple class types at once.
    """

    SYSTEM_PROMPT = """
    You are a Boston fitness expert. Return a JSON object with a key "classes" containing a list of off-campus
    fitness studios near Boston University. For each class include:
    - name
    - category
    - address
    - distance_mi
    - description
    - website or phone if known
    """

    user_prompt = f"""
    Find OFF-CAMPUS fitness class locations near Boston University.
    Categories requested: {", ".join(categories)}.
    Provide 8–15 results across ANY of the categories.
    Return a JSON object in the format {{ "classes": [...] }}.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    try:
        import json
        result = json.loads(response.choices[0].message.content)  # Fixed: output_json() -> proper parsing
        return result.get("classes", [])
    except Exception as e:
        print(f"Error parsing OpenAI response: {e}")
        return []


# Main function
def find_classes(campus, categories=None):
    """
    campus: "on" or "off"
    categories: list of selected class types
    """

    if categories is None or len(categories) == 0:
        raise ValueError("You must select at least one category before searching for classes.")

    categories = [c.lower() for c in categories]

    # On campus
    if campus == "on":
        classes = format_fitrec_classes()

        if categories:
            classes = [c for c in classes if c["category"] in categories]

        return classes

    # Off campus
    elif campus == "off":
        return search_off_campus_exercise(categories)

    else:
        raise ValueError("You must select 'On Campus' or 'Off Campus'")
