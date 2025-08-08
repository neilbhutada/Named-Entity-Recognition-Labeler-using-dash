import dash
from dash import html, dcc, callback, Input, Output, State
import json

# For development, we'll use a simulated version of our component
# In production, this would be: from dash_ner_labeler import NERLabeler

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
    html.H1("NER Labeler Demo", style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        html.H3("Instructions:", style={'color': '#2c3e50'}),
        html.Ul([
            html.Li("Select text with your mouse to highlight it"),
            html.Li("Choose an entity label from the popup menu"),
            html.Li("Click on labeled entities to remove them"),
            html.Li("View all labeled entities in the summary below")
        ], style={'marginBottom': 20})
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20}),
    
    # Text input area
    html.Div([
        html.H3("Text to Label:"),
        dcc.Textarea(
            id='text-input',
            value=SAMPLE_TEXT.strip(),
            style={
                'width': '100%', 
                'height': 120, 
                'padding': 10,
                'borderRadius': 4,
                'border': '1px solid #ddd',
                'fontSize': 14
            }
        )
    ], style={'marginBottom': 20}),
    
    # Custom label types input
    html.Div([
        html.H3("Custom Label Types (comma-separated):"),
        dcc.Input(
            id='labels-input',
            value='PERSON,ORGANIZATION,LOCATION,MISCELLANEOUS',
            style={
                'width': '100%',
                'padding': 10,
                'borderRadius': 4,
                'border': '1px solid #ddd'
            }
        )
    ], style={'marginBottom': 20}),
    
    html.Button('Update Component', id='update-btn', n_clicks=0, 
                style={
                    'padding': '10px 20px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': 4,
                    'cursor': 'pointer',
                    'marginBottom': 20
                }),
    
    # Placeholder for our NER component (simulated with HTML for demo)
    html.Div(id='ner-component-container', style={'marginBottom': 30}),
    
    # Results display
    html.Div([
        html.H3("Labeled Entities (JSON Output):"),
        html.Pre(
            id='entities-output',
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
    ])
])

@callback(
    [Output('ner-component-container', 'children'),
     Output('entities-output', 'children')],
    [Input('update-btn', 'n_clicks')],
    [State('text-input', 'value'),
     State('labels-input', 'value')]
)
def update_ner_component(n_clicks, text_value, labels_value):
    if not text_value:
        return "Please enter some text to label.", "No entities"
    
    # Parse label types
    label_types = [label.strip() for label in labels_value.split(',') if label.strip()]
    
    # Create a simulated NER component using HTML
    # In the real implementation, this would be:
    # ner_component = NERLabeler(
    #     id='ner-labeler',
    #     text=text_value,
    #     labelTypes=label_types,
    #     entities=[]
    # )
    
    # For demo purposes, create an interactive HTML version
    ner_component = html.Div([
        html.H3("NER Labeler Component"),
        html.Div([
            html.P("🚧 Demo Mode: This simulates the actual NER component behavior", 
                   style={'backgroundColor': '#fff3cd', 'padding': 10, 'borderRadius': 4}),
            html.Div([
                html.P("Text to label:", style={'fontWeight': 'bold'}),
                html.Div(
                    text_value,
                    id='text-display',
                    style={
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'borderRadius': 6,
                        'padding': 20,
                        'lineHeight': 1.6,
                        'fontSize': 16,
                        'minHeight': 200,
                        'userSelect': 'text',
                        'cursor': 'text'
                    }
                )
            ]),
            html.Div([
                html.P("Available Labels:", style={'fontWeight': 'bold', 'marginTop': 15}),
                html.Div([
                    html.Span(
                        label,
                        className=f'label-{label.lower()}',
                        style={
                            'display': 'inline-block',
                            'padding': '4px 12px',
                            'margin': '2px',
                            'borderRadius': 15,
                            'fontSize': 12,
                            'fontWeight': 'bold',
                            'backgroundColor': get_label_color(label),
                            'color': 'white' if label != 'PERSON' else 'black',
                            'border': f'1px solid {get_label_border_color(label)}'
                        }
                    ) for label in label_types
                ])
            ])
        ])
    ], style={
        'border': '2px solid #007bff',
        'borderRadius': 8,
        'padding': 20,
        'backgroundColor': 'white'
    })
    
    # Sample entities output
    sample_entities = [
        {"id": 1, "text": "Apple Inc.", "label": "ORGANIZATION", "start": 0, "end": 10},
        {"id": 2, "text": "Tim Cook", "label": "PERSON", "start": 85, "end": 93},
        {"id": 3, "text": "Cupertino, California", "label": "LOCATION", "start": 65, "end": 86}
    ]
    
    entities_json = json.dumps(sample_entities, indent=2)
    
    return ner_component, entities_json

def get_label_color(label):
    colors = {
        'PERSON': '#ffeb3b',
        'ORGANIZATION': '#2196f3',
        'LOCATION': '#4caf50',
        'MISCELLANEOUS': '#ff9800'
    }
    return colors.get(label.upper(), '#6c757d')

def get_label_border_color(label):
    colors = {
        'PERSON': '#fbc02d',
        'ORGANIZATION': '#1976d2',
        'LOCATION': '#388e3c',
        'MISCELLANEOUS': '#f57c00'
    }
    return colors.get(label.upper(), '#495057')

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)