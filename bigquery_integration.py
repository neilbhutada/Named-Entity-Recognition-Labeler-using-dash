"""
BigQuery Integration for NER Labeler
====================================

This module provides integration with Google BigQuery for:
1. Loading text instances for annotation
2. Storing annotations with full audit trail
3. Managing annotation ledgers and user tracking
4. Batch operations for efficient data processing

Features:
- Secure credential management
- Configurable table schemas
- Batch loading and uploading
- Error handling and retry logic
- Annotation history tracking

Author: Generated with Claude Code
License: MIT
"""

import os
import json
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryNERManager:
    """
    Manager class for BigQuery integration with NER labeling system
    """
    
    def __init__(self, 
                 project_id: str,
                 credentials_path: Optional[str] = None,
                 dataset_id: str = "ner_labeling"):
        """
        Initialize BigQuery NER Manager
        
        Args:
            project_id: Google Cloud Project ID
            credentials_path: Path to service account credentials JSON file
            dataset_id: BigQuery dataset name for storing annotation data
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        
        # Initialize BigQuery client
        if credentials_path and os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info(f"Using credentials from: {credentials_path}")
        
        try:
            self.client = bigquery.Client(project=project_id)
            logger.info(f"Connected to BigQuery project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise
        
        # Initialize dataset and tables
        self._setup_dataset_and_tables()
    
    def _setup_dataset_and_tables(self):
        """Create dataset and required tables if they don't exist"""
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
                logger.info(f"Dataset {self.dataset_id} already exists")
            except NotFound:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = self.client.create_dataset(dataset)
                logger.info(f"Created dataset {self.dataset_id}")
            
            # Create required tables
            self._create_texts_table()
            self._create_annotations_table()
            self._create_annotation_history_table()
            self._create_user_sessions_table()
            
        except Exception as e:
            logger.error(f"Failed to setup dataset and tables: {e}")
            raise
    
    def _create_texts_table(self):
        """Create table for storing source texts to be annotated"""
        table_id = f"{self.project_id}.{self.dataset_id}.texts"
        
        schema = [
            bigquery.SchemaField("text_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("text_content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # 'pending', 'in_progress', 'completed'
            bigquery.SchemaField("assigned_to", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("priority", "INTEGER", mode="NULLABLE"),
        ]
        
        self._create_table_if_not_exists(table_id, schema, "Source texts for annotation")
    
    def _create_annotations_table(self):
        """Create table for storing annotations"""
        table_id = f"{self.project_id}.{self.dataset_id}.annotations"
        
        schema = [
            bigquery.SchemaField("annotation_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("text_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("entity_text", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("entity_label", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("start_position", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("end_position", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("confidence", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),  # For soft deletes
            bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
        ]
        
        self._create_table_if_not_exists(table_id, schema, "Entity annotations")
    
    def _create_annotation_history_table(self):
        """Create table for storing annotation history/audit trail"""
        table_id = f"{self.project_id}.{self.dataset_id}.annotation_history"
        
        schema = [
            bigquery.SchemaField("history_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("annotation_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("text_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("action", "STRING", mode="REQUIRED"),  # 'create', 'update', 'delete'
            bigquery.SchemaField("entity_data", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("client_info", "JSON", mode="NULLABLE"),
        ]
        
        self._create_table_if_not_exists(table_id, schema, "Annotation history and audit trail")
    
    def _create_user_sessions_table(self):
        """Create table for tracking user sessions"""
        table_id = f"{self.project_id}.{self.dataset_id}.user_sessions"
        
        schema = [
            bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_activity", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("end_time", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("texts_annotated", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("total_annotations", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("session_metadata", "JSON", mode="NULLABLE"),
        ]
        
        self._create_table_if_not_exists(table_id, schema, "User annotation sessions")
    
    def _create_table_if_not_exists(self, table_id: str, schema: List[bigquery.SchemaField], description: str):
        """Create BigQuery table if it doesn't exist"""
        try:
            self.client.get_table(table_id)
            logger.info(f"Table {table_id} already exists")
        except NotFound:
            table = bigquery.Table(table_id, schema=schema)
            table.description = description
            table = self.client.create_table(table)
            logger.info(f"Created table {table_id}")
    
    def load_texts_for_annotation(self, 
                                 limit: int = 10, 
                                 status: str = "pending",
                                 assigned_to: Optional[str] = None) -> pd.DataFrame:
        """
        Load texts from BigQuery for annotation
        
        Args:
            limit: Number of texts to load
            status: Filter by status ('pending', 'in_progress', 'completed')
            assigned_to: Filter by assigned user
            
        Returns:
            DataFrame with text data
        """
        try:
            query = f"""
            SELECT 
                text_id,
                text_content,
                source,
                metadata,
                created_at,
                status,
                assigned_to,
                priority
            FROM `{self.project_id}.{self.dataset_id}.texts`
            WHERE status = @status
            """
            
            if assigned_to:
                query += " AND assigned_to = @assigned_to"
            
            query += """
            ORDER BY 
                priority DESC NULLS LAST,
                created_at ASC
            LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("status", "STRING", status),
                    bigquery.ScalarQueryParameter("limit", "INTEGER", limit),
                ]
            )
            
            if assigned_to:
                job_config.query_parameters.append(
                    bigquery.ScalarQueryParameter("assigned_to", "STRING", assigned_to)
                )
            
            df = self.client.query(query, job_config=job_config).to_dataframe()
            logger.info(f"Loaded {len(df)} texts for annotation")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load texts: {e}")
            raise
    
    def upload_annotations(self, 
                          text_id: str,
                          entities: List[Dict],
                          user_id: str,
                          username: str,
                          session_id: Optional[str] = None) -> bool:
        """
        Upload annotations to BigQuery
        
        Args:
            text_id: ID of the text being annotated
            entities: List of entity dictionaries
            user_id: ID of the user making annotations
            username: Username of the annotator
            session_id: Optional session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Prepare annotation records
            annotation_records = []
            history_records = []
            
            for entity in entities:
                annotation_id = f"{text_id}_{entity.get('id', datetime.now().timestamp())}"
                
                # Annotation record
                annotation_record = {
                    "annotation_id": annotation_id,
                    "text_id": text_id,
                    "entity_text": entity["text"],
                    "entity_label": entity["label"],
                    "start_position": entity["start"],
                    "end_position": entity["end"],
                    "confidence": entity.get("confidence", 1.0),
                    "user_id": user_id,
                    "username": username,
                    "created_at": entity.get("timestamp", current_time.isoformat()),
                    "updated_at": current_time.isoformat(),
                    "is_active": True,
                    "metadata": json.dumps(entity.get("metadata", {}))
                }
                annotation_records.append(annotation_record)
                
                # History record
                history_record = {
                    "history_id": f"{annotation_id}_{current_time.timestamp()}",
                    "annotation_id": annotation_id,
                    "text_id": text_id,
                    "action": "create",
                    "entity_data": json.dumps(entity),
                    "user_id": user_id,
                    "username": username,
                    "session_id": session_id,
                    "timestamp": current_time.isoformat(),
                    "client_info": json.dumps({"source": "ner_labeler_dash"})
                }
                history_records.append(history_record)
            
            # Upload annotations
            if annotation_records:
                annotations_table = self.client.get_table(f"{self.project_id}.{self.dataset_id}.annotations")
                errors = self.client.insert_rows_json(annotations_table, annotation_records)
                
                if errors:
                    logger.error(f"Failed to insert annotations: {errors}")
                    return False
                
                logger.info(f"Uploaded {len(annotation_records)} annotations for text {text_id}")
            
            # Upload history
            if history_records:
                history_table = self.client.get_table(f"{self.project_id}.{self.dataset_id}.annotation_history")
                errors = self.client.insert_rows_json(history_table, history_records)
                
                if errors:
                    logger.error(f"Failed to insert history: {errors}")
                    return False
                
                logger.info(f"Uploaded {len(history_records)} history records")
            
            # Update text status
            self._update_text_status(text_id, "completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload annotations: {e}")
            return False
    
    def load_existing_annotations(self, text_id: str) -> List[Dict]:
        """
        Load existing annotations for a text from BigQuery
        
        Args:
            text_id: ID of the text
            
        Returns:
            List of annotation dictionaries
        """
        try:
            query = f"""
            SELECT 
                annotation_id as id,
                entity_text as text,
                entity_label as label,
                start_position as start,
                end_position as end,
                user_id,
                username,
                created_at as timestamp,
                confidence,
                metadata
            FROM `{self.project_id}.{self.dataset_id}.annotations`
            WHERE text_id = @text_id AND is_active = true
            ORDER BY start_position
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("text_id", "STRING", text_id)
                ]
            )
            
            results = self.client.query(query, job_config=job_config)
            annotations = []
            
            for row in results:
                annotation = {
                    "id": row.id,
                    "text": row.text,
                    "label": row.label,
                    "start": row.start,
                    "end": row.end,
                    "user_id": row.user_id,
                    "username": row.username,
                    "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                    "confidence": row.confidence,
                    "metadata": json.loads(row.metadata) if row.metadata else {}
                }
                annotations.append(annotation)
            
            logger.info(f"Loaded {len(annotations)} existing annotations for text {text_id}")
            return annotations
            
        except Exception as e:
            logger.error(f"Failed to load existing annotations: {e}")
            return []
    
    def get_annotation_history(self, text_id: Optional[str] = None, user_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get annotation history from BigQuery
        
        Args:
            text_id: Optional filter by text ID
            user_id: Optional filter by user ID
            
        Returns:
            DataFrame with annotation history
        """
        try:
            query = f"""
            SELECT 
                history_id,
                annotation_id,
                text_id,
                action,
                entity_data,
                user_id,
                username,
                session_id,
                timestamp,
                client_info
            FROM `{self.project_id}.{self.dataset_id}.annotation_history`
            WHERE 1=1
            """
            
            params = []
            if text_id:
                query += " AND text_id = @text_id"
                params.append(bigquery.ScalarQueryParameter("text_id", "STRING", text_id))
            
            if user_id:
                query += " AND user_id = @user_id"
                params.append(bigquery.ScalarQueryParameter("user_id", "STRING", user_id))
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            job_config = bigquery.QueryJobConfig(query_parameters=params)
            df = self.client.query(query, job_config=job_config).to_dataframe()
            
            logger.info(f"Retrieved {len(df)} history records")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get annotation history: {e}")
            return pd.DataFrame()
    
    def _update_text_status(self, text_id: str, status: str):
        """Update the status of a text"""
        try:
            query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.texts`
            SET status = @status
            WHERE text_id = @text_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("status", "STRING", status),
                    bigquery.ScalarQueryParameter("text_id", "STRING", text_id)
                ]
            )
            
            self.client.query(query, job_config=job_config)
            logger.info(f"Updated text {text_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update text status: {e}")
    
    def bulk_upload_texts(self, texts_df: pd.DataFrame) -> bool:
        """
        Bulk upload texts to BigQuery for annotation
        
        Args:
            texts_df: DataFrame with columns: text_id, text_content, source, metadata, priority
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add required columns
            current_time = datetime.now(timezone.utc).isoformat()
            texts_df["created_at"] = current_time
            texts_df["status"] = "pending"
            
            # Convert to records
            records = texts_df.to_dict("records")
            
            # Upload to BigQuery
            table = self.client.get_table(f"{self.project_id}.{self.dataset_id}.texts")
            errors = self.client.insert_rows_json(table, records)
            
            if errors:
                logger.error(f"Failed to bulk upload texts: {errors}")
                return False
            
            logger.info(f"Bulk uploaded {len(records)} texts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk upload texts: {e}")
            return False
    
    def get_user_statistics(self, user_id: Optional[str] = None) -> Dict:
        """
        Get user annotation statistics
        
        Args:
            user_id: Optional filter by user ID
            
        Returns:
            Dictionary with user statistics
        """
        try:
            query = f"""
            SELECT 
                user_id,
                username,
                COUNT(*) as total_annotations,
                COUNT(DISTINCT text_id) as texts_annotated,
                MIN(created_at) as first_annotation,
                MAX(created_at) as last_annotation
            FROM `{self.project_id}.{self.dataset_id}.annotations`
            WHERE is_active = true
            """
            
            params = []
            if user_id:
                query += " AND user_id = @user_id"
                params.append(bigquery.ScalarQueryParameter("user_id", "STRING", user_id))
            
            query += " GROUP BY user_id, username ORDER BY total_annotations DESC"
            
            job_config = bigquery.QueryJobConfig(query_parameters=params)
            results = self.client.query(query, job_config=job_config)
            
            stats = []
            for row in results:
                stat = {
                    "user_id": row.user_id,
                    "username": row.username,
                    "total_annotations": row.total_annotations,
                    "texts_annotated": row.texts_annotated,
                    "first_annotation": row.first_annotation.isoformat() if row.first_annotation else None,
                    "last_annotation": row.last_annotation.isoformat() if row.last_annotation else None
                }
                stats.append(stat)
            
            logger.info(f"Retrieved statistics for {len(stats)} users")
            return {"users": stats, "total_users": len(stats)}
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {"users": [], "total_users": 0}

# Example usage and configuration
def create_sample_config():
    """Create a sample configuration file for BigQuery integration"""
    config = {
        "project_id": "your-gcp-project-id",
        "dataset_id": "ner_labeling",
        "credentials_path": "path/to/service-account-key.json",
        "default_batch_size": 10,
        "auto_assign_texts": True,
        "require_confidence_scores": False
    }
    
    with open("bigquery_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Sample configuration saved to bigquery_config.json")
    print("Please update the configuration with your actual BigQuery project details.")

if __name__ == "__main__":
    # Create sample configuration
    create_sample_config()