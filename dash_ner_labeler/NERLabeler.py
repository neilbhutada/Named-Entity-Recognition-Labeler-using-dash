import os
import json
from dash.development.base_component import Component, _explicitize_args


class NERLabeler(Component):
    """A Dash component for Named Entity Recognition (NER) text labeling.
    
    This component allows users to manually highlight and label text for NER tasks.
    Users can select text with their mouse and assign entity labels like PERSON, 
    ORGANIZATION, LOCATION, etc.

    Keyword arguments:
    - id (string; optional): The ID used to identify this component in Dash callbacks.
    - text (string; required): The text to be labeled for NER.
    - entities (list; optional): List of already labeled entities. Each entity should be 
      a dictionary with keys: 'id', 'text', 'label', 'start', 'end'.
    - labelTypes (list; optional): List of available label types for entity labeling.
      Default: ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS']
    """
    
    @_explicitize_args
    def __init__(self,
                 id=Component.UNDEFINED,
                 text=Component.REQUIRED,
                 entities=Component.UNDEFINED,
                 labelTypes=Component.UNDEFINED,
                 **kwargs):
        self._prop_names = ['id', 'text', 'entities', 'labelTypes']
        self._type = 'NERLabeler'
        self._namespace = 'dash_ner_labeler'
        self._valid_wildcard_attributes = []
        self.available_properties = ['id', 'text', 'entities', 'labelTypes']
        self.available_wildcard_properties = []
        
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)
        args = {k: _locals[k] for k in _explicit_args if k != 'self'}
        
        for k in ['text']:
            if k not in args:
                raise TypeError('Required argument `{}` was not specified.'.format(k))
        
        super(NERLabeler, self).__init__(**args)


# Set component metadata
NERLabeler._prop_names = ['id', 'text', 'entities', 'labelTypes']
NERLabeler._type = 'NERLabeler'
NERLabeler._namespace = 'dash_ner_labeler'

# Load metadata
_current_path = os.path.dirname(os.path.abspath(__file__))

# Try to load metadata from build directory
_metadata_path = os.path.join(_current_path, '..', 'build', 'metadata.json')
if os.path.exists(_metadata_path):
    with open(_metadata_path) as f:
        _metadata = json.load(f)
        NERLabeler._prop_names = _metadata.get('props', {}).get('children', {}).get('NERLabeler', {}).get('props', NERLabeler._prop_names)
else:
    # Fallback metadata
    _metadata = {
        'NERLabeler': {
            'props': {
                'id': {'type': 'string', 'required': False},
                'text': {'type': 'string', 'required': True},
                'entities': {'type': 'list', 'required': False},
                'labelTypes': {'type': 'list', 'required': False}
            }
        }
    }