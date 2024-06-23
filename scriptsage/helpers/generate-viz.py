import json
import matplotlib.pyplot as plt
import networkx as nx

# Load the screenplay data
with open('Reservoir-Dogs-structured.json', 'r') as f:
    data = json.load(f)

characters = data['screenplay']['characters']

# Create a bar chart for dialogue lines
def plot_dialogue_distribution(characters):
    character_names = [char['name'] for char in characters]
    dialogue_lines = [char['dialogue_lines'] for char in characters]

    plt.figure(figsize=(14, 8))
    plt.barh(character_names, dialogue_lines, color='skyblue')
    plt.xlabel('Number of Dialogue Lines')
    plt.ylabel('Characters')
    plt.title('Dialogue Distribution in Reservoir Dogs')
    plt.gca().invert_yaxis()
    plt.show()

plot_dialogue_distribution(characters)

# Create a character interaction network
def plot_character_interaction(characters):
    G = nx.Graph()

    # Add nodes
    for char in characters:
        G.add_node(char['name'], size=char['dialogue_lines'])

    # Add edges
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
    plt.title('Character Interaction Network in Reservoir Dogs')
    plt.show()

plot_character_interaction(characters)
