#!/usr/bin/env python3
"""
BigQuery Setup Script for NER Labeler
=====================================

This script helps set up BigQuery integration for the NER labeler by:
1. Creating sample configuration files
2. Setting up sample data
3. Testing the connection
4. Creating initial tables and schema

Usage:
    python setup_bigquery.py --project-id YOUR_PROJECT_ID
    python setup_bigquery.py --project-id YOUR_PROJECT_ID --create-sample-data
    python setup_bigquery.py --test-connection
"""

import argparse
import json
import sys
import pandas as pd
from datetime import datetime
from bigquery_integration import BigQueryNERManager

def create_config_file(project_id: str, dataset_id: str = "ner_labeling", credentials_path: str = None):
    """Create BigQuery configuration file"""
    config = {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "credentials_path": credentials_path,
        "default_batch_size": 10,
        "auto_assign_texts": True,
        "require_confidence_scores": False,
        "default_label_types": [
            "PERSON", "ORGANIZATION", "LOCATION", "MISCELLANEOUS", 
            "DATE", "MONEY", "PRODUCT", "EVENT"
        ]
    }
    
    config_file = "bigquery_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created configuration file: {config_file}")
    print(f"📝 Project ID: {project_id}")
    print(f"📝 Dataset ID: {dataset_id}")
    
    if not credentials_path:
        print("⚠️  No credentials path specified. Make sure to:")
        print("   1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   2. Or run: gcloud auth application-default login")
        print("   3. Or update the config file with your service account key path")

def create_sample_data(manager: BigQueryNERManager):
    """Create sample text data for testing"""
    sample_texts = pd.DataFrame([
        {
            "text_id": "tech_001",
            "text_content": "Apple Inc. announced that Tim Cook will continue as CEO through 2025. The Cupertino-based company reported record revenue of $394 billion in fiscal year 2022.",
            "source": "tech_news",
            "metadata": json.dumps({"category": "technology", "date": "2023-01-15"}),
            "priority": 1
        },
        {
            "text_id": "tech_002",
            "text_content": "Microsoft Corporation's Azure cloud platform grew 40% year-over-year. CEO Satya Nadella highlighted the success during the quarterly earnings call from Redmond, Washington.",
            "source": "earnings_reports",
            "metadata": json.dumps({"category": "business", "date": "2023-02-10"}),
            "priority": 2
        },
        {
            "text_id": "tech_003",
            "text_content": "Google's parent company Alphabet Inc. invested $10 billion in AI research in 2022. The Mountain View company is competing with OpenAI and other AI startups.",
            "source": "ai_news",
            "metadata": json.dumps({"category": "artificial_intelligence", "date": "2023-03-05"}),
            "priority": 3
        },
        {
            "text_id": "finance_001",
            "text_content": "JPMorgan Chase reported net income of $37.7 billion in 2022. CEO Jamie Dimon praised the bank's resilient performance amid economic uncertainty.",
            "source": "financial_reports", 
            "metadata": json.dumps({"category": "finance", "date": "2023-01-20"}),
            "priority": 2
        },
        {
            "text_id": "healthcare_001",
            "text_content": "Pfizer Inc. announced positive results from its Alzheimer's drug trial. The New York-based pharmaceutical company expects FDA approval by end of 2024.",
            "source": "healthcare_news",
            "metadata": json.dumps({"category": "healthcare", "date": "2023-04-12"}),
            "priority": 1
        },
        {
            "text_id": "sports_001",
            "text_content": "The Los Angeles Lakers signed a new player development coach. LeBron James welcomed the addition, stating it will help young players in their training facility.",
            "source": "sports_news",
            "metadata": json.dumps({"category": "sports", "date": "2023-05-08"}),
            "priority": 3
        },
        {
            "text_id": "automotive_001", 
            "text_content": "Tesla Inc. delivered over 1.3 million vehicles in 2022. Elon Musk announced plans to expand the Austin, Texas Gigafactory and hire 2,000 new employees.",
            "source": "automotive_news",
            "metadata": json.dumps({"category": "automotive", "date": "2023-01-03"}),
            "priority": 2
        },
        {
            "text_id": "retail_001",
            "text_content": "Amazon.com Inc. reported strong holiday sales with $149.2 billion in revenue for Q4 2022. Andy Jassy noted improvements in their Seattle-based logistics network.",
            "source": "retail_reports",
            "metadata": json.dumps({"category": "retail", "date": "2023-02-02"}),
            "priority": 1
        }
    ])
    
    success = manager.bulk_upload_texts(sample_texts)
    
    if success:
        print(f"✅ Created {len(sample_texts)} sample texts in BigQuery")
        print("📝 Sample texts include:")
        for _, row in sample_texts.iterrows():
            print(f"   - {row['text_id']}: {row['text_content'][:50]}...")
    else:
        print("❌ Failed to create sample texts")
        
    return success

def test_connection(project_id: str):
    """Test BigQuery connection and display status"""
    try:
        print(f"🔌 Testing connection to {project_id}...")
        
        # Initialize manager
        manager = BigQueryNERManager(project_id=project_id)
        print("✅ BigQuery connection established")
        
        # Test loading texts
        texts_df = manager.load_texts_for_annotation(limit=3)
        print(f"✅ Successfully loaded {len(texts_df)} texts")
        
        # Test user statistics
        stats = manager.get_user_statistics()
        print(f"✅ Retrieved statistics for {stats['total_users']} users")
        
        # Test annotation history
        history_df = manager.get_annotation_history()
        print(f"✅ Retrieved {len(history_df)} history records")
        
        print("🎉 All BigQuery operations working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("🔍 Common solutions:")
        print("   1. Check your project ID")
        print("   2. Verify authentication (gcloud auth login)")
        print("   3. Ensure BigQuery API is enabled")
        print("   4. Check IAM permissions")
        return False

def create_sample_annotations(manager: BigQueryNERManager):
    """Create sample annotations for testing"""
    sample_annotations = [
        {
            "text_id": "tech_001",
            "entities": [
                {"id": 1, "text": "Apple Inc.", "label": "ORGANIZATION", "start": 0, "end": 10},
                {"id": 2, "text": "Tim Cook", "label": "PERSON", "start": 25, "end": 33},
                {"id": 3, "text": "Cupertino", "label": "LOCATION", "start": 82, "end": 91},
                {"id": 4, "text": "$394 billion", "label": "MONEY", "start": 125, "end": 137},
                {"id": 5, "text": "fiscal year 2022", "label": "DATE", "start": 141, "end": 157}
            ]
        },
        {
            "text_id": "tech_002", 
            "entities": [
                {"id": 1, "text": "Microsoft Corporation", "label": "ORGANIZATION", "start": 0, "end": 21},
                {"id": 2, "text": "Azure", "label": "PRODUCT", "start": 24, "end": 29},
                {"id": 3, "text": "Satya Nadella", "label": "PERSON", "start": 72, "end": 85},
                {"id": 4, "text": "Redmond, Washington", "label": "LOCATION", "start": 144, "end": 163}
            ]
        }
    ]
    
    for sample in sample_annotations:
        success = manager.upload_annotations(
            text_id=sample["text_id"],
            entities=sample["entities"],
            user_id="demo_user_001",
            username="demo_annotator",
            session_id="setup_session_001"
        )
        
        if success:
            print(f"✅ Created {len(sample['entities'])} sample annotations for {sample['text_id']}")
        else:
            print(f"❌ Failed to create annotations for {sample['text_id']}")

def main():
    parser = argparse.ArgumentParser(description="Setup BigQuery integration for NER Labeler")
    parser.add_argument("--project-id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--dataset-id", default="ner_labeling", help="BigQuery dataset name")
    parser.add_argument("--credentials-path", help="Path to service account credentials JSON")
    parser.add_argument("--create-sample-data", action="store_true", help="Create sample texts and annotations")
    parser.add_argument("--test-connection", action="store_true", help="Test BigQuery connection")
    parser.add_argument("--create-config-only", action="store_true", help="Only create configuration file")
    
    args = parser.parse_args()
    
    print("🔧 BigQuery NER Labeler Setup")
    print("=" * 40)
    
    # Create configuration file
    create_config_file(args.project_id, args.dataset_id, args.credentials_path)
    
    if args.create_config_only:
        print("✅ Configuration file created. Update it with your settings and run again.")
        return
    
    try:
        # Initialize BigQuery manager
        manager = BigQueryNERManager(
            project_id=args.project_id,
            dataset_id=args.dataset_id,
            credentials_path=args.credentials_path
        )
        
        print("✅ BigQuery dataset and tables initialized")
        
        # Create sample data if requested
        if args.create_sample_data:
            print("\n📝 Creating sample data...")
            create_sample_data(manager)
            
            # Create sample annotations
            print("\n🏷️ Creating sample annotations...")
            create_sample_annotations(manager)
        
        # Test connection if requested
        if args.test_connection:
            print("\n🧪 Testing connection...")
            test_connection(args.project_id)
        
        print("\n🎉 Setup completed successfully!")
        print("🚀 You can now run: python bigquery_demo.py")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n🔍 Troubleshooting steps:")
        print("   1. Verify your Google Cloud project ID")
        print("   2. Check authentication: gcloud auth application-default login")
        print("   3. Enable BigQuery API in your project")
        print("   4. Verify IAM permissions (BigQuery Admin or Editor)")
        sys.exit(1)

if __name__ == "__main__":
    main()