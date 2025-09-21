import json
from google.cloud import bigquery, aiplatform
from vertexai.language_models import TextEmbeddingModel

PROJECT_ID = "ai-boardroom-01"
REGION = "us-central1"
DATASET = "intell_claim_assessment"
TABLE = "Similarity_search_dataset"

OUTPUT_FILE = "claim_embeddings.jsonl"

def main():
    # Initialize clients
    bq = bigquery.Client(project=PROJECT_ID)
    aiplatform.init(project=PROJECT_ID, location=REGION)
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    # Query rows
    query = f"""
    SELECT claim_id, model, year, issue_description
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
    """
    rows = bq.query(query).result()

    with open(OUTPUT_FILE, "w") as f:
        for row in rows:
            text = f"Model: {row.model}, Year: {row.year}, Issue: {row.issue_description}"
            embedding = embedding_model.get_embeddings([text])[0].values

            datapoint = {
                "id": str(row.claim_id),
                "embedding": embedding,
                "attributes": {
                    "claim_id": row.claim_id,
                    "model": row.model,
                    "year": row.year,
                    "issue_description": row.issue_description,
                },
            }
            f.write(json.dumps(datapoint) + "\n")

    print(f"✅ Saved embeddings to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
