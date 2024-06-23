import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load the screenplay data
with open('Reservoir-Dogs-structured.json', 'r') as f:
    data = json.load(f)

characters = data['screenplay']['characters']
dialogue_interactions = data['screenplay']['dialogue_interactions']

# List of known characters in "Reservoir Dogs"
known_characters = [
    'MR. WHITE', 'MR. ORANGE', 'MR. BLONDE', 'MR. PINK', 'MR. BLUE', 'MR. BROWN',
    'JOE', 'NICE GUY EDDIE', 'WAITRESS', 'TEDDY', 'VIC', 'EDDIE', 'COP', 'JEFFREY', 
    'HOLDAWAY', 'FREDDY', 'JODIE'
]

# List of scene directions and specific entries to exclude
scene_directions = [
    'INT', 'EXT', 'CU', 'ECU', 'MEDIUM', 'SHOT', 'ANGLE', 'SLOW', 'MOTION',
    'FLASH', 'FRAME', 'LOW', 'HIGH', 'ON', 'TWO', 'OVER', 'FOUR', 'END',
    'FREEZE FRAME', 'FRAME ON HOLDAWAY', 'R E S E R V O I R  D O G S', 'FULL SCENE', 
    'BANG', 'RESERVOIR DOGS'
]

# Function to check if a name is a scene direction, cast name, or unwanted entry
def is_valid_character(name):
    invalid_chars = ['-', '.', ':']
    if any(char in name for char in invalid_chars):
        return False
    if any(name.startswith(direction) for direction in scene_directions):
        return False
    if name not in known_characters and len(name.split()) > 1:  # Assuming proper names have more than one word
        return False
    return True

# Function to merge interactions for duplicated characters
def merge_interactions(interactions, char1, char2):
    if char1 in interactions:
        if char2 in interactions:
            for key, value in interactions[char2].items():
                if key in interactions[char1]:
                    interactions[char1][key] += value
                else:
                    interactions[char1][key] = value
            del interactions[char2]
        for key in interactions:
            if char2 in interactions[key]:
                if char1 in interactions[key]:
                    interactions[key][char1] += interactions[key][char2]
                else:
                    interactions[key][char1] = interactions[key][char2]
                del interactions[key][char2]

# Merge "EDDIE" and "NICE GUY EDDIE"
merge_interactions(dialogue_interactions, 'NICE GUY EDDIE', 'EDDIE')

# Filter out non-character entries and merge any remaining duplicates in character list
valid_characters = [char['name'] for char in characters if is_valid_character(char['name'])]
if 'EDDIE' in valid_characters:
    valid_characters.remove('EDDIE')

# Create a DataFrame for the interaction matrix with valid characters only
interaction_matrix = pd.DataFrame(index=valid_characters, columns=valid_characters).fillna(0)

# Fill the interaction matrix
for char1, interactions in dialogue_interactions.items():
    if is_valid_character(char1):
        for char2, count in interactions.items():
            if is_valid_character(char2):
                interaction_matrix.at[char1, char2] = count

# Apply logarithmic scale to improve color variation
interaction_matrix = interaction_matrix.applymap(lambda x: np.log1p(x))

# Create the heatmap
plt.figure(figsize=(14, 12))
sns.heatmap(interaction_matrix, cmap='coolwarm', linewidths=.5)
plt.title('Character Interaction Frequency in Reservoir Dogs')
plt.xlabel('Character')
plt.ylabel('Character')
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('Reservoir-Dogs-Character-Interaction-Heatmap.png')
plt.show()
