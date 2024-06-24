import requests
from bs4 import BeautifulSoup
import re
import json

# URL of the screenplay
url = "https://imsdb.com/scripts/Reservoir-Dogs.html"

# Get the page content
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find the main content of the screenplay
script_content = soup.find("td", class_="scrtext").find("pre").get_text(separator="\n")


def parse_screenplay(script):
    scenes = []
    characters = {}
    current_scene = None
    current_characters = set()
    dialogue_interactions = {}

    lines = script.split("\n")
    scene_pattern = re.compile(r"^\s*(INT\.|EXT\.)")
    character_pattern = re.compile(r"^[A-Z][A-Z\s]+$")
    dialogue_pattern = re.compile(r"^\s{10,}")

    current_character = None

    for line in lines:
        # Identify new scenes
        if scene_pattern.match(line):
            if current_scene:
                current_scene["characters"] = list(current_characters)
                scenes.append(current_scene)
            current_scene = {
                "scene_number": len(scenes) + 1,
                "location": line.strip(),
                "characters": [],
            }
            current_characters = set()
        # Identify characters and their dialogues
        elif character_pattern.match(line.strip()) and not line.strip().endswith(":"):
            current_character = line.strip()
            if current_character not in characters:
                characters[current_character] = {
                    "name": current_character,
                    "dialogue_lines": 0,
                    "scenes": [],
                }
            characters[current_character]["scenes"].append(len(scenes) + 1)
            current_characters.add(current_character)
        elif dialogue_pattern.match(line) and current_character:
            characters[current_character]["dialogue_lines"] += 1
            for other_character in current_characters:
                if other_character != current_character:
                    if current_character not in dialogue_interactions:
                        dialogue_interactions[current_character] = {}
                    if other_character not in dialogue_interactions[current_character]:
                        dialogue_interactions[current_character][other_character] = 0
                    dialogue_interactions[current_character][other_character] += 1

    # Append the last scene
    if current_scene:
        current_scene["characters"] = list(current_characters)
        scenes.append(current_scene)

    # Convert characters dict to list
    characters_list = [v for v in characters.values()]

    return {
        "screenplay": {
            "title": "Reservoir Dogs",
            "characters": characters_list,
            "scenes": scenes,
            "dialogue_interactions": dialogue_interactions,
        }
    }


screenplay_data = parse_screenplay(script_content)

# Save the structured data to a JSON file
filename = "Reservoir-Dogs-structured.json"
with open(filename, "w") as f:
    json.dump(screenplay_data, f, indent=2)

print(f"Data saved to {filename}")
