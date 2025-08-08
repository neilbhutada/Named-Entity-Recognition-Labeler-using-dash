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

The easiest way to get started is to run the working demo:

```bash
# Clone this repository
git clone https://github.com/yourusername/dash-ner-labeler.git
cd dash-ner-labeler

# Install Python dependencies
pip install dash

# Run the demo
python working_demo.py
```

Then visit http://localhost:8051 to see the interactive NER labeler in action!

### How to Use the Demo

1. **Select text** with your mouse in the gray text area
2. **Click a label button** (PERSON, ORGANIZATION, LOCATION, MISCELLANEOUS)
3. **View labeled entities** in the list below
4. **Remove entities** by clicking the red "×" button on any entity card
5. **Export JSON** data for ML training

### Demo Features

- ✅ Interactive text selection with mouse
- ✅ Multiple entity types with color coding
- ✅ Add and remove entity labels
- ✅ JSON export for machine learning
- ✅ Real-time visual feedback

## Implementation Status

🚧 **Current Version**: This project includes a fully functional NER labeler implemented using Dash's clientside callbacks (`working_demo.py`).

📋 **Future Development**: The React component foundation is in place for creating a proper Dash component package, but requires additional integration work.

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
# Interactive demo with full NER functionality
python working_demo.py
```

Visit http://localhost:8051 to see the working NER labeler.

The demo includes helpful startup instructions and runs a fully interactive NER labeling interface.

### Project Structure

```
dash-ner-labeler/
├── working_demo.py            # 🎯 Main demo - fully functional NER labeler
├── src/lib/                   # React component source (for future development)
│   ├── components/
│   │   ├── NERLabeler.react.js # React component foundation
│   │   └── NERLabeler.css      # Component styling
│   └── index.js               # Component entry point
├── dash_ner_labeler/          # Python package structure
│   ├── __init__.py
│   ├── NERLabeler.py          # Python component wrapper
│   └── metadata.json          # Component metadata
├── build/                     # Built JavaScript files
├── package.json               # Node.js dependencies and scripts
├── webpack.config.js          # Build configuration
├── setup.py                   # Python package setup
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore patterns
└── README.md                  # This documentation
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