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
from helpers.social_network_analysis import plot_social_network
from collections import Counter
import nltk
from nltk.corpus import stopwords

# Define directories
home_dir = os.path.expanduser("~")
screenplay_dir = os.path.join(home_dir, ".scriptsage", "screenplays")
viz_dir = os.path.join(home_dir, ".scriptsage", "viz")

# Create directories if they don't exist
os.makedirs(screenplay_dir, exist_ok=True)
os.makedirs(viz_dir, exist_ok=True)


def scrape_screenplay(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    script_content = (
        soup.find("td", class_="scrtext").find("pre").get_text(separator="\n")
    )
    title = (
        soup.find("td", align="center").find("h1").get_text()
    )  # Extract title from the <h1> tag
    return title, script_content


def parse_screenplay(script, title):
    scenes = []
    characters = {}
    current_scene = None
    current_characters = set()
    dialogue_interactions = {}
    current_character = None
    global_characters = []
    global_dialogues = []

    lines = script.split("\n")
    scene_pattern = re.compile(r"^\s*(INT\.|EXT\.)")
    character_pattern = re.compile(r'\s{20,}([A-Z][A-Z\s.]+)(?:\s*\(.*\))?')
    dialogue_pattern = re.compile(r'^\s{10,}')
    
    def normalize_character_name(name):
        name = name.strip()
        name_corrections = {
            "EDDIE": "EDDIE (NICE GUY EDDIE)",
            "NICE GUY EDDIE": "EDDIE (NICE GUY EDDIE)",
            "MR. WRITE": "MR. WHITE",
            "YOUNG WOMAN": "HONEY BUNNY",
            "YOUNG MAN": "PUMPKIN"
            # Add any other corrections here
        }
        return name_corrections.get(name, name)

    def is_valid_character(name):
        invalid_names = [
            'CUT TO', 'FADE IN', 'FADE OUT', 'DISSOLVE TO', 'JEAN LUC GODDARD',
            'TITLE SEQUENCE', 'END CREDITS', 'THE END', 'SUPERIMPOSE', 'SUPER',
            'ANGLE ON', 'CLOSE ON', 'CLOSEUP', 'CLOSE UP', 'CONTINUED', 'CAMERA',
            'FADE TO BLACK', 'BACK TO SCENE', 'MONTAGE', 'FLASHBACK', 'INTERCUT',
            'TIME CUT', 'SMASH CUT', 'MATCH CUT', 'JUMP CUT', 'FREEZE FRAME',
            'SLOW MOTION', 'FAST MOTION', 'SPLIT SCREEN', 'STOCK SHOT', 'ANGLE',
            'POV', 'POINT OF VIEW', 'PAN', 'ZOOM', 'TRACKING SHOT', 'DOLLY',
            'CRANE SHOT', 'AERIAL SHOT', 'ESTABLISHING SHOT', 'WIDE SHOT',
            'MEDIUM SHOT', 'LONG SHOT', 'TWO SHOT', 'OVER THE SHOULDER', 'MR. PINK                      MR. WHITE', 'R E S E R V O I R   D O G S', 'RESERVOIR DOGS',
            'MR. WHITE   MR. PINK   EDDIE', 'LAWRENCE TIERNEY', 'JEAN PIERRE MELVILLE',
            'CHOW YUEN FAT', 'ROGER CORMAN', 'TIMOTHY CAREY', 'ANDRE D', 'LIONEL WHITE',
            'BACK TO', 'POLICE FORCE'
        ]
        return name and len(name) > 1 and name not in invalid_names

    # Skip lines until the first scene direction
    start_index = 0
    for i, line in enumerate(lines):
        if scene_pattern.match(line):
            start_index = i
            break

    # Process lines starting from the first scene direction
    for line in lines[start_index:]:
        # Identify new scenes
        if scene_pattern.match(line):
            if current_scene:
                current_scene["characters"] = list(set(map(normalize_character_name, current_characters)))
                scenes.append(current_scene)
            current_scene = {
                "scene_number": len(scenes) + 1,
                "location": line.strip(),
                "characters": [],
            }
            current_characters = set()
            current_character = None
        # Identify characters and their dialogues
        else:
            character_matches = character_pattern.findall(line)
            if character_matches:
                for match in character_matches:
                    current_character = normalize_character_name(match)
                    if is_valid_character(current_character):
                        if current_character not in characters:
                            characters[current_character] = {
                                "name": current_character,
                                "dialogue_lines": 0,
                                "scenes": [],
                            }
                        characters[current_character]["scenes"].append(len(scenes) + 1)
                        current_characters.add(current_character)
                        if current_character not in global_characters:
                            global_characters.append(current_character)
            
            elif dialogue_pattern.match(line) and current_character:
                if is_valid_character(current_character):
                    characters[current_character]["dialogue_lines"] += 1
                    global_dialogues.append(line.strip())
                    for other_character in current_characters:
                        if other_character != current_character:
                            if current_character not in dialogue_interactions:
                                dialogue_interactions[current_character] = {}
                            if other_character not in dialogue_interactions[current_character]:
                                dialogue_interactions[current_character][other_character] = 0
                            dialogue_interactions[current_character][other_character] += 1

    if current_scene:
        current_scene["characters"] = list(set(map(normalize_character_name, current_characters)))
        scenes.append(current_scene)

    # Normalize global_characters
    global_characters = [normalize_character_name(char) for char in global_characters]

    # Combine dialogues for EDDIE and NICE GUY EDDIE
    combined_dialogues = []
    eddie_dialogue = ""
    for char, dialogue in zip(global_characters, global_dialogues):
        if char == "EDDIE (NICE GUY EDDIE)":
            eddie_dialogue += dialogue + " "
        else:
            combined_dialogues.append(dialogue)
    
    if eddie_dialogue:
        combined_dialogues.append(eddie_dialogue.strip())
        global_characters = [char for char in global_characters if char != "EDDIE (NICE GUY EDDIE)"]
        global_characters.append("EDDIE (NICE GUY EDDIE)")

    print(f"Total characters found: {len(characters)}")  # Debug print
    print(f"Total scenes found: {len(scenes)}")  # Debug print
    print(f"Dialogue interactions: {dialogue_interactions}")  # Debug print

    return {
        "screenplay": {
            "title": title,
            "characters": list(characters.values()),
            "scenes": scenes,
            "dialogue_interactions": dialogue_interactions,
            "global_characters": global_characters,
            "global_dialogues": combined_dialogues,
        }
    }


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def plot_dialogue_distribution(screenplay_data, output_path):
    characters = screenplay_data["screenplay"]["characters"]
    
    # Ensure characters is a list of dictionaries
    if not isinstance(characters, list):
        print("Error: characters data is not in the expected format")
        return

    character_names = []
    dialogue_lines = []

    for char in characters:
        if isinstance(char, dict) and "name" in char and "dialogue_lines" in char:
            character_names.append(char["name"])
            dialogue_lines.append(char["dialogue_lines"])
        else:
            print(f"Skipping invalid character data: {char}")

    if not character_names or not dialogue_lines:
        print("No valid character data found for dialogue distribution")
        return

    # Sort characters by dialogue lines in descending order
    sorted_chars = sorted(zip(character_names, dialogue_lines), key=lambda x: x[1], reverse=True)
    character_names, dialogue_lines = zip(*sorted_chars)

    plt.figure(figsize=(14, 8))
    plt.barh(character_names, dialogue_lines, color="skyblue")
    plt.xlabel("Number of Dialogue Lines")
    plt.ylabel("Characters")
    plt.title("Dialogue Distribution")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_character_interaction(data, output_path):
    G = nx.Graph()

    for char in data["screenplay"]["characters"]:
        G.add_node(char["name"], size=char["dialogue_lines"])

    for scene in data["screenplay"]["scenes"]:
        for i in range(len(scene["characters"])):
            for j in range(i + 1, len(scene["characters"])):
                char1 = scene["characters"][i]
                char2 = scene["characters"][j]
                if G.has_edge(char1, char2):
                    G[char1][char2]["weight"] += 1
                else:
                    G.add_edge(char1, char2, weight=1)

    pos = nx.spring_layout(G)
    sizes = [nx.get_node_attributes(G, "size")[node] * 10 for node in G.nodes()]
    weights = [G[u][v]["weight"] for u, v in G.edges()]

    plt.figure(figsize=(14, 10))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=sizes,
        width=weights,
        node_color="skyblue",
        edge_color="gray",
        font_size=10,
    )
    plt.title("Character Interaction Network")
    plt.savefig(output_path)
    plt.close()


def plot_heatmap(data, output_path):
    characters = data["screenplay"]["characters"]
    dialogue_interactions = data["screenplay"]["dialogue_interactions"]

    # Create a list of character names
    character_names = [char["name"] for char in characters]

    # Create a DataFrame for the interaction matrix
    interaction_matrix = pd.DataFrame(0, index=character_names, columns=character_names)

    # Fill the interaction matrix
    for char1, interactions in dialogue_interactions.items():
        for char2, count in interactions.items():
            interaction_matrix.at[char1, char2] = count

    # Check if the matrix is empty
    if interaction_matrix.empty or interaction_matrix.sum().sum() == 0:
        print("No character interactions found. Skipping heatmap generation.")
        return

    # Apply logarithmic scale to improve color variation
    interaction_matrix = interaction_matrix.apply(lambda x: np.log1p(x))

    # Create the heatmap
    plt.figure(figsize=(14, 12))
    sns.heatmap(interaction_matrix, cmap="coolwarm", linewidths=0.5)
    plt.title("Character Interaction Frequency")
    plt.xlabel("Character")
    plt.ylabel("Character")
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def get_metrics(screenplay_data):
    script_content = screenplay_data['screenplay']['script_content']
    words = script_content.lower().split()
    word_count = len(words)
    scene_count = len(screenplay_data['screenplay']['scenes'])
    character_count = len(screenplay_data['screenplay']['characters'])
    character_names = [char['name'] for char in screenplay_data['screenplay']['characters']]

    # Download stopwords if not already downloaded
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))

    # Add additional stopwords
    additional_stopwords = {
        'i\'m', 'got', 'he\'s', 'get', 'gonna', 'are', 'it\'s', 'don\'t', 'that\'s', 'you\'re', 
        'ain\'t', 'can\'t', 'won\'t', 'gotta', 'wanna', 'it.', '-', '--', '...', ':', ';', ',', '.',
        '?', '!', '(', ')', '[', ']', '{', '}', '"', "'", '`'
    }
    stop_words.update(additional_stopwords)

    # Top 50 most used words (excluding stopwords and non-word characters)
    word_freq = Counter(word for word in words if word not in stop_words and word.isalnum())
    top_50_words = word_freq.most_common(50)

    # Update character_words using global_characters and global_dialogues
    character_words = {char: [] for char in screenplay_data['screenplay']['global_characters']}
    for char, dialogue in zip(screenplay_data['screenplay']['global_characters'], screenplay_data['screenplay']['global_dialogues']):
        words = dialogue.lower().split()
        # Remove the character names from the dialogue
        words = [word for word in words if word not in [name.lower().replace('.', '') for name in character_names]]
        character_words[char].extend(words)

    # Top 5 words per character
    top_character_words = {}
    for char, words in character_words.items():
        char_word_freq = Counter(word for word in words if word not in stop_words and word.isalnum())
        top_character_words[char] = char_word_freq.most_common(5)

    return {
        'word_count': word_count,
        'scene_count': scene_count,
        'character_count': character_count,
        'character_names': character_names,
        'top_50_words': top_50_words,
        'top_character_words': top_character_words
    }

def print_metrics(metrics):
    print(f"Total word count: {metrics['word_count']}")
    print(f"Total scene count: {metrics['scene_count']}")
    print(f"Total character count: {metrics['character_count']}")
    print(f"Characters: {', '.join(metrics['character_names'])}")
    print("\nTop 50 most used words:")
    for word, count in metrics['top_50_words']:
        print(f"{word}: {count}")
    print("\nTop 5 words per character:")
    for char, words in metrics['top_character_words'].items():
        print(f"{char}: {', '.join(f'{word}({count})' for word, count in words)}")

def main():
    parser = argparse.ArgumentParser(description="ScriptSage CLI")
    parser.add_argument("url", type=str, help="URL of the screenplay to scrape")
    parser.add_argument("--metrics", action="store_true", help="Print screenplay metrics")
    args = parser.parse_args()

    title, script_content = scrape_screenplay(args.url)
    screenplay_data = parse_screenplay(script_content, title)
    screenplay_data['screenplay']['script_content'] = script_content  # Add full script content to the data

    # Sanitize title for filenames
    sanitized_title = re.sub(r"\W+", "_", title)

    screenplay_filename = os.path.join(screenplay_dir, f"{sanitized_title}.json")
    save_json(screenplay_data, screenplay_filename)

    # Generate visualizations
    visualizations = [
        (plot_dialogue_distribution, "dialogue_distribution"),
        (plot_character_interaction, "character_interaction"),
        (plot_heatmap, "character_interaction_heatmap"),
        (plot_social_network, "social_network")
    ]

    for plot_func, viz_name in visualizations:
        try:
            plot_func(
                screenplay_data,
                os.path.join(viz_dir, f"{sanitized_title}_{viz_name}.png"),
            )
        except Exception as e:
            print(f"Failed to generate {viz_name}: {str(e)}")

    if args.metrics:
        metrics = get_metrics(screenplay_data)
        print_metrics(metrics)

    print(f"Screenplay data saved to: {screenplay_filename}")
    plot_dialogue_distribution(
        screenplay_data,
        os.path.join(viz_dir, f"{sanitized_title}_dialogue_distribution.png"),
    )
    plot_character_interaction(
        screenplay_data,
        os.path.join(viz_dir, f"{sanitized_title}_character_interaction.png"),
    )
    plot_heatmap(
        screenplay_data,
        os.path.join(viz_dir, f"{sanitized_title}_character_interaction_heatmap.png"),
    )
    plot_social_network(
        screenplay_data, os.path.join(viz_dir, f"{sanitized_title}_social_network.png")
    )

    if args.metrics:
        metrics = get_metrics(screenplay_data)
        print_metrics(metrics)


if __name__ == "__main__":
    main()

