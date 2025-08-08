import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback
import json

# Sample text for demonstration
SAMPLE_TEXT = """Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Tim Cook is the current CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976."""

# Initialize the Dash app
app = dash.Dash(__name__)

# Add custom JavaScript for text selection
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .ner-text-container {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 20px;
                line-height: 1.6;
                font-size: 16px;
                min-height: 200px;
                cursor: text;
                position: relative;
                user-select: text;
            }
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
            .ner-person { background-color: #ffeb3b; border: 1px solid #fbc02d; }
            .ner-organization { background-color: #2196f3; color: white; border: 1px solid #1976d2; }
            .ner-location { background-color: #4caf50; color: white; border: 1px solid #388e3c; }
            .ner-miscellaneous { background-color: #ff9800; color: white; border: 1px solid #f57c00; }
            
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

# Define the app layout
app.layout = html.Div([
    html.H1("Working NER Labeler Demo", style={'textAlign': 'center', 'marginBottom': 30}),
    
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
        
        # Hidden div to store entities
        dcc.Store(id='entities-store', data=[]),
        
        # Selected text info
        html.Div(id='selection-info', style={'marginTop': 20}),
    ]),
    
    html.Hr(style={'margin': '40px 0'}),
    
    # Results display  
    html.Div([
        html.H3("Labeled Entities:"),
        html.Div(id='entities-display')
    ]),
    
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

# Add client-side callback for text selection
app.clientside_callback(
    """
    function(person_clicks, org_clicks, loc_clicks, misc_clicks, current_entities) {
        const ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered.length) {
            return [current_entities, 'Select some text and click a label button'];
        }
        
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
        
        // Get selected text
        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.toString().trim() === '') {
            return [current_entities, 'No text selected'];
        }
        
        const selectedText = selection.toString().trim();
        const range = selection.getRangeAt(0);
        
        // Calculate approximate start position (simplified)
        const textContainer = document.getElementById('text-display');
        const beforeRange = document.createRange();
        beforeRange.setStart(textContainer, 0);
        beforeRange.setEnd(range.startContainer, range.startOffset);
        const start = beforeRange.toString().length;
        
        // Create new entity
        const newEntity = {
            id: Date.now() + Math.random(),
            text: selectedText,
            label: label,
            start: start,
            end: start + selectedText.length
        };
        
        const updatedEntities = [...current_entities, newEntity];
        
        // Clear selection
        selection.removeAllRanges();
        
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

@callback(
    Output('entities-json', 'children'),
    [Input('entities-store', 'data')]
)
def update_json_display(entities):
    return json.dumps(entities, indent=2)

@callback(
    Output('entities-display', 'children'),
    [Input('entities-store', 'data')]
)
def display_entities(entities):
    if not entities:
        return html.P("No entities labeled yet.")
    
    entity_cards = []
    for entity in entities:
        color_map = {
            'PERSON': '#ffeb3b',
            'ORGANIZATION': '#2196f3',
            'LOCATION': '#4caf50', 
            'MISCELLANEOUS': '#ff9800'
        }
        
        text_color = 'black' if entity['label'] == 'PERSON' else 'white'
        bg_color = color_map.get(entity['label'], '#6c757d')
        
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
            html.Span(f'"{entity["text"]}"', style={'fontWeight': 'bold'}),
            html.Span(f" (position {entity['start']}-{entity['end']})",
                     style={'color': '#6c757d', 'fontSize': '12px'})
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

if __name__ == '__main__':
    app.run(debug=True, port=8051)