AI Code Reviewer - Deployment Guide
This guide provides instructions for deploying the AI Code Reviewer application to Google Cloud Run.

Prerequisites
Google Cloud SDK: Make sure you have the gcloud command-line tool installed and configured on your local machine. You can find installation instructions here.GCP Project: You need a Google Cloud Project with billing enabled.Enabled APIs: Ensure the following APIs are enabled in your GCP project. You can enable them by searching for them in the GCP Console's "APIs & Services" dashboard.Cloud Build APICloud Run APIVertex AI APIIdentity and Access Management (IAM) APIDeployment 

Steps1. Create a Service AccountYour Cloud Run service needs an identity to interact with the Vertex AI API securely. It's a best practice to create a dedicated service account for this purpose.

a. Create the service account: Open your terminal or Cloud Shell and run the following command, replacing YOUR_PROJECT_ID with your actual GCP Project ID.gcloud iam service-accounts create code-reviewer-sa \
    --display-name="Service Account for Code Reviewer App" \
    --project=YOUR_PROJECT_ID
b. Grant the "Vertex AI User" role to the service account. This allows it to make calls to the Gemini model.gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:code-reviewer-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
Remember to replace YOUR_PROJECT_ID in both places.

2. Build and Deploy to Cloud RunNavigate to the root directory of your project (where your app.py, Dockerfile, etc., are located) in your terminal. Then, run the following command. This single command will use Cloud Build to build your container image from the Dockerfile and then deploy that image to Cloud Run.gcloud run deploy ai-code-reviewer \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --service-account=code-reviewer-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars="GCP_PROJECT_ID=YOUR_PROJECT_ID" \
    --set-env-vars="FLASK_SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')"
Command Breakdown:gcloud run deploy ai-code-reviewer: Deploys a new service or a new revision of a service named ai-code-reviewer.--source .: Tells Cloud Build to use the source code from the current directory.--platform managed: Specifies the fully managed, serverless Cloud Run environment.--region us-central1: Sets the deployment region. You can choose a different region if you prefer.--allow-unauthenticated: This makes your web app's URL public. Access to the core functionality is still protected by your Flask application's login system.--service-account: Attaches the dedicated service account you created in the previous step, giving the service the necessary permissions.--set-env-vars: Sets environment variables that your application can access.GCP_PROJECT_ID: Your script needs this to initialize the Vertex AI client.FLASK_SECRET_KEY: Sets a secure, random secret key for Flask sessions, which is crucial for security.3. Access Your ApplicationOnce the deployment is complete, the gcloud command will output a Service URL. You can visit this URL in your web browser to access your deployed AI Code Reviewer application.