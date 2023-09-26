import os
import datetime
import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:

    # Read environment variables
    managed_identity_client_id = os.environ.get('MANAGED_IDENTITY_CLIENT_ID')
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    expiry_days = int(os.environ.get('EXPIRY_DAYS', 14))

    if not subscription_id:
        logging.error("AZURE_SUBSCRIPTION_ID environment variable not set.")
        return
    
    if not managed_identity_client_id:
        logging.error("MANAGED_IDENTITY_CLIENT_ID environment variable not set.")
        return

    # Initialize Azure SDK
    credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id, exclude_interactive_browser_credential=False, additionally_allowed_tenants="*")
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get current date
    now = datetime.datetime.now()

    # List all resource groups
    for item in resource_client.resource_groups.list():
        resource_group_name = item.name
        resource_tags = item.tags if item.tags else {}

        # Check if ExpirationDate is "Exempt"
        if resource_tags.get('ExpirationDate') == 'Exempt':
            continue

        # Check if ExpirationDate exists and is in the past
        if 'ExpirationDate' in resource_tags:
            expiration_date = datetime.datetime.strptime(resource_tags['ExpirationDate'], '%Y-%m-%d')
            if expiration_date < now:
                # Delete the resource group
                logging.info(f"Deleting resource group: {resource_group_name}")
                resource_client.resource_groups.begin_delete(resource_group_name).result()
            continue  # Skip to the next resource group, don't update the ExpirationDate tag

        # Set ExpirationDate to expiry_days days from now
        expiration_date = (now + datetime.timedelta(days=expiry_days)).strftime('%Y-%m-%d')
        resource_tags['ExpirationDate'] = expiration_date

        # Update the resource group tags
        resource_group_params = ResourceGroup(location=item.location, tags=resource_tags)
        resource_client.resource_groups.create_or_update(resource_group_name, resource_group_params)
        
        logging.info(f"Updated ExpirationDate for resource group: {resource_group_name}")