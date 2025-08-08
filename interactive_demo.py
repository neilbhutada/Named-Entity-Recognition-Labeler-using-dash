import dash
from dash import html, dcc, callback, Input, Output, State
from dash_ner_labeler import NERLabeler
import json

# Sample text for demonstration
SAMPLE_TEXT = """
Apple Inc. is an American multinational technology company headquartered in Cupertino, California. 
Tim Cook is the current CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and 
Ronald Wayne in April 1976. Apple is known for products like the iPhone, iPad, and Mac computers. 
Microsoft Corporation, based in Redmond, Washington, is one of Apple's main competitors. 
Both companies are listed on the NASDAQ stock exchange in New York City.
"""

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Interactive NER Labeler Demo", style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        html.H3("Instructions:", style={'color': '#2c3e50'}),
        html.Ul([
            html.Li("Select text with your mouse to highlight it"),
            html.Li("Choose an entity label from the popup menu that appears"),
            html.Li("Click on labeled entities to remove them"),
            html.Li("View all labeled entities in the summary below")
        ], style={'marginBottom': 20})
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20}),
    
    # The actual NER Labeler component
    NERLabeler(
        id='ner-labeler',
        text=SAMPLE_TEXT.strip(),
        labelTypes=['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'],
        entities=[]
    ),
    
    html.Hr(style={'margin': '40px 0'}),
    
    # Results display
    html.Div([
        html.H3("Labeled Entities:"),
        html.Div(id='entities-display')
    ]),
    
    html.Div([
        html.H3("Raw JSON Output:"),
        html.Pre(
            id='entities-json',
            style={
                'backgroundColor': '#f8f9fa',
                'border': '1px solid #ddd',
                'borderRadius': 4,
                'padding': 15,
                'fontSize': 12,
                'maxHeight': 300,
                'overflow': 'auto'
            }
        )
    ], style={'marginTop': 30})
], style={'maxWidth': 1200, 'margin': '0 auto', 'padding': 20})

@callback(
    [Output('entities-display', 'children'),
     Output('entities-json', 'children')],
    [Input('ner-labeler', 'entities')]
)
def update_entities_display(entities):
    if not entities:
        return html.P("No entities labeled yet. Select text to start labeling!"), "[]"
    
    # Create a nice display of entities
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
            html.Span(entity['text'], style={'fontWeight': 'bold'}),
            html.Span(f" (chars {entity['start']}-{entity['end']})", 
                     style={'color': '#6c757d', 'fontSize': '12px'})
        ], style={
            'display': 'flex', 
            'alignItems': 'center',
            'backgroundColor': 'white',
            'border': '1px solid #dee2e6',
            'borderRadius': '8px',
            'padding': '12px',
            'marginBottom': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
        entity_cards.append(card)
    
    entities_json = json.dumps(entities, indent=2)
    
    return html.Div(entity_cards), entities_json

if __name__ == '__main__':
    app.run(debug=True, port=8050)