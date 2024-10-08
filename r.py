from fastapi import FastAPI
import os
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.mgmt.applicationinsights.models import ApplicationInsightsComponent

app = FastAPI()

# Environment variables for subscription and other resource info
SUBSCRIPTION_ID = "da9091ec-d18f-456c-9c21-5783ee7f4645"
RESOURCE_GROUP_NAME = "SatelliteScalingTestUtka"
APP_INSIGHTS_NAME = "utka-test1"
LOCATION = "EastUS"

@app.get("/create-app-insights")
async def create_app_insights():
    # Use DefaultAzureCredential for Managed Identity authentication in Azure
    credential = DefaultAzureCredential()

    # Create Resource Management Client
    resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)

    # Create Application Insights Management Client
    app_insights_client = ApplicationInsightsManagementClient(credential, SUBSCRIPTION_ID)

    try:
        # Check if the resource group exists (create it if needed)
        if not resource_client.resource_groups.check_existence(RESOURCE_GROUP_NAME):
            resource_client.resource_groups.create_or_update(
                RESOURCE_GROUP_NAME,
                {"location": LOCATION}
            )

        # Create or update the Application Insights resource
        insight_properties = ApplicationInsightsComponent(
            location=LOCATION,
            application_type="web",
            kind="web",
            workspace_resource_id="/subscriptions/da9091ec-d18f-456c-9c21-5783ee7f4645/resourceGroups/SatelliteScalingTestUtka/providers/Microsoft.OperationalInsights/workspaces/test-utka-law"
        )

        result = app_insights_client.components.create_or_update(
            resource_group_name=RESOURCE_GROUP_NAME,
            resource_name=APP_INSIGHTS_NAME,
            insight_properties=insight_properties
        )

        return {"message": f"Application Insights resource created with ID: {result.id}"}
    
    except Exception as e:
        logging.error(f"Error creating Application Insights resource: {e}")
        return {"error": str(e)}