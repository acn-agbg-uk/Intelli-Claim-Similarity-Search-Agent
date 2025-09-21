import os
import json
from flask import Flask, request, jsonify
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

app = Flask(__name__)

PROJECT_ID = "ai-boardroom-01"
REGION = "us-central1"
INDEX_ENDPOINT_ID = "219851748020322304"
DEPLOYED_INDEX_ID = "claims_index"

embedding_model = None
index_endpoint = None


@app.before_first_request
def init_clients():
    """Initialize Vertex AI clients once before the first request."""
    global embedding_model, index_endpoint
    if embedding_model is None or index_endpoint is None:
        aiplatform.init(project=PROJECT_ID, location=REGION)
        embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=f"projects/{PROJECT_ID}/locations/{REGION}/indexEndpoints/{INDEX_ENDPOINT_ID}"
        )


@app.route("/")
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/find_similar_claims", methods=["POST"])
def find_similar_claims():
    data = request.json
    model = data.get("model")
    year = data.get("year")
    description = data.get("description")

    if not (model and year and description):
        return jsonify({"error": "Missing one of required fields: model, year, description"}), 400

    try:
        # Combine fields into one text input for embeddings
        query_text = f"Model: {model}, Year: {year}, Issue: {description}"

        embedding = embedding_model.get_embeddings([query_text])[0].values

        response = index_endpoint.find_neighbors(
            deployed_index_id=DEPLOYED_INDEX_ID,
            queries=[embedding],
            num_neighbors=10,
            return_full_datapoint=True,
        )

        similar_claims = []
        context_parts = []

        if response and response[0]:
            for neighbor in response[0]:
                distance = neighbor.distance
                confidence = 1 - (distance / 2) if distance is not None else 0

                if confidence >= 0.85:
                    attributes = {}
                    if hasattr(neighbor, "datapoint") and neighbor.datapoint is not None:
                        attributes = neighbor.datapoint.to_dict().get("attributes", {})

                    claim_info = {
                        "claim_number": attributes.get("claim_id", getattr(neighbor, "id", None)),
                        "model": attributes.get("model"),
                        "year": attributes.get("year"),
                        "description": attributes.get("issue_description"),
                        "confidence_score": confidence,
                    }

                    similar_claims.append(claim_info)

                    # Add to context (compact)
                    context_parts.append(
                        f"[{claim_info['model']} {claim_info['year']}] "
                        f"{claim_info['description']} "
                        f"(conf: {claim_info['confidence_score']:.2f})"
                    )

        # Limit to top 3
        similar_claims = similar_claims[:3]
        context = " | ".join(context_parts[:3])

        return jsonify(
            {
                "similar_claims": similar_claims,
                "count": len(similar_claims),
                "context": context,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))