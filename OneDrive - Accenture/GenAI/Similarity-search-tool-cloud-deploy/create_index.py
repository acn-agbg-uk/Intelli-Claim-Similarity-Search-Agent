from google.cloud import aiplatform

PROJECT_ID = "ai-boardroom-01"
REGION = "us-central1"
INDEX_DISPLAY_NAME = "claims_similarity_index_v2"
GCS_JSONL_URI = "gs://agent-demo-similarity-search-model/claim_embeddings/claim_embeddings.jsonl"

# Initialize Vertex AI
aiplatform.init(project=PROJECT_ID, location=REGION)

# Create a new Matching Engine index
index = aiplatform.MatchingEngineIndex.create(
    display_name=INDEX_DISPLAY_NAME,
    contents=[GCS_JSONL_URI],          # your JSONL with embeddings
    metadata_schema_uri="gs://google-cloud-aiplatform/schema/matchingengine/metadata/nearest_neighbor_search_1.0.0.yaml",
    metadata={
        "config": {
            "dimensions": 768,                 # embedding vector size
            "approximateNeighborsCount": 150,  # adjust as needed
            "distanceMeasureType": "DOT_PRODUCT_DISTANCE",  # or "COSINE_DISTANCE"
            "shardSize": "SHARD_SIZE_MEDIUM"
        }
    },
    update_method="BATCH_UPDATE"
)

print("Index creation started. Index resource name:", index.resource_name)
