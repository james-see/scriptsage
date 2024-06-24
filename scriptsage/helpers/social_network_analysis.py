import networkx as nx
from pyvis.network import Network
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

def plot_social_network(data, output_path):
    G = nx.Graph()

    # Add nodes with dialogue lines as node size
    for char in data['screenplay']['characters']:
        G.add_node(char['name'], size=char['dialogue_lines'])

    # Add edges based on character interactions in scenes
    for scene in data['screenplay']['scenes']:
        for i in range(len(scene['characters'])):
            for j in range(i + 1, len(scene['characters'])):
                char1 = scene['characters'][i]
                char2 = scene['characters'][j]
                if G.has_edge(char1, char2):
                    G[char1][char2]['weight'] += 1
                else:
                    G.add_edge(char1, char2, weight=1)

    # Calculate centrality measures
    eigenvector_centrality = nx.eigenvector_centrality(G)
    centrality = nx.degree_centrality(G)

    # Create a PyVis network
    net = Network(notebook=False, height="1000px", width="1000px")

    # Add nodes to the PyVis network
    for node in G.nodes():
        net.add_node(node, size=max(5, G.nodes[node]['size'] / 5), title=f"Eigenvector Centrality: {eigenvector_centrality[node]:.4f}")

    # Add edges to the PyVis network
    for edge in G.edges():
        net.add_edge(edge[0], edge[1], value=G.edges[edge]['weight'])

    # Highlight top 3 central characters
    top_3_central_chars = sorted(centrality, key=centrality.get, reverse=True)[:3]
    for char in top_3_central_chars:
        net.get_node(char)['color'] = 'red'

    # Generate the network visualization
    html_path = output_path.replace('.png', '.html')
    net.write_html(html_path, notebook=False)  # Use write_html instead of show

    # Convert HTML to PNG using Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get('file://' + html_path)
    time.sleep(2)  # Allow some time for the page to render

    # Set the window size
    driver.set_window_size(1200, 1200)  # Increase the window size for better layout
    driver.save_screenshot(output_path)
    driver.quit()

# Example usage:
# data = load_your_data()  # Replace with your data loading method
# plot_social_network(data, '/mnt/data/social_network.png')
