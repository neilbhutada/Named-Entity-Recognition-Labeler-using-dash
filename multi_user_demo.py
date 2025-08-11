"""
Multi-User NER Labeler - Interactive Demo
=========================================

A fully functional Named Entity Recognition (NER) text labeling interface built with Dash.
This demo supports multiple users with annotation tracking, history, and user attribution.

Features:
- Multi-user support with simple username-based sessions
- Interactive text selection with mouse
- Multiple entity types (PERSON, ORGANIZATION, LOCATION, MISCELLANEOUS)
- Add/remove entity labels with user tracking
- Real-time annotation history
- User attribution for all annotations
- Timestamp tracking for all changes
- JSON export for ML training data

Author: Generated with Claude Code
License: MIT
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ALL
import json
from datetime import datetime

# Import the updated NER component
from dash_ner_labeler import NERLabeler

# Sample text for demonstration - contains various entity types
SAMPLE_TEXT = """Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Tim Cook is the current CEO of Apple. The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976 to develop and sell personal computers. Microsoft Corporation is another major technology company based in Redmond, Washington. Bill Gates and Paul Allen founded Microsoft in 1975. Both companies have had significant impact on the technology industry globally."""

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Multi-User NER Labeler Demo"

# ========================================
# APP LAYOUT DEFINITION
# ========================================

app.layout = html.Div([
    # Main title
    html.H1("Multi-User NER Labeler Demo", style={'textAlign': 'center', 'marginBottom': 30, 'color': '#2c3e50'}),
    
    # Instructions panel
    html.Div([
        html.H3("Multi-User Features:", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Ul([
            html.Li("🔒 Set your username before annotating"),
            html.Li("🖱️ Select text with your mouse to highlight it"),
            html.Li("🏷️ Choose a label type from the popup modal"),
            html.Li("👥 See who made each annotation and when"),
            html.Li("📋 View annotation history with user attribution"),
            html.Li("❌ Click on entities to remove them (tracks user action)"),
            html.Li("📊 Export JSON data with full user metadata"),
        ], style={'marginBottom': 20, 'lineHeight': 1.6})
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20, 'border': '1px solid #e9ecef'}),
    
    # Main NER Labeler Component
    html.Div([
        NERLabeler(
            id='ner-labeler',
            text=SAMPLE_TEXT,
            entities=[],
            labelTypes=['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'],
            currentUser=None,
            annotationHistory=[],
            showUserInfo=True,
            showHistory=True
        )
    ], style={'marginBottom': 30}),
    
    html.Hr(style={'margin': '40px 0'}),
    
    # Statistics section
    html.Div([
        html.H3("📊 Statistics:", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div(id='statistics-display', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
            'gap': '15px'
        })
    ], style={'marginBottom': 30}),
    
    # JSON export section for ML training data
    html.Div([
        html.H3("🔗 JSON Export (for ML Training):", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div([
            html.Button("📋 Copy JSON", id="copy-json-btn", style={
                'backgroundColor': '#007bff', 'color': 'white', 'border': 'none',
                'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                'marginBottom': '10px', 'fontSize': '14px'
            }),
            html.Div(id='copy-status', style={'color': '#28a745', 'fontSize': '12px', 'marginBottom': '10px'})
        ]),
        html.Pre(id='entities-json', style={
            'backgroundColor': '#f8f9fa',
            'border': '1px solid #ddd', 
            'borderRadius': 4,
            'padding': 15,
            'fontSize': 11,
            'maxHeight': '300px',
            'overflowY': 'auto',
            'whiteSpace': 'pre-wrap',
            'fontFamily': 'Monaco, Consolas, "Lucida Console", monospace'
        })
    ])
])

# ========================================
# CALLBACK FUNCTIONS
# ========================================

# Update statistics display
@callback(
    Output('statistics-display', 'children'),
    [Input('ner-labeler', 'entities'),
     Input('ner-labeler', 'annotationHistory'),
     Input('ner-labeler', 'currentUser')]
)
def update_statistics(entities, history, current_user):
    """Display statistics about annotations and users."""
    entities = entities or []
    history = history or []
    
    # Count entities by type
    entity_counts = {}
    for entity in entities:
        label = entity['label']
        entity_counts[label] = entity_counts.get(label, 0) + 1
    
    # Count entities by user
    user_counts = {}
    for entity in entities:
        username = entity.get('username', 'Unknown')
        user_counts[username] = user_counts.get(username, 0) + 1
    
    # Count actions by user
    action_counts = {}
    for entry in history:
        username = entry.get('username', 'Unknown')
        if username not in action_counts:
            action_counts[username] = {'add': 0, 'remove': 0}
        action_counts[username][entry['action']] += 1
    
    stats_cards = []
    
    # Total entities card
    stats_cards.append(
        html.Div([
            html.H4("📝 Total Entities", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
            html.H2(str(len(entities)), style={'margin': '5px 0', 'color': '#2c3e50'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
    )
    
    # Entity types card
    if entity_counts:
        type_text = ", ".join([f"{label}: {count}" for label, count in entity_counts.items()])
        stats_cards.append(
            html.Div([
                html.H4("🏷️ By Type", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
                html.P(type_text, style={'margin': '5px 0', 'fontSize': '12px', 'color': '#2c3e50'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
        )
    
    # Active users card
    if user_counts:
        user_text = ", ".join([f"@{user}: {count}" for user, count in user_counts.items()])
        stats_cards.append(
            html.Div([
                html.H4("👥 Active Users", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
                html.P(user_text, style={'margin': '5px 0', 'fontSize': '12px', 'color': '#2c3e50'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
        )
    
    # Current user card
    current_user_name = current_user.get('name') if current_user else 'Not set'
    stats_cards.append(
        html.Div([
            html.H4("👤 Current User", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
            html.P(f"@{current_user_name}" if current_user_name != 'Not set' else current_user_name, 
                   style={'margin': '5px 0', 'fontSize': '14px', 'color': '#2c3e50', 'fontWeight': 'bold'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
    )
    
    return stats_cards

# Update JSON display with enhanced formatting
@callback(
    Output('entities-json', 'children'),
    [Input('ner-labeler', 'entities'),
     Input('ner-labeler', 'annotationHistory'),
     Input('ner-labeler', 'currentUser')]
)
def update_json_display(entities, history, current_user):
    """Convert entities and metadata to formatted JSON for display and export."""
    export_data = {
        "text": SAMPLE_TEXT,
        "entities": entities or [],
        "annotation_history": history or [],
        "current_user": current_user,
        "export_timestamp": datetime.now().isoformat(),
        "total_entities": len(entities or []),
        "total_actions": len(history or [])
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)

# Copy to clipboard functionality (client-side callback)
app.clientside_callback(
    """
    function(n_clicks, json_content) {
        if (n_clicks && json_content) {
            // Copy to clipboard
            navigator.clipboard.writeText(json_content).then(function() {
                // Success - return status message
                return "✅ JSON copied to clipboard!";
            }, function() {
                // Fallback for older browsers
                const textArea = document.createElement("textarea");
                textArea.value = json_content;
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                try {
                    document.execCommand('copy');
                    return "✅ JSON copied to clipboard!";
                } catch (err) {
                    return "❌ Failed to copy. Please copy manually.";
                }
                document.body.removeChild(textArea);
            });
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('copy-status', 'children'),
    Input('copy-json-btn', 'n_clicks'),
    State('entities-json', 'children'),
    prevent_initial_call=True
)

# Clear copy status after 3 seconds
app.clientside_callback(
    """
    function(status) {
        if (status && status !== window.dash_clientside.no_update) {
            setTimeout(function() {
                // Find the element and clear it
                const element = document.getElementById('copy-status');
                if (element) {
                    element.innerHTML = '';
                }
            }, 3000);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('copy-status', 'style'),
    Input('copy-status', 'children'),
    prevent_initial_call=True
)

# ========================================
# RUN THE APPLICATION
# ========================================

if __name__ == '__main__':
    print("🚀 Starting Multi-User Dash NER Labeler Demo...")
    print("📍 Visit: http://localhost:8052")
    print("👥 Multi-User Features:")
    print("   ✅ User authentication (username-based)")
    print("   ✅ Annotation tracking with timestamps")
    print("   ✅ User attribution for all changes")
    print("   ✅ Annotation history with full audit trail")
    print("   ✅ Statistics and user activity monitoring")
    print("   ✅ Enhanced JSON export with metadata")
    print("📖 Instructions:")
    print("   1. Set your username first")
    print("   2. Select text with your mouse")
    print("   3. Choose a label from the popup")
    print("   4. View history and user attributions")
    print("   5. Export annotated data with full metadata")
    print("-" * 60)
    
    app.run(debug=True, port=8052)