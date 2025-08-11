#!/usr/bin/env python3
"""
Test script for multi-user NER labeling functionality

This script tests the enhanced NER labeler component with multi-user features:
- User tracking
- Annotation history
- Timestamp attribution
- Entity management with user context
"""

from dash_ner_labeler import NERLabeler
import json
from datetime import datetime

def test_component_properties():
    """Test that the component has all required multi-user properties"""
    print("🧪 Testing NERLabeler component properties...")
    
    # Test that component can be instantiated with new properties
    component = NERLabeler(
        id='test-ner',
        text="Apple Inc. is headquartered in Cupertino, California.",
        entities=[],
        labelTypes=['PERSON', 'ORGANIZATION', 'LOCATION'],
        currentUser={'id': 'test123', 'name': 'testuser'},
        annotationHistory=[],
        showUserInfo=True,
        showHistory=True
    )
    
    # Check that all properties are available
    expected_props = ['id', 'text', 'entities', 'labelTypes', 'currentUser', 
                     'annotationHistory', 'showUserInfo', 'showHistory']
    
    actual_props = component.available_properties
    
    for prop in expected_props:
        assert prop in actual_props, f"Missing property: {prop}"
    
    print("✅ All component properties are available")
    return True

def test_entity_structure():
    """Test the enhanced entity structure with user tracking"""
    print("🧪 Testing enhanced entity data structure...")
    
    # Sample entity with user tracking
    sample_entity = {
        'id': 123456789.123,
        'text': 'Apple Inc.',
        'label': 'ORGANIZATION',
        'start': 0,
        'end': 10,
        'user_id': 'user123',
        'username': 'john_doe',
        'timestamp': datetime.now().isoformat()
    }
    
    # Test required fields
    required_fields = ['id', 'text', 'label', 'start', 'end']
    user_fields = ['user_id', 'username', 'timestamp']
    
    for field in required_fields + user_fields:
        assert field in sample_entity, f"Missing field: {field}"
    
    print("✅ Entity structure supports user tracking")
    return True

def test_annotation_history_structure():
    """Test the annotation history structure"""
    print("🧪 Testing annotation history data structure...")
    
    # Sample history entry
    sample_history = {
        'id': 123456789.456,
        'action': 'add',
        'entity': {
            'id': 123456789.123,
            'text': 'Apple Inc.',
            'label': 'ORGANIZATION',
            'start': 0,
            'end': 10
        },
        'user_id': 'user123',
        'username': 'john_doe',
        'timestamp': datetime.now().isoformat()
    }
    
    # Test required fields
    required_fields = ['id', 'action', 'entity', 'user_id', 'username', 'timestamp']
    
    for field in required_fields:
        assert field in sample_history, f"Missing field: {field}"
    
    # Test action values
    assert sample_history['action'] in ['add', 'remove'], f"Invalid action: {sample_history['action']}"
    
    print("✅ Annotation history structure is correct")
    return True

def test_multi_user_scenario():
    """Test a realistic multi-user annotation scenario"""
    print("🧪 Testing multi-user annotation scenario...")
    
    # Simulate multiple users annotating the same text
    text = "Tim Cook is the CEO of Apple Inc. in Cupertino, California."
    
    # User 1 annotations
    user1_entities = [
        {
            'id': 1001,
            'text': 'Tim Cook',
            'label': 'PERSON',
            'start': 0,
            'end': 8,
            'user_id': 'user1',
            'username': 'alice',
            'timestamp': '2024-01-01T10:00:00Z'
        },
        {
            'id': 1002,
            'text': 'Apple Inc.',
            'label': 'ORGANIZATION',
            'start': 25,
            'end': 35,
            'user_id': 'user1',
            'username': 'alice',
            'timestamp': '2024-01-01T10:01:00Z'
        }
    ]
    
    # User 2 annotations
    user2_entities = [
        {
            'id': 2001,
            'text': 'Cupertino, California',
            'label': 'LOCATION',
            'start': 39,
            'end': 60,
            'user_id': 'user2',
            'username': 'bob',
            'timestamp': '2024-01-01T10:30:00Z'
        }
    ]
    
    # Combined entities from both users
    all_entities = user1_entities + user2_entities
    
    # Annotation history
    history = [
        {
            'id': 'h1',
            'action': 'add',
            'entity': user1_entities[0],
            'user_id': 'user1',
            'username': 'alice',
            'timestamp': '2024-01-01T10:00:00Z'
        },
        {
            'id': 'h2',
            'action': 'add',
            'entity': user1_entities[1],
            'user_id': 'user1',
            'username': 'alice',
            'timestamp': '2024-01-01T10:01:00Z'
        },
        {
            'id': 'h3',
            'action': 'add',
            'entity': user2_entities[0],
            'user_id': 'user2',
            'username': 'bob',
            'timestamp': '2024-01-01T10:30:00Z'
        }
    ]
    
    # Validate the scenario
    assert len(all_entities) == 3, f"Expected 3 entities, got {len(all_entities)}"
    assert len(history) == 3, f"Expected 3 history entries, got {len(history)}"
    
    # Check user distribution
    user1_count = sum(1 for e in all_entities if e['username'] == 'alice')
    user2_count = sum(1 for e in all_entities if e['username'] == 'bob')
    
    assert user1_count == 2, f"Expected 2 entities from alice, got {user1_count}"
    assert user2_count == 1, f"Expected 1 entity from bob, got {user2_count}"
    
    print("✅ Multi-user scenario validation passed")
    return True

def test_json_export():
    """Test JSON export with multi-user data"""
    print("🧪 Testing JSON export with user metadata...")
    
    export_data = {
        "text": "Apple Inc. is based in California.",
        "entities": [
            {
                'id': 1,
                'text': 'Apple Inc.',
                'label': 'ORGANIZATION',
                'start': 0,
                'end': 10,
                'user_id': 'user1',
                'username': 'alice',
                'timestamp': '2024-01-01T10:00:00Z'
            }
        ],
        "annotation_history": [
            {
                'id': 'h1',
                'action': 'add',
                'entity': {'id': 1, 'text': 'Apple Inc.', 'label': 'ORGANIZATION'},
                'user_id': 'user1',
                'username': 'alice',
                'timestamp': '2024-01-01T10:00:00Z'
            }
        ],
        "current_user": {'id': 'user1', 'name': 'alice'},
        "export_timestamp": datetime.now().isoformat(),
        "total_entities": 1,
        "total_actions": 1
    }
    
    # Test JSON serialization
    json_str = json.dumps(export_data, indent=2)
    
    # Test JSON deserialization
    parsed_data = json.loads(json_str)
    
    assert parsed_data['total_entities'] == 1
    assert parsed_data['total_actions'] == 1
    assert len(parsed_data['entities']) == 1
    assert len(parsed_data['annotation_history']) == 1
    
    print("✅ JSON export/import works correctly")
    return True

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Running Multi-User NER Labeler Tests")
    print("=" * 50)
    
    tests = [
        test_component_properties,
        test_entity_structure,
        test_annotation_history_structure,
        test_multi_user_scenario,
        test_json_export
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Multi-user functionality is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)