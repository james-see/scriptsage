import requests
from bs4 import BeautifulSoup

# URL of the screenplay
url = 'https://imsdb.com/scripts/Reservoir-Dogs.html'

# Get the page content
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the main content of the screenplay
script_content = soup.find('td', class_='scrtext').find('pre').get_text(separator='\n')

import re

def parse_screenplay(script):
    scenes = []
    characters = {}
    current_scene = None
    current_characters = set()

    lines = script.split('\n')
    scene_pattern = re.compile(r'^\s*(INT\.|EXT\.)')
    character_pattern = re.compile(r'^[A-Z][A-Z\s]+$')

    for line in lines:
        # Identify new scenes
        if scene_pattern.match(line):
            if current_scene:
                current_scene['characters'] = list(current_characters)
                scenes.append(current_scene)
            current_scene = {
                'scene_number': len(scenes) + 1,
                'location': line.strip(),
                'characters': []
            }
            current_characters = set()
        # Identify characters and their dialogues
        elif character_pattern.match(line.strip()) and not line.strip().endswith(':'):
            character = line.strip()
            if character not in characters:
                characters[character] = {'name': character, 'dialogue_lines': 0, 'scenes': []}
            characters[character]['scenes'].append(len(scenes) + 1)
            current_characters.add(character)
            next_line_index = lines.index(line) + 1
            # Count dialogue lines
            while next_line_index < len(lines) and not scene_pattern.match(lines[next_line_index]) and not character_pattern.match(lines[next_line_index].strip()):
                characters[character]['dialogue_lines'] += 1
                next_line_index += 1

    # Append the last scene
    if current_scene:
        current_scene['characters'] = list(current_characters)
        scenes.append(current_scene)

    # Convert characters dict to list
    characters_list = [v for v in characters.values()]

    return {
        'screenplay': {
            'title': 'Reservoir Dogs',
            'characters': characters_list,
            'scenes': scenes
        }
    }

screenplay_data = parse_screenplay(script_content)
import json

print(json.dumps(screenplay_data, indent=2))
filename = 'Reservoir-Dogs-structured.json'
with open(filename, 'w') as f:
    json.dump(screenplay_data, f, indent=2)

print(f"Data saved to {filename}")