# Dash NER Labeler

A custom Plotly Dash component for Named Entity Recognition (NER) text labeling. This component allows users to manually highlight and label text segments for machine learning tasks.

## Features

- **Interactive Text Selection**: Users can select text with their mouse to highlight entities
- **Customizable Labels**: Define your own entity types (PERSON, ORGANIZATION, LOCATION, etc.)
- **Visual Highlighting**: Different colors for different entity types
- **Entity Management**: Add, view, and remove labeled entities
- **Export Ready**: Get labeled entities as structured data for ML training

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dash-ner-labeler.git
cd dash-ner-labeler

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies and build the component
npm install
npm run build

# Install the Python package
pip install -e .
```

## Quick Start

```python
import dash
from dash import html, callback, Input, Output
from dash_ner_labeler import NERLabeler

app = dash.Dash(__name__)

app.layout = html.Div([
    NERLabeler(
        id='ner-labeler',
        text="Apple Inc. is based in Cupertino. Tim Cook is the CEO.",
        labelTypes=['PERSON', 'ORGANIZATION', 'LOCATION'],
        entities=[]
    ),
    html.Div(id='output')
])

@callback(
    Output('output', 'children'),
    Input('ner-labeler', 'entities')
)
def display_entities(entities):
    if not entities:
        return "No entities labeled yet."
    
    return html.Div([
        html.H3("Labeled Entities:"),
        html.Ul([
            html.Li(f"{entity['text']} ({entity['label']})")
            for entity in entities
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
```

## Usage

### Basic Component

```python
from dash_ner_labeler import NERLabeler

NERLabeler(
    id='my-ner-labeler',
    text="Your text to be labeled here...",
    labelTypes=['PERSON', 'ORG', 'LOCATION', 'MISC'],
    entities=[]  # Pre-existing entities (optional)
)
```

### Component Properties

- **id** (string, optional): Component identifier for callbacks
- **text** (string, required): The text to be labeled
- **entities** (list, optional): Pre-existing labeled entities
- **labelTypes** (list, optional): Available label types for entities

### Entity Format

Each entity in the `entities` list should have this structure:

```python
{
    "id": "unique_identifier",
    "text": "entity_text",
    "label": "ENTITY_TYPE", 
    "start": 0,  # Start character position
    "end": 10    # End character position
}
```

## Development

### Building the Component

```bash
# Install dependencies
npm install

# Build for development (with watch mode)
npm run build:watch

# Build for production
npm run build
```

### Running the Demo

```bash
python demo_app.py
```

Visit http://localhost:8050 to see the demo application.

### Project Structure

```
dash-ner-labeler/
├── src/lib/                    # React source code
│   ├── components/
│   │   ├── NERLabeler.react.js # Main React component
│   │   └── NERLabeler.css      # Component styles
│   └── index.js               # Entry point
├── dash_ner_labeler/          # Python package
│   ├── __init__.py
│   ├── NERLabeler.py          # Python wrapper
│   └── _imports_.py
├── demo_app.py                # Demo application
├── package.json               # Node.js configuration
├── webpack.config.js          # Build configuration
└── setup.py                   # Python package setup
```

## Customization

### Custom Label Types

You can define your own entity types:

```python
NERLabeler(
    text="Your text here...",
    labelTypes=['PRODUCT', 'COMPANY', 'TECHNOLOGY', 'CURRENCY']
)
```

### Custom Styling

The component uses CSS classes that can be overridden:

- `.ner-labeler-container` - Main container
- `.ner-text-container` - Text display area
- `.ner-entity` - Highlighted entity spans
- `.ner-person`, `.ner-organization`, etc. - Entity type specific styles

## Use Cases

- **Training Data Creation**: Generate labeled datasets for NER models
- **Data Annotation**: Manually annotate documents for analysis
- **Content Analysis**: Identify and categorize entities in text
- **Document Processing**: Extract structured information from unstructured text

## Browser Support

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.