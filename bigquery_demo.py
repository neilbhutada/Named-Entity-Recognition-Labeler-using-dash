"""
BigQuery-Integrated NER Labeler - Production Demo
================================================

A production-ready Named Entity Recognition (NER) text labeling interface with BigQuery integration.
This demo supports loading texts from BigQuery, collaborative annotation, and storing results back
with complete audit trails.

Features:
- Load text instances from BigQuery tables
- Multi-user collaborative annotation
- Real-time annotation history
- Upload annotations to BigQuery with audit trail
- User statistics and progress tracking
- Batch processing capabilities
- Session management

Author: Generated with Claude Code
License: MIT
"""

import dash
from dash import html, dcc, callback, Input, Output, State, ALL, ctx
import json
import pandas as pd
from datetime import datetime
import uuid
import os
from typing import Dict, List, Optional

# Import components
from dash_ner_labeler import NERLabeler
from bigquery_integration import BigQueryNERManager

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "BigQuery NER Labeler"

# Global variables for demo (in production, use proper state management)
current_texts_df = pd.DataFrame()
current_text_index = 0
session_id = str(uuid.uuid4())

# Demo configuration (replace with your actual BigQuery config)
DEMO_CONFIG = {
    "project_id": "your-project-id",  # Replace with your GCP project ID
    "dataset_id": "ner_labeling",
    "credentials_path": None,  # Will use default credentials
    "batch_size": 5
}

# Initialize BigQuery manager (will be None in demo mode)
bq_manager = None
demo_mode = True

def initialize_bigquery():
    """Initialize BigQuery connection"""
    global bq_manager, demo_mode
    
    try:
        if os.path.exists("bigquery_config.json"):
            with open("bigquery_config.json", "r") as f:
                config = json.load(f)
                DEMO_CONFIG.update(config)
        
        # Try to initialize BigQuery (will fail gracefully in demo mode)
        bq_manager = BigQueryNERManager(
            project_id=DEMO_CONFIG["project_id"],
            credentials_path=DEMO_CONFIG.get("credentials_path"),
            dataset_id=DEMO_CONFIG["dataset_id"]
        )
        demo_mode = False
        print("✅ BigQuery connection established")
        
    except Exception as e:
        print(f"⚠️ BigQuery not available, running in demo mode: {e}")
        bq_manager = None
        demo_mode = True

# Initialize on startup
initialize_bigquery()

def create_demo_texts():
    """Create sample texts for demo mode"""
    return pd.DataFrame([
        {
            "text_id": "text_001",
            "text_content": "Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Tim Cook serves as the CEO, succeeding Steve Jobs who co-founded the company with Steve Wozniak.",
            "source": "demo_data",
            "status": "pending",
            "priority": 1
        },
        {
            "text_id": "text_002", 
            "text_content": "Microsoft Corporation is a multinational technology company based in Redmond, Washington. Satya Nadella is the current CEO, taking over from Bill Gates and Steve Ballmer.",
            "source": "demo_data",
            "status": "pending",
            "priority": 2
        },
        {
            "text_id": "text_003",
            "text_content": "Google LLC, a subsidiary of Alphabet Inc., was founded by Larry Page and Sergey Brin while they were PhD students at Stanford University in California. The company is now led by CEO Sundar Pichai.",
            "source": "demo_data", 
            "status": "pending",
            "priority": 3
        },
        {
            "text_id": "text_004",
            "text_content": "Amazon.com, Inc. is an American multinational technology company based in Seattle, Washington. Jeff Bezos founded the company in 1994, and Andy Jassy currently serves as CEO.",
            "source": "demo_data",
            "status": "pending",
            "priority": 4
        },
        {
            "text_id": "text_005",
            "text_content": "Tesla, Inc. is an American electric vehicle and clean energy company based in Austin, Texas. Elon Musk serves as CEO and has been instrumental in the company's growth since joining in 2004.",
            "source": "demo_data",
            "status": "pending", 
            "priority": 5
        }
    ])

# ========================================
# APP LAYOUT DEFINITION
# ========================================

app.layout = html.Div([
    # Store components for state management
    dcc.Store(id='texts-store', data=[]),
    dcc.Store(id='current-text-index', data=0),
    dcc.Store(id='session-id', data=session_id),
    dcc.Store(id='bigquery-status', data={"connected": not demo_mode, "demo_mode": demo_mode}),
    
    # Header
    html.Div([
        html.H1("🔗 BigQuery NER Labeler", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
        html.P("Production-ready annotation platform with BigQuery integration", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 30})
    ]),
    
    # BigQuery Connection Status
    html.Div(id='bigquery-status-display', style={'marginBottom': 20}),
    
    # Control Panel
    html.Div([
        html.H3("📋 Control Panel", style={'color': '#2c3e50', 'marginBottom': 15}),
        
        # Load texts section
        html.Div([
            html.H4("🔄 Load Texts", style={'color': '#34495e', 'marginBottom': 10}),
            html.Div([
                html.Button("📥 Load from BigQuery", id="load-bigquery-btn", 
                           style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none',
                                 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                                 'marginRight': '10px', 'fontSize': '14px'},
                           disabled=demo_mode),
                html.Button("🎯 Load Demo Data", id="load-demo-btn",
                           style={'backgroundColor': '#e74c3c', 'color': 'white', 'border': 'none',
                                 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                                 'marginRight': '10px', 'fontSize': '14px'}),
                dcc.Input(id="batch-size-input", type="number", value=5, min=1, max=50,
                         style={'padding': '10px', 'borderRadius': '5px', 'border': '1px solid #ddd',
                               'width': '80px', 'marginRight': '10px'}),
                html.Span("texts", style={'color': '#7f8c8d', 'fontSize': '14px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': 15}),
            
            # Navigation controls
            html.Div([
                html.Button("⬅️ Previous", id="prev-text-btn",
                           style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none',
                                 'padding': '8px 16px', 'borderRadius': '5px', 'cursor': 'pointer',
                                 'marginRight': '10px', 'fontSize': '12px'},
                           disabled=True),
                html.Span(id="text-counter", style={'color': '#2c3e50', 'fontWeight': 'bold', 'marginRight': '10px'}),
                html.Button("Next ➡️", id="next-text-btn",
                           style={'backgroundColor': '#95a5a6', 'color': 'white', 'border': 'none',
                                 'padding': '8px 16px', 'borderRadius': '5px', 'cursor': 'pointer',
                                 'marginRight': '20px', 'fontSize': '12px'},
                           disabled=True),
                html.Button("💾 Save to BigQuery", id="save-bigquery-btn",
                           style={'backgroundColor': '#27ae60', 'color': 'white', 'border': 'none',
                                 'padding': '8px 16px', 'borderRadius': '5px', 'cursor': 'pointer',
                                 'fontSize': '12px'},
                           disabled=True)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': 15}),
        ], style={'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
        
        # Status and messages
        html.Div(id='status-messages', style={'marginBottom': 20})
        
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20}),
    
    # Current Text Info
    html.Div(id='current-text-info', style={'marginBottom': 20}),
    
    # Main NER Labeler Component
    html.Div([
        NERLabeler(
            id='ner-labeler',
            text="",
            entities=[],
            labelTypes=['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS', 'DATE', 'MONEY', 'PRODUCT'],
            currentUser=None,
            annotationHistory=[],
            showUserInfo=True,
            showHistory=True
        )
    ], id='ner-container', style={'marginBottom': 30}),
    
    html.Hr(style={'margin': '40px 0'}),
    
    # Statistics Dashboard
    html.Div([
        html.H3("📊 Annotation Dashboard", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div(id='statistics-dashboard', style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
            'gap': '15px',
            'marginBottom': '20px'
        }),
        
        # Progress tracking
        html.Div([
            html.H4("📈 Progress Tracking", style={'color': '#2c3e50', 'marginBottom': 10}),
            html.Div(id='progress-display')
        ])
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8, 'marginBottom': 20}),
    
    # Export section
    html.Div([
        html.H3("📤 Export & Audit", style={'color': '#2c3e50', 'marginBottom': 15}),
        html.Div([
            html.Button("📋 Export Current Session", id="export-session-btn",
                       style={'backgroundColor': '#8e44ad', 'color': 'white', 'border': 'none',
                             'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                             'marginRight': '10px', 'fontSize': '14px'}),
            html.Button("📊 View Audit Trail", id="view-audit-btn",
                       style={'backgroundColor': '#f39c12', 'color': 'white', 'border': 'none',
                             'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                             'fontSize': '14px'})
        ], style={'marginBottom': '15px'}),
        
        html.Div(id='export-display')
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 8})
])

# ========================================
# CALLBACK FUNCTIONS
# ========================================

@callback(
    Output('bigquery-status-display', 'children'),
    Input('bigquery-status', 'data')
)
def display_bigquery_status(status):
    """Display BigQuery connection status"""
    if status['demo_mode']:
        return html.Div([
            html.Div([
                "⚠️ Demo Mode: BigQuery not connected. Using sample data.",
                html.Br(),
                html.Small("To connect BigQuery: Create bigquery_config.json with your project details.",
                          style={'color': '#7f8c8d'})
            ], style={'backgroundColor': '#fff3cd', 'border': '1px solid #ffeaa7', 'color': '#856404',
                     'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px'})
        ])
    else:
        return html.Div([
            html.Div([
                f"✅ Connected to BigQuery: {DEMO_CONFIG['project_id']}.{DEMO_CONFIG['dataset_id']}"
            ], style={'backgroundColor': '#d4edda', 'border': '1px solid #c3e6cb', 'color': '#155724',
                     'padding': '10px', 'borderRadius': '5px', 'marginBottom': '10px'})
        ])

@callback(
    [Output('texts-store', 'data'),
     Output('current-text-index', 'data'),
     Output('status-messages', 'children')],
    [Input('load-bigquery-btn', 'n_clicks'),
     Input('load-demo-btn', 'n_clicks')],
    [State('batch-size-input', 'value')]
)
def load_texts(bigquery_clicks, demo_clicks, batch_size):
    """Load texts from BigQuery or demo data"""
    global current_texts_df
    
    if not ctx.triggered:
        return [], 0, ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == 'load-bigquery-btn' and not demo_mode:
            # Load from BigQuery
            df = bq_manager.load_texts_for_annotation(limit=batch_size or 5)
            if not df.empty:
                current_texts_df = df
                message = html.Div(f"✅ Loaded {len(df)} texts from BigQuery", 
                                  style={'color': '#27ae60', 'fontWeight': 'bold'})
                return df.to_dict('records'), 0, message
            else:
                message = html.Div("⚠️ No pending texts found in BigQuery", 
                                  style={'color': '#f39c12', 'fontWeight': 'bold'})
                return [], 0, message
                
        elif button_id == 'load-demo-btn':
            # Load demo data
            df = create_demo_texts()
            current_texts_df = df
            message = html.Div(f"✅ Loaded {len(df)} demo texts", 
                              style={'color': '#27ae60', 'fontWeight': 'bold'})
            return df.to_dict('records'), 0, message
            
    except Exception as e:
        message = html.Div(f"❌ Error loading texts: {str(e)}", 
                          style={'color': '#e74c3c', 'fontWeight': 'bold'})
        return [], 0, message
    
    return [], 0, ""

@callback(
    [Output('current-text-index', 'data', allow_duplicate=True),
     Output('prev-text-btn', 'disabled'),
     Output('next-text-btn', 'disabled'),
     Output('save-bigquery-btn', 'disabled')],
    [Input('prev-text-btn', 'n_clicks'),
     Input('next-text-btn', 'n_clicks')],
    [State('current-text-index', 'data'),
     State('texts-store', 'data')],
    prevent_initial_call=True
)
def navigate_texts(prev_clicks, next_clicks, current_index, texts_data):
    """Navigate between texts"""
    if not texts_data:
        return 0, True, True, True
    
    total_texts = len(texts_data)
    
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'prev-text-btn' and current_index > 0:
            current_index -= 1
        elif button_id == 'next-text-btn' and current_index < total_texts - 1:
            current_index += 1
    
    prev_disabled = current_index <= 0
    next_disabled = current_index >= total_texts - 1
    save_disabled = not texts_data
    
    return current_index, prev_disabled, next_disabled, save_disabled

@callback(
    [Output('ner-labeler', 'text'),
     Output('ner-labeler', 'entities'),
     Output('current-text-info', 'children'),
     Output('text-counter', 'children')],
    [Input('current-text-index', 'data')],
    [State('texts-store', 'data')]
)
def update_current_text(current_index, texts_data):
    """Update the NER labeler with current text"""
    if not texts_data or current_index >= len(texts_data):
        return "", [], "", "No texts loaded"
    
    current_text_data = texts_data[current_index]
    text_id = current_text_data.get('text_id', f'text_{current_index}')
    text_content = current_text_data.get('text_content', '')
    
    # Load existing annotations if connected to BigQuery
    existing_entities = []
    if not demo_mode and bq_manager:
        try:
            existing_entities = bq_manager.load_existing_annotations(text_id)
        except Exception as e:
            print(f"Failed to load existing annotations: {e}")
    
    # Create text info display
    text_info = html.Div([
        html.H4("📄 Current Text", style={'color': '#2c3e50', 'marginBottom': 10}),
        html.Div([
            html.Strong("Text ID: "), text_id,
            html.Br(),
            html.Strong("Source: "), current_text_data.get('source', 'Unknown'),
            html.Br(),
            html.Strong("Status: "), 
            html.Span(current_text_data.get('status', 'unknown'), 
                     style={'backgroundColor': '#3498db', 'color': 'white', 'padding': '2px 8px', 
                           'borderRadius': '12px', 'fontSize': '12px'}),
            html.Br(),
            html.Strong("Priority: "), current_text_data.get('priority', 'N/A'),
        ], style={'fontSize': '14px', 'color': '#34495e'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': '15px', 'borderRadius': '8px'})
    
    counter = f"Text {current_index + 1} of {len(texts_data)}"
    
    return text_content, existing_entities, text_info, counter

@callback(
    Output('status-messages', 'children', allow_duplicate=True),
    Input('save-bigquery-btn', 'n_clicks'),
    [State('ner-labeler', 'entities'),
     State('ner-labeler', 'currentUser'),
     State('current-text-index', 'data'),
     State('texts-store', 'data'),
     State('session-id', 'data')],
    prevent_initial_call=True
)
def save_annotations_to_bigquery(n_clicks, entities, current_user, current_index, texts_data, session_id):
    """Save current annotations to BigQuery"""
    if not n_clicks or not texts_data or current_index >= len(texts_data):
        return ""
    
    if not current_user or not current_user.get('name'):
        return html.Div("⚠️ Please set a username before saving annotations", 
                       style={'color': '#f39c12', 'fontWeight': 'bold'})
    
    try:
        current_text_data = texts_data[current_index]
        text_id = current_text_data.get('text_id', f'text_{current_index}')
        
        if demo_mode:
            # Demo mode - just show success message
            return html.Div([
                f"✅ Demo: Would save {len(entities or [])} annotations for text {text_id}",
                html.Br(),
                html.Small(f"User: {current_user['name']}, Session: {session_id[:8]}...", 
                          style={'color': '#7f8c8d'})
            ], style={'color': '#27ae60', 'fontWeight': 'bold'})
        
        # Real BigQuery save
        success = bq_manager.upload_annotations(
            text_id=text_id,
            entities=entities or [],
            user_id=current_user.get('id', 'unknown'),
            username=current_user['name'],
            session_id=session_id
        )
        
        if success:
            return html.Div([
                f"✅ Saved {len(entities or [])} annotations to BigQuery",
                html.Br(),
                html.Small(f"Text: {text_id}, User: {current_user['name']}", 
                          style={'color': '#7f8c8d'})
            ], style={'color': '#27ae60', 'fontWeight': 'bold'})
        else:
            return html.Div("❌ Failed to save annotations to BigQuery", 
                           style={'color': '#e74c3c', 'fontWeight': 'bold'})
            
    except Exception as e:
        return html.Div(f"❌ Error saving to BigQuery: {str(e)}", 
                       style={'color': '#e74c3c', 'fontWeight': 'bold'})

@callback(
    Output('statistics-dashboard', 'children'),
    [Input('ner-labeler', 'entities'),
     Input('ner-labeler', 'annotationHistory'),
     Input('current-text-index', 'data'),
     Input('texts-store', 'data')]
)
def update_statistics_dashboard(entities, history, current_index, texts_data):
    """Update the statistics dashboard"""
    entities = entities or []
    history = history or []
    
    # Current session stats
    total_entities = len(entities)
    entity_types = {}
    for entity in entities:
        label = entity['label']
        entity_types[label] = entity_types.get(label, 0) + 1
    
    # User activity
    user_activity = {}
    for entry in history:
        username = entry.get('username', 'Unknown')
        if username not in user_activity:
            user_activity[username] = {'add': 0, 'remove': 0}
        user_activity[username][entry['action']] += 1
    
    # Progress stats
    texts_completed = current_index if texts_data else 0
    total_texts = len(texts_data) if texts_data else 0
    progress_percentage = (texts_completed / total_texts * 100) if total_texts > 0 else 0
    
    stats_cards = []
    
    # Current text stats
    stats_cards.append(
        html.Div([
            html.H4("📝 Current Text", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
            html.H2(str(total_entities), style={'margin': '5px 0', 'color': '#2c3e50'}),
            html.P("entities annotated", style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
    )
    
    # Progress card
    stats_cards.append(
        html.Div([
            html.H4("📊 Progress", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
            html.H2(f"{progress_percentage:.1f}%", style={'margin': '5px 0', 'color': '#2c3e50'}),
            html.P(f"{texts_completed}/{total_texts} texts", style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'})
        ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
    )
    
    # Entity types card
    if entity_types:
        top_type = max(entity_types.keys(), key=lambda k: entity_types[k])
        stats_cards.append(
            html.Div([
                html.H4("🏷️ Top Label", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
                html.H2(str(entity_types[top_type]), style={'margin': '5px 0', 'color': '#2c3e50'}),
                html.P(top_type, style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
        )
    
    # User activity card
    if user_activity:
        most_active_user = max(user_activity.keys(), key=lambda k: sum(user_activity[k].values()))
        total_actions = sum(user_activity[most_active_user].values())
        stats_cards.append(
            html.Div([
                html.H4("👤 Most Active", style={'margin': 0, 'fontSize': '14px', 'color': '#6c757d'}),
                html.H2(str(total_actions), style={'margin': '5px 0', 'color': '#2c3e50'}),
                html.P(f"@{most_active_user}", style={'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d'})
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #e9ecef'})
        )
    
    return stats_cards

@callback(
    Output('export-display', 'children'),
    [Input('export-session-btn', 'n_clicks'),
     Input('view-audit-btn', 'n_clicks')],
    [State('ner-labeler', 'entities'),
     State('ner-labeler', 'annotationHistory'),
     State('ner-labeler', 'currentUser'),
     State('session-id', 'data'),
     State('texts-store', 'data')]
)
def handle_export_actions(export_clicks, audit_clicks, entities, history, current_user, session_id, texts_data):
    """Handle export and audit actions"""
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'export-session-btn':
        # Export current session data
        session_data = {
            "session_id": session_id,
            "user": current_user,
            "timestamp": datetime.now().isoformat(),
            "texts_loaded": len(texts_data) if texts_data else 0,
            "current_entities": entities or [],
            "annotation_history": history or [],
            "session_stats": {
                "total_entities": len(entities or []),
                "total_actions": len(history or []),
                "bigquery_connected": not demo_mode
            }
        }
        
        return html.Div([
            html.H4("📋 Session Export", style={'marginBottom': '10px'}),
            html.Pre(json.dumps(session_data, indent=2), style={
                'backgroundColor': '#f8f9fa', 'border': '1px solid #ddd',
                'borderRadius': '4px', 'padding': '15px', 'fontSize': '11px',
                'maxHeight': '400px', 'overflowY': 'auto',
                'fontFamily': 'Monaco, Consolas, monospace'
            })
        ])
    
    elif button_id == 'view-audit-btn':
        # Show audit trail
        if demo_mode:
            audit_info = "⚠️ Audit trail only available with BigQuery connection"
        else:
            audit_info = "✅ Audit trail available in BigQuery annotation_history table"
        
        return html.Div([
            html.H4("📊 Audit Trail", style={'marginBottom': '10px'}),
            html.P(audit_info, style={'color': '#7f8c8d'}),
            html.Div([
                html.H5("Current Session History:", style={'marginTop': '15px', 'marginBottom': '10px'}),
                html.Div([
                    html.Div([
                        html.Span(f"{entry.get('action', 'unknown').upper()}", 
                                 style={'backgroundColor': '#3498db', 'color': 'white', 'padding': '2px 6px',
                                       'borderRadius': '3px', 'fontSize': '10px', 'marginRight': '8px'}),
                        html.Span(f"@{entry.get('username', 'Unknown')}", style={'fontWeight': 'bold', 'marginRight': '8px'}),
                        html.Span(entry.get('entity', {}).get('text', 'N/A'), style={'marginRight': '8px'}),
                        html.Small(entry.get('timestamp', ''), style={'color': '#7f8c8d'})
                    ], style={'padding': '8px', 'backgroundColor': 'white', 'border': '1px solid #e9ecef',
                             'borderRadius': '4px', 'marginBottom': '5px'})
                    for entry in (history or [])[-10:]  # Show last 10 actions
                ])
            ])
        ])
    
    return ""

# ========================================
# RUN THE APPLICATION
# ========================================

if __name__ == '__main__':
    print("🚀 Starting BigQuery-Integrated NER Labeler...")
    print("📍 Visit: http://localhost:8053")
    print("=" * 60)
    
    if demo_mode:
        print("⚠️ Running in DEMO MODE")
        print("📋 Features available:")
        print("   ✅ Load demo texts")
        print("   ✅ Multi-user annotation")
        print("   ✅ Session export")
        print("   ❌ BigQuery integration (not configured)")
        print("")
        print("🔗 To enable BigQuery:")
        print("   1. Create bigquery_config.json with your project details")
        print("   2. Install google-cloud-bigquery: pip install google-cloud-bigquery")
        print("   3. Set up authentication (service account or default credentials)")
    else:
        print("✅ BigQuery CONNECTED")
        print(f"📊 Project: {DEMO_CONFIG['project_id']}")
        print(f"📊 Dataset: {DEMO_CONFIG['dataset_id']}")
        print("📋 Features available:")
        print("   ✅ Load texts from BigQuery")
        print("   ✅ Multi-user annotation")
        print("   ✅ Save annotations to BigQuery")
        print("   ✅ Audit trail and history")
        print("   ✅ User statistics")
    
    print("=" * 60)
    print("📖 Instructions:")
    print("   1. Set your username")
    print("   2. Load texts (BigQuery or demo)")
    print("   3. Navigate through texts")
    print("   4. Annotate entities")
    print("   5. Save to BigQuery (if connected)")
    print("   6. Export session data")
    print("-" * 60)
    
    app.run(debug=True, port=8053)