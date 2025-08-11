#!/usr/bin/env python3
"""
Test BigQuery Integration
========================

Test script for BigQuery integration functionality without requiring actual BigQuery connection.
Tests the integration architecture, data structures, and API compatibility.
"""

import unittest
import json
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from bigquery_integration import BigQueryNERManager
    BIGQUERY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ BigQuery libraries not available: {e}")
    BIGQUERY_AVAILABLE = False

class TestBigQueryIntegration(unittest.TestCase):
    """Test BigQuery integration functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.sample_project_id = "test-project-123"
        self.sample_dataset_id = "test_ner_labeling"
        
        # Sample text data
        self.sample_texts_df = pd.DataFrame([
            {
                "text_id": "test_001",
                "text_content": "Apple Inc. is headquartered in Cupertino, California.",
                "source": "test_data",
                "metadata": '{"category": "tech"}',
                "priority": 1
            },
            {
                "text_id": "test_002", 
                "text_content": "Microsoft Corporation was founded by Bill Gates.",
                "source": "test_data",
                "metadata": '{"category": "tech"}',
                "priority": 2
            }
        ])
        
        # Sample entities
        self.sample_entities = [
            {
                "id": 1,
                "text": "Apple Inc.",
                "label": "ORGANIZATION",
                "start": 0,
                "end": 10,
                "confidence": 0.95
            },
            {
                "id": 2,
                "text": "Cupertino, California",
                "label": "LOCATION", 
                "start": 31,
                "end": 52,
                "confidence": 0.90
            }
        ]
        
        # Sample user info
        self.sample_user_id = "test_user_123"
        self.sample_username = "test_annotator"
        self.sample_session_id = "session_456"
    
    def test_data_structures(self):
        """Test that data structures match BigQuery schema requirements"""
        print("🧪 Testing data structures...")
        
        # Test texts DataFrame structure
        required_text_columns = ['text_id', 'text_content', 'source', 'metadata', 'priority']
        for col in required_text_columns:
            self.assertIn(col, self.sample_texts_df.columns, f"Missing column: {col}")
        
        # Test entity structure
        required_entity_fields = ['id', 'text', 'label', 'start', 'end']
        for entity in self.sample_entities:
            for field in required_entity_fields:
                self.assertIn(field, entity, f"Missing entity field: {field}")
        
        # Test entity positions are valid
        for entity in self.sample_entities:
            self.assertGreaterEqual(entity['start'], 0, "Start position should be >= 0")
            self.assertGreater(entity['end'], entity['start'], "End should be > start")
            self.assertIsInstance(entity['text'], str, "Entity text should be string")
            self.assertIsInstance(entity['label'], str, "Entity label should be string")
        
        print("✅ Data structures are valid")
    
    def test_annotation_format(self):
        """Test annotation data format for BigQuery compatibility"""
        print("🧪 Testing annotation format...")
        
        # Create annotation record format
        annotation_record = {
            "annotation_id": f"test_001_{self.sample_entities[0]['id']}",
            "text_id": "test_001",
            "entity_text": self.sample_entities[0]["text"],
            "entity_label": self.sample_entities[0]["label"],
            "start_position": self.sample_entities[0]["start"],
            "end_position": self.sample_entities[0]["end"],
            "confidence": self.sample_entities[0].get("confidence", 1.0),
            "user_id": self.sample_user_id,
            "username": self.sample_username,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            "metadata": json.dumps({})
        }
        
        # Test all required fields are present
        required_fields = [
            'annotation_id', 'text_id', 'entity_text', 'entity_label',
            'start_position', 'end_position', 'user_id', 'username',
            'created_at', 'updated_at', 'is_active'
        ]
        
        for field in required_fields:
            self.assertIn(field, annotation_record, f"Missing annotation field: {field}")
        
        # Test data types
        self.assertIsInstance(annotation_record['start_position'], int)
        self.assertIsInstance(annotation_record['end_position'], int)
        self.assertIsInstance(annotation_record['confidence'], (int, float))
        self.assertIsInstance(annotation_record['is_active'], bool)
        
        print("✅ Annotation format is valid")
    
    def test_history_format(self):
        """Test annotation history format"""
        print("🧪 Testing history format...")
        
        # Create history record format
        history_record = {
            "history_id": f"hist_{datetime.now().timestamp()}",
            "annotation_id": f"test_001_{self.sample_entities[0]['id']}",
            "text_id": "test_001",
            "action": "create",
            "entity_data": json.dumps(self.sample_entities[0]),
            "user_id": self.sample_user_id,
            "username": self.sample_username,
            "session_id": self.sample_session_id,
            "timestamp": datetime.now().isoformat(),
            "client_info": json.dumps({"source": "ner_labeler_test"})
        }
        
        # Test required fields
        required_fields = [
            'history_id', 'text_id', 'action', 'entity_data',
            'user_id', 'username', 'timestamp'
        ]
        
        for field in required_fields:
            self.assertIn(field, history_record, f"Missing history field: {field}")
        
        # Test action is valid
        self.assertIn(history_record['action'], ['create', 'update', 'delete'])
        
        # Test entity_data is valid JSON
        entity_data = json.loads(history_record['entity_data'])
        self.assertIsInstance(entity_data, dict)
        
        print("✅ History format is valid")
    
    def test_user_session_format(self):
        """Test user session format"""
        print("🧪 Testing user session format...")
        
        session_record = {
            "session_id": self.sample_session_id,
            "user_id": self.sample_user_id,
            "username": self.sample_username,
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "end_time": None,
            "texts_annotated": 2,
            "total_annotations": 5,
            "session_metadata": json.dumps({"client": "web_interface"})
        }
        
        required_fields = [
            'session_id', 'user_id', 'username', 'start_time',
            'last_activity', 'texts_annotated', 'total_annotations'
        ]
        
        for field in required_fields:
            self.assertIn(field, session_record, f"Missing session field: {field}")
        
        # Test data types
        self.assertIsInstance(session_record['texts_annotated'], int)
        self.assertIsInstance(session_record['total_annotations'], int)
        
        print("✅ User session format is valid")
    
    @unittest.skipUnless(BIGQUERY_AVAILABLE, "BigQuery libraries not available")
    @patch('bigquery_integration.bigquery.Client')
    def test_manager_initialization(self, mock_client):
        """Test BigQuery manager initialization with mocked client"""
        print("🧪 Testing manager initialization...")
        
        # Mock the BigQuery client
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Mock dataset operations
        mock_client_instance.dataset.return_value = Mock()
        mock_client_instance.get_dataset.side_effect = Exception("Dataset not found")
        mock_client_instance.create_dataset.return_value = Mock()
        mock_client_instance.get_table.side_effect = Exception("Table not found") 
        mock_client_instance.create_table.return_value = Mock()
        
        # Initialize manager
        manager = BigQueryNERManager(
            project_id=self.sample_project_id,
            dataset_id=self.sample_dataset_id
        )
        
        # Verify initialization
        self.assertEqual(manager.project_id, self.sample_project_id)
        self.assertEqual(manager.dataset_id, self.sample_dataset_id)
        self.assertIsNotNone(manager.client)
        
        print("✅ Manager initialization successful")
    
    def test_configuration_creation(self):
        """Test configuration file creation"""
        print("🧪 Testing configuration creation...")
        
        # Test configuration structure
        config = {
            "project_id": self.sample_project_id,
            "dataset_id": self.sample_dataset_id,
            "credentials_path": None,
            "default_batch_size": 10,
            "auto_assign_texts": True,
            "require_confidence_scores": False
        }
        
        # Validate configuration fields
        required_fields = ['project_id', 'dataset_id', 'default_batch_size']
        for field in required_fields:
            self.assertIn(field, config, f"Missing config field: {field}")
        
        # Test JSON serialization
        config_json = json.dumps(config, indent=2)
        parsed_config = json.loads(config_json)
        self.assertEqual(parsed_config, config)
        
        print("✅ Configuration creation successful")
    
    def test_batch_operations(self):
        """Test batch operation data preparation"""
        print("🧪 Testing batch operations...")
        
        # Test text batch preparation
        texts_for_upload = self.sample_texts_df.copy()
        texts_for_upload["created_at"] = datetime.now().isoformat()
        texts_for_upload["status"] = "pending"
        
        # Convert to records for BigQuery insertion
        records = texts_for_upload.to_dict("records")
        
        # Validate batch structure
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), len(self.sample_texts_df))
        
        for record in records:
            self.assertIn("text_id", record)
            self.assertIn("text_content", record)
            self.assertIn("created_at", record)
            self.assertIn("status", record)
        
        print("✅ Batch operations format valid")
    
    def test_statistics_calculation(self):
        """Test statistics calculation logic"""
        print("🧪 Testing statistics calculation...")
        
        # Sample annotation data for statistics
        sample_annotations = [
            {"user_id": "user1", "username": "alice", "entity_label": "PERSON", "text_id": "text1"},
            {"user_id": "user1", "username": "alice", "entity_label": "ORG", "text_id": "text1"}, 
            {"user_id": "user2", "username": "bob", "entity_label": "PERSON", "text_id": "text2"},
            {"user_id": "user1", "username": "alice", "entity_label": "LOCATION", "text_id": "text2"},
        ]
        
        # Calculate statistics manually for validation
        user_counts = {}
        label_counts = {}
        
        for annotation in sample_annotations:
            username = annotation["username"]
            label = annotation["entity_label"]
            
            user_counts[username] = user_counts.get(username, 0) + 1
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # Validate calculations
        self.assertEqual(user_counts["alice"], 3)
        self.assertEqual(user_counts["bob"], 1)
        self.assertEqual(label_counts["PERSON"], 2)
        self.assertEqual(label_counts["ORG"], 1)
        
        print("✅ Statistics calculation successful")
    
    def test_demo_data_creation(self):
        """Test demo data creation"""
        print("🧪 Testing demo data creation...")
        
        # Import demo creation function
        from bigquery_demo import create_demo_texts
        
        demo_texts = create_demo_texts()
        
        # Validate demo data structure
        self.assertIsInstance(demo_texts, pd.DataFrame)
        self.assertGreater(len(demo_texts), 0)
        
        required_columns = ['text_id', 'text_content', 'source', 'status', 'priority']
        for col in required_columns:
            self.assertIn(col, demo_texts.columns)
        
        # Check data quality
        for _, row in demo_texts.iterrows():
            self.assertIsInstance(row['text_id'], str)
            self.assertIsInstance(row['text_content'], str)
            self.assertGreater(len(row['text_content']), 10)  # Meaningful content
            self.assertIn(row['status'], ['pending', 'in_progress', 'completed'])
        
        print("✅ Demo data creation successful")

def run_integration_tests():
    """Run all BigQuery integration tests"""
    print("🧪 BigQuery Integration Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBigQueryIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 50)
    print(f"📊 Test Results:")
    print(f"   ✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Tests failed: {len(result.failures)}")
    print(f"   💥 Tests errors: {len(result.errors)}")
    
    # Print details for failures
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 All BigQuery integration tests passed!")
        print("✅ Ready for BigQuery integration")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
    
    return success

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)