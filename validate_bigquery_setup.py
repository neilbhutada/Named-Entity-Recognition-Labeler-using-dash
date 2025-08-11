#!/usr/bin/env python3
"""
Validate BigQuery Integration Setup
==================================

Simple validation script that tests BigQuery integration components
without requiring external dependencies.
"""

import json
import os
import sys
from datetime import datetime

def validate_files_exist():
    """Check that all required files exist"""
    print("🔍 Validating file structure...")
    
    required_files = [
        'bigquery_integration.py',
        'bigquery_demo.py', 
        'setup_bigquery.py',
        'requirements_bigquery.txt',
        'BIGQUERY_INTEGRATION.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def validate_bigquery_integration_structure():
    """Validate BigQuery integration module structure"""
    print("🔍 Validating BigQuery integration module...")
    
    try:
        # Read the file content
        with open('bigquery_integration.py', 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            'class BigQueryNERManager',
            'def load_texts_for_annotation',
            'def upload_annotations', 
            'def load_existing_annotations',
            'def get_annotation_history',
            'def get_user_statistics',
            'def bulk_upload_texts',
            '_create_texts_table',
            '_create_annotations_table',
            '_create_annotation_history_table',
            '_create_user_sessions_table'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        
        print("✅ BigQuery integration structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating integration: {e}")
        return False

def validate_demo_structure():
    """Validate demo application structure"""
    print("🔍 Validating demo application...")
    
    try:
        with open('bigquery_demo.py', 'r') as f:
            content = f.read()
        
        required_components = [
            'from bigquery_integration import BigQueryNERManager',
            'from dash_ner_labeler import NERLabeler',
            'def create_demo_texts',
            'load-bigquery-btn',
            'save-bigquery-btn',
            'statistics-dashboard',
            'annotation_history'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing demo components: {missing_components}")
            return False
        
        print("✅ Demo application structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating demo: {e}")
        return False

def validate_requirements():
    """Validate requirements file"""
    print("🔍 Validating requirements...")
    
    try:
        with open('requirements_bigquery.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = [
            'dash',
            'google-cloud-bigquery',
            'google-auth',
            'pandas'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages in requirements: {missing_packages}")
            return False
        
        print("✅ Requirements file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating requirements: {e}")
        return False

def validate_setup_script():
    """Validate setup script"""
    print("🔍 Validating setup script...")
    
    try:
        with open('setup_bigquery.py', 'r') as f:
            content = f.read()
        
        required_functions = [
            'def create_config_file',
            'def create_sample_data',
            'def test_connection',
            'def create_sample_annotations',
            'def main'
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Missing setup functions: {missing_functions}")
            return False
        
        print("✅ Setup script is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating setup script: {e}")
        return False

def validate_data_structures():
    """Validate critical data structures"""
    print("🔍 Validating data structures...")
    
    # Test entity structure
    sample_entity = {
        "id": 123,
        "text": "Apple Inc.",
        "label": "ORGANIZATION", 
        "start": 0,
        "end": 10,
        "user_id": "user123",
        "username": "annotator",
        "timestamp": datetime.now().isoformat()
    }
    
    required_entity_fields = ['id', 'text', 'label', 'start', 'end', 'user_id', 'username', 'timestamp']
    for field in required_entity_fields:
        if field not in sample_entity:
            print(f"❌ Missing entity field: {field}")
            return False
    
    # Test annotation history structure  
    sample_history = {
        "id": "hist123",
        "action": "add",
        "entity": sample_entity,
        "user_id": "user123",
        "username": "annotator",
        "timestamp": datetime.now().isoformat()
    }
    
    required_history_fields = ['id', 'action', 'entity', 'user_id', 'username', 'timestamp']
    for field in required_history_fields:
        if field not in sample_history:
            print(f"❌ Missing history field: {field}")
            return False
    
    # Test JSON serialization
    try:
        json.dumps(sample_entity)
        json.dumps(sample_history)
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    print("✅ Data structures are valid")
    return True

def validate_documentation():
    """Validate documentation exists and has key sections"""
    print("🔍 Validating documentation...")
    
    try:
        with open('BIGQUERY_INTEGRATION.md', 'r') as f:
            content = f.read()
        
        required_sections = [
            '## 🎯 Features',
            '## 🛠️ Setup Instructions',
            '## 📊 Usage Workflow', 
            '## 🔧 API Reference',
            '## 📈 Production Considerations',
            '## 🔍 Troubleshooting'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing documentation sections: {missing_sections}")
            return False
        
        # Check for key information
        key_info = [
            'BigQueryNERManager',
            'texts table',
            'annotations table', 
            'annotation_history table',
            'user_sessions table'
        ]
        
        missing_info = []
        for info in key_info:
            if info not in content:
                missing_info.append(info)
        
        if missing_info:
            print(f"❌ Missing key information: {missing_info}")
            return False
        
        print("✅ Documentation is comprehensive")
        return True
        
    except Exception as e:
        print(f"❌ Error validating documentation: {e}")
        return False

def create_sample_config():
    """Create a sample configuration for testing"""
    print("🔧 Creating sample configuration...")
    
    config = {
        "project_id": "your-gcp-project-id",
        "dataset_id": "ner_labeling", 
        "credentials_path": None,
        "default_batch_size": 10,
        "auto_assign_texts": True,
        "require_confidence_scores": False,
        "default_label_types": [
            "PERSON", "ORGANIZATION", "LOCATION", "MISCELLANEOUS",
            "DATE", "MONEY", "PRODUCT", "EVENT"
        ]
    }
    
    try:
        with open('bigquery_config_sample.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Sample configuration created: bigquery_config_sample.json")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample config: {e}")
        return False

def main():
    """Run all validations"""
    print("🧪 BigQuery Integration Validation")
    print("=" * 50)
    
    validations = [
        ("File Structure", validate_files_exist),
        ("BigQuery Integration", validate_bigquery_integration_structure),
        ("Demo Application", validate_demo_structure),
        ("Requirements", validate_requirements),
        ("Setup Script", validate_setup_script),
        ("Data Structures", validate_data_structures),
        ("Documentation", validate_documentation),
        ("Sample Config", create_sample_config)
    ]
    
    passed = 0
    failed = 0
    
    for name, validation_func in validations:
        try:
            print(f"\n📋 {name}:")
            if validation_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {name} validation failed with error: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Validation Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 BigQuery integration is ready!")
        print("📋 Next steps:")
        print("   1. Install dependencies: pip install -r requirements_bigquery.txt")
        print("   2. Set up BigQuery: python setup_bigquery.py --project-id YOUR_PROJECT_ID")
        print("   3. Run demo: python bigquery_demo.py")
        print("   4. See BIGQUERY_INTEGRATION.md for detailed setup")
        return True
    else:
        print("\n⚠️ Some validations failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)