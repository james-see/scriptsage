import os
import argparse
import requests
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
import re

# Define directories
home_dir = os.path.expanduser("~")
screenplay_dir = os.path.join(home_dir, ".scriptsage", "screenplays")
viz_dir = os.path.join(home_dir, ".scriptsage", "viz")

# Create directories if they don't exist
os.makedirs(screenplay_dir, exist_ok=True)
os.makedirs(viz_dir, exist_ok=True)

def scrape_screenplay(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    script_content = soup.find('td', class_='scrtext').find('pre').get_text(separator='\n')
    title = soup.find('td', align='center').find('h1').get_text()  # Extract title from the <h1> tag
    return title, script_content

def parse_screenplay(script, title):
    scenes = []
    characters = {}
    current_scene = None
    current_characters = set()
    dialogue_interactions = {}

    lines = script.split('\n')
    scene_pattern = re.compile(r'^\s*(INT\.|EXT\.)')
    character_pattern = re.compile(r'^[A-Z][A-Z\s]+$')
    dialogue_pattern = re.compile(r'^\s{10,}')

    current_character = None

    def is_valid_character(name):
        if 'CU' in name or '-' in name or ':' in name or 'POV' in name or 'ON' in name or 'FRAME' in name or 'SHOT' in name or 'BANG' in name or title.upper() in name:
            return False
        return True

    for line in lines:
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
        elif character_pattern.match(line.strip()) and not line.strip().endswith(':'):
            current_character = line.strip()
            if is_valid_character(current_character):
                if current_character not in characters:
                    characters[current_character] = {'name': current_character, 'dialogue_lines': 0, 'scenes': []}
                characters[current_character]['scenes'].append(len(scenes) + 1)
                current_characters.add(current_character)
        elif dialogue_pattern.match(line) and current_character:
            if is_valid_character(current_character):
                characters[current_character]['dialogue_lines'] += 1
                for other_character in current_characters:
                    if other_character != current_character:
                        if current_character not in dialogue_interactions:
                            dialogue_interactions[current_character] = {}
                        if other_character not in dialogue_interactions[current_character]:
                            dialogue_interactions[current_character][other_character] = 0
                        dialogue_interactions[current_character][other_character] += 1

    if current_scene:
        current_scene['characters'] = list(current_characters)
        scenes.append(current_scene)

    characters_list = [v for v in characters.values()]

    return {
        'screenplay': {
            'title': title,
            'characters': characters_list,
            'scenes': scenes,
            'dialogue_interactions': dialogue_interactions
        }
    }

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def plot_dialogue_distribution(characters, output_path):
    character_names = [char['name'] for char in characters]
    dialogue_lines = [char['dialogue_lines'] for char in characters]

    plt.figure(figsize=(14, 8))
    plt.barh(character_names, dialogue_lines, color='skyblue')
    plt.xlabel('Number of Dialogue Lines')
    plt.ylabel('Characters')
    plt.title('Dialogue Distribution')
    plt.gca().invert_yaxis()
    plt.savefig(output_path)
    plt.close()

def plot_character_interaction(data, output_path):
    G = nx.Graph()

    for char in data['screenplay']['characters']:
        G.add_node(char['name'], size=char['dialogue_lines'])

    for scene in data['screenplay']['scenes']:
        for i in range(len(scene['characters'])):
            for j in range(i + 1, len(scene['characters'])):
                char1 = scene['characters'][i]
                char2 = scene['characters'][j]
                if G.has_edge(char1, char2):
                    G[char1][char2]['weight'] += 1
                else:
                    G.add_edge(char1, char2, weight=1)

    pos = nx.spring_layout(G)
    sizes = [nx.get_node_attributes(G, 'size')[node] * 10 for node in G.nodes()]
    weights = [G[u][v]['weight'] for u, v in G.edges()]

    plt.figure(figsize=(14, 10))
    nx.draw(G, pos, with_labels=True, node_size=sizes, width=weights, node_color='skyblue', edge_color='gray', font_size=10)
    plt.title('Character Interaction Network')
    plt.savefig(output_path)
    plt.close()

def plot_heatmap(data, output_path):
    characters = data['screenplay']['characters']
    dialogue_interactions = data['screenplay']['dialogue_interactions']

    # Create a list of character names
    character_names = [char['name'] for char in characters]

    # Create a DataFrame for the interaction matrix
    interaction_matrix = pd.DataFrame(0, index=character_names, columns=character_names)

    # Fill the interaction matrix
    for char1, interactions in dialogue_interactions.items():
        for char2, count in interactions.items():
            interaction_matrix.at[char1, char2] = count

    # Apply logarithmic scale to improve color variation
    interaction_matrix = interaction_matrix.applymap(lambda x: np.log1p(x))

    # Create the heatmap
    plt.figure(figsize=(14, 12))
    sns.heatmap(interaction_matrix, cmap='coolwarm', linewidths=.5)
    plt.title('Character Interaction Frequency')
    plt.xlabel('Character')
    plt.ylabel('Character')
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="ScriptSage CLI")
    parser.add_argument('url', type=str, help='URL of the screenplay to scrape')
    args = parser.parse_args()

    title, script_content = scrape_screenplay(args.url)
    screenplay_data = parse_screenplay(script_content, title)

    # Sanitize title for filenames
    sanitized_title = re.sub(r'\W+', '_', title)

    screenplay_filename = os.path.join(screenplay_dir, f'{sanitized_title}.json')
    save_json(screenplay_data, screenplay_filename)

    plot_dialogue_distribution(screenplay_data['screenplay']['characters'], os.path.join(viz_dir, f'{sanitized_title}_dialogue_distribution.png'))
    plot_character_interaction(screenplay_data, os.path.join(viz_dir, f'{sanitized_title}_character_interaction.png'))
    plot_heatmap(screenplay_data, os.path.join(viz_dir, f'{sanitized_title}_character_interaction_heatmap.png'))

if __name__ == "__main__":
    main()
