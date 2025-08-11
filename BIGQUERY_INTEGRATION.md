# BigQuery Integration for NER Labeler

This guide explains how to integrate the NER Labeler with Google BigQuery for production-scale annotation workflows.

## 🎯 Features

### Core Capabilities
- **Text Loading**: Load text instances from BigQuery tables
- **Annotation Storage**: Store annotations with full user attribution
- **Audit Trail**: Complete history of all annotation changes
- **Multi-User Support**: Track multiple annotators working on the same dataset
- **Batch Processing**: Efficiently handle large datasets
- **Statistics**: Real-time user and annotation statistics

### BigQuery Schema
The integration creates four main tables: texts table, annotations table, annotation_history table, and user_sessions table.

#### 1. `texts` - Source texts for annotation
```sql
- text_id: STRING (unique identifier)
- text_content: STRING (the text to annotate) 
- source: STRING (data source/origin)
- metadata: JSON (additional metadata)
- created_at: TIMESTAMP
- status: STRING (pending/in_progress/completed)
- assigned_to: STRING (optional user assignment)
- priority: INTEGER (annotation priority)
```

#### 2. `annotations` - Entity annotations
```sql
- annotation_id: STRING (unique identifier)
- text_id: STRING (reference to texts table)
- entity_text: STRING (the annotated text span)
- entity_label: STRING (entity type/label)
- start_position: INTEGER (character start position)
- end_position: INTEGER (character end position)  
- confidence: FLOAT (optional confidence score)
- user_id: STRING (annotator user ID)
- username: STRING (annotator username)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- is_active: BOOLEAN (for soft deletes)
- metadata: JSON (additional annotation metadata)
```

#### 3. `annotation_history` - Complete audit trail
```sql
- history_id: STRING (unique identifier)
- annotation_id: STRING (reference to annotation)
- text_id: STRING (reference to text)
- action: STRING (create/update/delete)
- entity_data: JSON (full entity data snapshot)
- user_id: STRING (user who made the change)
- username: STRING (username who made the change)
- session_id: STRING (annotation session ID)
- timestamp: TIMESTAMP
- client_info: JSON (client/application metadata)
```

#### 4. `user_sessions` - User session tracking
```sql
- session_id: STRING (unique session identifier)
- user_id: STRING (user identifier) 
- username: STRING (username)
- start_time: TIMESTAMP
- last_activity: TIMESTAMP
- end_time: TIMESTAMP (nullable)
- texts_annotated: INTEGER
- total_annotations: INTEGER
- session_metadata: JSON
```

## 🛠️ Setup Instructions

### Prerequisites
1. **Google Cloud Project** with BigQuery API enabled
2. **Authentication** set up (service account or user credentials)
3. **IAM Permissions**: BigQuery Admin or BigQuery Data Editor

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements_bigquery.txt
```

2. **Set up authentication** (choose one):
   - **Service Account**: Download service account key JSON
   - **User Credentials**: Run `gcloud auth application-default login`
   - **Environment**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

3. **Configure BigQuery**:
```bash
# Create configuration and setup tables
python setup_bigquery.py --project-id YOUR_PROJECT_ID

# Create with sample data
python setup_bigquery.py --project-id YOUR_PROJECT_ID --create-sample-data

# Test connection
python setup_bigquery.py --project-id YOUR_PROJECT_ID --test-connection
```

4. **Update configuration**:
Edit `bigquery_config.json`:
```json
{
  "project_id": "your-gcp-project-id",
  "dataset_id": "ner_labeling",
  "credentials_path": "path/to/service-account.json",
  "default_batch_size": 10,
  "auto_assign_texts": true,
  "require_confidence_scores": false
}
```

### Running the Application

```bash
# Start BigQuery-integrated demo
python bigquery_demo.py
```

Visit: http://localhost:8053

## 📊 Usage Workflow

### 1. Load Texts from BigQuery
```python
# Load pending texts for annotation
texts_df = bq_manager.load_texts_for_annotation(
    limit=10, 
    status="pending",
    assigned_to="user123"
)
```

### 2. Annotate Texts
- Set your username in the UI
- Navigate through loaded texts
- Select text spans and assign labels
- View real-time annotation history

### 3. Save Annotations to BigQuery
```python
# Upload annotations with full audit trail
success = bq_manager.upload_annotations(
    text_id="text_001",
    entities=entities_list,
    user_id="user123", 
    username="annotator_name",
    session_id="session_uuid"
)
```

### 4. Monitor Progress
- View user statistics and progress
- Export session data
- Access complete audit trails

## 🔧 API Reference

### BigQueryNERManager Class

#### Initialization
```python
manager = BigQueryNERManager(
    project_id="your-project",
    credentials_path="path/to/creds.json",  # Optional
    dataset_id="ner_labeling"  # Optional
)
```

#### Key Methods

**Load texts for annotation:**
```python
texts_df = manager.load_texts_for_annotation(
    limit=10,
    status="pending", 
    assigned_to=None
)
```

**Upload annotations:**
```python
success = manager.upload_annotations(
    text_id="text_001",
    entities=[{
        "id": 1,
        "text": "Apple Inc.",
        "label": "ORGANIZATION", 
        "start": 0,
        "end": 10,
        "confidence": 0.95
    }],
    user_id="user123",
    username="annotator",
    session_id="session_uuid"
)
```

**Load existing annotations:**
```python
annotations = manager.load_existing_annotations("text_001")
```

**Get annotation history:**
```python
history_df = manager.get_annotation_history(
    text_id="text_001",  # Optional filter
    user_id="user123"    # Optional filter  
)
```

**Get user statistics:**
```python
stats = manager.get_user_statistics(user_id="user123")
```

**Bulk upload texts:**
```python
texts_df = pd.DataFrame([{
    "text_id": "new_text_001",
    "text_content": "Text to be annotated...",
    "source": "data_source",
    "priority": 1
}])
success = manager.bulk_upload_texts(texts_df)
```

## 📈 Production Considerations

### Performance Optimization
- **Batch Operations**: Use batch loading/uploading for large datasets
- **Indexing**: Create indexes on frequently queried columns
- **Partitioning**: Partition large tables by date or user
- **Caching**: Cache frequently accessed data

### Security Best Practices
- **Authentication**: Use service accounts with minimal required permissions
- **Data Encryption**: Enable encryption at rest and in transit
- **Audit Logging**: Monitor all BigQuery operations
- **Access Control**: Implement row-level security if needed

### Monitoring and Maintenance
- **Cost Monitoring**: Track BigQuery usage and costs
- **Data Retention**: Implement data lifecycle policies
- **Backup Strategy**: Regular exports and backups
- **Performance Monitoring**: Monitor query performance

### Scaling Considerations
- **Concurrent Users**: Design for multiple simultaneous annotators
- **Data Volume**: Plan for large text corpora and annotation volumes
- **Geographic Distribution**: Consider BigQuery regions for global teams
- **Integration**: Connect with existing data pipelines and workflows

## 🔍 Troubleshooting

### Common Issues

**Authentication Errors:**
```bash
# Set up default credentials
gcloud auth application-default login

# Or set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

**Permission Errors:**
- Verify BigQuery API is enabled
- Check IAM roles (BigQuery Admin or Data Editor required)
- Ensure service account has proper permissions

**Connection Timeouts:**
- Check network connectivity
- Verify project ID and dataset names
- Try reducing batch sizes

**Data Format Issues:**
- Ensure text data is properly encoded (UTF-8)
- Validate JSON metadata format
- Check for null values in required fields

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Example Queries

### Get annotation statistics by user:
```sql
SELECT 
  username,
  COUNT(*) as total_annotations,
  COUNT(DISTINCT text_id) as unique_texts,
  AVG(confidence) as avg_confidence
FROM `project.ner_labeling.annotations` 
WHERE is_active = true
GROUP BY username
ORDER BY total_annotations DESC
```

### Get annotation progress by date:
```sql
SELECT 
  DATE(created_at) as annotation_date,
  COUNT(*) as annotations_created,
  COUNT(DISTINCT user_id) as active_users
FROM `project.ner_labeling.annotations`
WHERE is_active = true
GROUP BY DATE(created_at)
ORDER BY annotation_date DESC
```

### Get most common entity types:
```sql
SELECT 
  entity_label,
  COUNT(*) as count,
  COUNT(DISTINCT text_id) as texts_with_label
FROM `project.ner_labeling.annotations`
WHERE is_active = true
GROUP BY entity_label
ORDER BY count DESC
```

## 🤝 Integration Examples

### Data Pipeline Integration
```python
# Example: Load texts from existing data warehouse
def load_texts_from_warehouse():
    query = """
    SELECT 
      id as text_id,
      content as text_content,
      'warehouse' as source,
      TO_JSON_STRING(metadata) as metadata,
      priority
    FROM `project.data_warehouse.documents`
    WHERE needs_annotation = true
    """
    
    df = client.query(query).to_dataframe()
    return manager.bulk_upload_texts(df)
```

### ML Pipeline Integration
```python
# Example: Export annotated data for model training
def export_training_data():
    query = """
    SELECT 
      t.text_content,
      ARRAY_AGG(STRUCT(
        a.entity_text,
        a.entity_label,
        a.start_position,
        a.end_position
      )) as entities
    FROM `project.ner_labeling.texts` t
    JOIN `project.ner_labeling.annotations` a 
      ON t.text_id = a.text_id
    WHERE t.status = 'completed' 
      AND a.is_active = true
    GROUP BY t.text_id, t.text_content
    """
    
    return client.query(query).to_dataframe()
```

## 📚 Additional Resources

- [Google Cloud BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Python Client Library](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [IAM Permissions for BigQuery](https://cloud.google.com/bigquery/docs/access-control)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)

## 🆘 Support

For issues with BigQuery integration:

1. Check the troubleshooting section above
2. Review BigQuery quotas and limits
3. Verify authentication and permissions
4. Check application logs for detailed error messages
5. Test with the provided sample data and scripts

For production deployments, consider:
- Professional Google Cloud support
- BigQuery consulting services  
- Custom implementation assistance