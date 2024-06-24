# ScriptSage

ScriptSage is a tool designed to parse and evaluate movie scripts. It provides functionalities to scrape screenplay data, structure it into a JSON format, and visualize character interactions and dialogue distributions.

## Features

- **Screenplay Scraping**: Extract screenplay content from the web.
- **Data Structuring**: Convert screenplay content into structured JSON format.
- **Visualization**: Generate visualizations for dialogue distribution and character interactions.

## Example Output Conversation Heatmap

![heat-map-cleaned-up](https://github.com/james-see/scriptsage/assets/616585/adcab939-efc6-4cf9-ad96-6d6e6645b6de)

## Installation

Ensure you have Python 3.11 installed. You can install the required dependencies using Poetry:

```sh
poetry install
```

## Usage

### Command Line Interface (CLI)

ScriptSage provides a command line interface to scrape, parse, and visualize movie scripts. 

To use the CLI, run the following command:

```sh
python scriptsage_cli.py <script_url> [--metric]
```

The `--metric` flag is optional. When included, it will display additional metrics about the screenplay.

For example, to scrape the screenplay of "Reservoir Dogs" and save it as a structured JSON file:

```sh
python scriptsage_cli.py https://imsdb.com/scripts/Reservoir-Dogs.html
```

To scrape the screenplay and display additional metrics:

```sh
python scriptsage_cli.py https://imsdb.com/scripts/Reservoir-Dogs.html --metric
```

This will perform the following actions:
1. Scrape the screenplay content from the provided URL.
2. Parse the screenplay content to extract scenes, characters, and dialogue interactions.
3. Save the structured data as a JSON file in `~/.scriptsage/screenplays/`.
4. Generate and save visualizations for dialogue distribution and character interactions in `~/.scriptsage/viz/`.
5. If the `--metric` flag is used, display additional metrics such as total word count, scene count, character count, and top words used in the screenplay.

### Scraping Screenplay

To scrape the screenplay of "Reservoir Dogs" and save it as a structured JSON file:

```python:scriptsage/helpers/scraper.py
startLine: 1
endLine: 14
```

### Parsing Screenplay

To parse the screenplay content and save it to a JSON file:

```python:scriptsage/helpers/parse-dialogues.py
startLine: 76
endLine: 83
```

### Generating Visualizations

To generate visualizations for dialogue distribution and character interactions:

```python:scriptsage/helpers/generate-viz.py
startLine: 1
endLine: 52
```

## Project Structure

- **scriptsage/helpers/scraper.py**: Contains the code to scrape screenplay content from the web.
- **scriptsage/helpers/parse-dialogues.py**: Contains the code to parse the screenplay content and save it as a structured JSON file.
- **scriptsage/helpers/generate-viz.py**: Contains the code to generate visualizations for dialogue distribution and character interactions.
- **scriptsage/helpers/Reservoir-Dogs-structured.json**: Example of a structured JSON file generated from the screenplay.
- **scriptsage/helpers/Reservoir-Dogs.html**: Example of the raw HTML content of the screenplay.

## Dependencies

The project uses the following dependencies:

- **requests**: For making HTTP requests to fetch screenplay content.
- **beautifulsoup4**: For parsing HTML content.
- **pandas**: For data manipulation and analysis.
- **matplotlib**: For creating visualizations.
- **seaborn**: For creating statistical visualizations.
- **numpy**: For numerical operations.
- **json**: For handling JSON data.
- **poetry**: For dependency management and packaging.

## License

This project is licensed under the MIT License.
