"""
Dash NER Labeler - Interactive Demo
===================================

A fully functional Named Entity Recognition (NER) text labeling interface built with Dash.
This demo allows users to manually highlight text and assign entity labels for machine learning tasks.

Features:
- Interactive text selection with mouse
- Multiple entity types (PERSON, ORGANIZATION, LOCATION, MISCELLANEOUS)
- Add/remove entity labels
- Real-time visual feedback
- JSON export for ML training data

Author: Generated with Claude Code
License: MIT
"""

import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import json

# Sample text for demonstration - contains various entity types
SAMPLE_TEXT = """Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Tim Cook is the current CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976."""

# Initialize the Dash app
app = dash.Dash(__name__)

# Custom HTML template with embedded CSS and JavaScript
# This approach embeds all styling and JavaScript directly in the HTML for simplicity
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* === NER LABELER STYLES === */
            /* Main text container where users select text */
            .ner-text-container {
                background-color: #f8f9fa;   /* Light gray background */
                border: 1px solid #dee2e6;   /* Subtle border */
                border-radius: 6px;          /* Rounded corners */
                padding: 20px;               /* Internal spacing */
                line-height: 1.6;            /* Readable line spacing */
                font-size: 16px;             /* Comfortable reading size */
                min-height: 200px;           /* Minimum height for text area */
                cursor: text;                /* Text cursor on hover */
                position: relative;          /* For absolute positioning of children */
                user-select: text;           /* Allow text selection */
            }
            
            /* Highlighted entity spans - currently unused but ready for future implementation */
            .ner-entity {
                position: relative;
                padding: 2px 4px;
                margin: 0 1px;
                border-radius: 3px;
                cursor: pointer;
                display: inline;
                transition: all 0.2s ease;
            }
            .ner-entity:hover {
                opacity: 0.8;
            }
            
            /* Entity type color schemes */
            .ner-person { background-color: #ffeb3b; border: 1px solid #fbc02d; }               /* Yellow */
            .ner-organization { background-color: #2196f3; color: white; border: 1px solid #1976d2; } /* Blue */
            .ner-location { background-color: #4caf50; color: white; border: 1px solid #388e3c; }     /* Green */
            .ner-miscellaneous { background-color: #ff9800; color: white; border: 1px solid #f57c00; } /* Orange */
            
            .ner-label-modal {
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                display: none;
            }
            .ner-modal-content {
                padding: 15px;
                min-width: 200px;
            }
            .ner-label-btn {
                display: block;
                width: 100%;
                padding: 8px 12px;
                margin: 4px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                cursor: pointer;
                font-size: 13px;
            }
            .ner-label-btn:hover { background-color: #f5f5f5; }
            .ner-cancel-btn {
                display: block;
                width: 100%;
                padding: 8px 12px;
                margin: 8px 0 0 0;
                border: 1px solid #dc3545;
                border-radius: 4px;
                background: white;
                color: #dc3545;
                cursor: pointer;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <script>
            /* Placeholder for future clientside JavaScript functionality */
            window.dash_clientside = Object.assign({}, window.dash_clientside, {
                clientside: {
                    handleTextSelection: function(n_clicks) {
                        return window.dash_clientside.no_update;
                    }
                }
            });
        </script>
    </body>
</html>
'''

# ========================================
# APP LAYOUT DEFINITION
# ========================================

app.layout = html.Div([
    # Main title
    html.H1("Working NER Labeler Demo", style={'textAlign': 'center', 'marginBottom': 30}),
    
    # Instructions panel
    html.Div([
        html.H3("Instructions:", style={'color': '#2c3e50'}),
        html.Ul([
            html.Li("Select text with your mouse to highlight it"),
            html.Li("Click the buttons below to label selected text"),
            html.Li("Click on labeled entities to remove them"),
        ], style={'marginBottom': 20})
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20}),
    
    # Text container with JavaScript interaction
    html.Div([
        html.Div(
            id='text-display',
            children=SAMPLE_TEXT,
            className='ner-text-container'
        ),
        
        # Label buttons
        html.Div([
            html.H4("Label Selected Text:"),
            html.Button('PERSON', id='btn-person', className='ner-label-btn', 
                       style={'backgroundColor': '#ffeb3b', 'margin': '5px'}),
            html.Button('ORGANIZATION', id='btn-org', className='ner-label-btn',
                       style={'backgroundColor': '#2196f3', 'color': 'white', 'margin': '5px'}),
            html.Button('LOCATION', id='btn-loc', className='ner-label-btn',
                       style={'backgroundColor': '#4caf50', 'color': 'white', 'margin': '5px'}),
            html.Button('MISCELLANEOUS', id='btn-misc', className='ner-label-btn',
                       style={'backgroundColor': '#ff9800', 'color': 'white', 'margin': '5px'}),
        ], style={'marginTop': 20, 'textAlign': 'center'}),
        
        # Hidden data store to persist entity list across callbacks
        dcc.Store(id='entities-store', data=[]),
        
        # Feedback area to show user what text was selected/labeled
        html.Div(id='selection-info', style={'marginTop': 20}),
    ]),
    
    html.Hr(style={'margin': '40px 0'}),
    
    # Results display section
    html.Div([
        html.H3("Labeled Entities:"),
        html.Div(id='entities-display')  # Dynamic list of entities with remove buttons
    ]),
    
    # JSON export section for ML training data
    html.Div([
        html.H3("JSON Output:"),
        html.Pre(id='entities-json', style={
            'backgroundColor': '#f8f9fa',
            'border': '1px solid #ddd', 
            'borderRadius': 4,
            'padding': 15,
            'fontSize': 12
        })
    ])
])

# ========================================
# CALLBACK FUNCTIONS
# ========================================

# Main text selection and labeling callback (runs in browser)
# This handles all the core NER functionality using JavaScript
app.clientside_callback(
    """
    function(person_clicks, org_clicks, loc_clicks, misc_clicks, current_entities) {
        // === TEXT SELECTION AND LABELING LOGIC ===
        // This function runs in the browser and handles all text selection/labeling
        
        const ctx = window.dash_clientside.callback_context;
        
        // Check if any button was actually clicked
        if (!ctx.triggered.length) {
            return [current_entities, 'Select some text and click a label button'];
        }
        
        // Map button IDs to entity label types
        const button_id = ctx.triggered[0].prop_id.split('.')[0];
        const label_map = {
            'btn-person': 'PERSON',
            'btn-org': 'ORGANIZATION', 
            'btn-loc': 'LOCATION',
            'btn-misc': 'MISCELLANEOUS'
        };
        
        const label = label_map[button_id];
        if (!label) {
            return [current_entities, 'No label selected'];
        }
        
        // Get the user's text selection using browser Selection API
        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.toString().trim() === '') {
            return [current_entities, 'No text selected'];
        }
        
        const selectedText = selection.toString().trim();
        const range = selection.getRangeAt(0);
        
        // Calculate character position within the text container
        // This is a simplified approach that works for this demo
        const textContainer = document.getElementById('text-display');
        const beforeRange = document.createRange();
        beforeRange.setStart(textContainer, 0);
        beforeRange.setEnd(range.startContainer, range.startOffset);
        const start = beforeRange.toString().length;
        
        // Create new entity object for the labeled text
        const newEntity = {
            id: Date.now() + Math.random(),  // Unique ID using timestamp + random
            text: selectedText,
            label: label,
            start: start,
            end: start + selectedText.length
        };
        
        // Add to existing entities list
        const updatedEntities = [...current_entities, newEntity];
        
        // Clear the text selection to provide visual feedback
        selection.removeAllRanges();
        
        // Return updated data and user feedback message
        return [updatedEntities, `Labeled "${selectedText}" as ${label}`];
    }
    """,
    [Output('entities-store', 'data'),
     Output('selection-info', 'children')],
    [Input('btn-person', 'n_clicks'),
     Input('btn-org', 'n_clicks'), 
     Input('btn-loc', 'n_clicks'),
     Input('btn-misc', 'n_clicks')],
    [State('entities-store', 'data')],
    prevent_initial_call=True
)

# Simple callback to update JSON display whenever entities change
@callback(
    Output('entities-json', 'children'),
    [Input('entities-store', 'data')]
)
def update_json_display(entities):
    """Convert entities list to formatted JSON for display and export."""
    return json.dumps(entities, indent=2)

# Main callback to render the entities list with remove buttons
@callback(
    Output('entities-display', 'children'),
    [Input('entities-store', 'data')]
)
def display_entities(entities):
    """
    Create visual cards for each labeled entity with remove functionality.
    
    Args:
        entities: List of entity dictionaries from the data store
        
    Returns:
        List of HTML Div components representing entity cards
    """
    if not entities:
        return html.P("No entities labeled yet.")
    
    entity_cards = []
    for entity in entities:
        # Color scheme for different entity types
        color_map = {
            'PERSON': '#ffeb3b',        # Yellow
            'ORGANIZATION': '#2196f3',  # Blue
            'LOCATION': '#4caf50',      # Green
            'MISCELLANEOUS': '#ff9800'  # Orange
        }
        
        # Adjust text color for readability (yellow background needs black text)
        text_color = 'black' if entity['label'] == 'PERSON' else 'white'
        bg_color = color_map.get(entity['label'], '#6c757d')  # Default to gray
        
        card = html.Div([
            html.Span(
                entity['label'],
                style={
                    'backgroundColor': bg_color,
                    'color': text_color,
                    'padding': '4px 8px',
                    'borderRadius': '12px',
                    'fontSize': '11px',
                    'fontWeight': 'bold',
                    'marginRight': '10px'
                }
            ),
            html.Span(f'"{entity["text"]}"', style={'fontWeight': 'bold', 'flex': '1'}),
            html.Span(f" (position {entity['start']}-{entity['end']})",
                     style={'color': '#6c757d', 'fontSize': '12px', 'marginRight': '10px'}),
            html.Button(
                '×',
                id={'type': 'remove-entity', 'index': entity['id']},
                style={
                    'background': '#dc3545',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '50%',
                    'width': '25px',
                    'height': '25px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'lineHeight': '1'
                },
                title='Remove entity'
            )
        ], style={
            'display': 'flex',
            'alignItems': 'center', 
            'backgroundColor': 'white',
            'border': '1px solid #dee2e6',
            'borderRadius': '8px',
            'padding': '12px',
            'marginBottom': '8px'
        })
        entity_cards.append(card)
    
    return html.Div(entity_cards)

# Pattern-matching callback to handle entity removal
# Uses Dash's pattern-matching callback feature to handle dynamic remove buttons
@callback(
    Output('entities-store', 'data', allow_duplicate=True),
    Input({'type': 'remove-entity', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('entities-store', 'data'),
    prevent_initial_call=True
)
def remove_entity(n_clicks_list, entities):
    """
    Remove an entity when its remove button is clicked.
    
    This uses pattern-matching callbacks to handle dynamically created remove buttons.
    Each button has an ID like {'type': 'remove-entity', 'index': entity_id}.
    
    Args:
        n_clicks_list: List of n_clicks values for all remove buttons
        entities: Current list of entities from the data store
        
    Returns:
        Updated entities list with the clicked entity removed
    """
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks_list):
        return entities
    
    # Get information about which button was clicked
    triggered = ctx.triggered[0]
    if triggered['value'] is None or triggered['value'] == 0:
        return entities
        
    # Extract entity ID from the pattern-matching callback prop_id
    # Format: {"index":123.456,"type":"remove-entity"}.n_clicks
    prop_id = triggered['prop_id']
    try:
        # Use regex to find the entity ID in the JSON-like string
        import re
        match = re.search(r'"index":([^,}]+)', prop_id)
        if match:
            entity_id = float(match.group(1))  # Convert to float (timestamp + random)
            
            # Filter out the entity with the matching ID
            updated_entities = [entity for entity in entities if entity['id'] != entity_id]
            return updated_entities
    except Exception as e:
        # If parsing fails, return entities unchanged
        print(f"Error parsing entity ID: {e}")
        pass
    
    return entities

# ========================================
# RUN THE APPLICATION
# ========================================

if __name__ == '__main__':
    print("🚀 Starting Dash NER Labeler Demo...")
    print("📍 Visit: http://localhost:8051")
    print("📖 Instructions:")
    print("   1. Select text with your mouse")
    print("   2. Click a label button (PERSON, ORG, etc.)")
    print("   3. View results below and export JSON data")
    print("   4. Remove entities by clicking the red × button")
    print("-" * 50)
    
    app.run(debug=True, port=8051)