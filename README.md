# Azure Subscription Cleaner
Azure Subscription Cleaner is an Azure Function that tags and deletes Resource Groups marked for deletion.

## Azure Function
The Function is a Python 3.9 app that uses the Azure SDK and a Managed Identity to iterate over Resource Groups in a given Subscription and delete those that have been marked for deletion. The `EXPIRY_DAYS` environment variable dictates the number of days before a Resource Group is deleted. (now + EXPIRY_DAYS)

The tag `ExpirationDate` will be assigned to the Resource Group with the appropriate date. If a Resource Group needs to be indefinitely excluded from deletion, the tag `ExpirationDate` with the value `Exempt` can be assigned to the Resource Group. Also [consider adding a Resource Lock](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/lock-resources?tabs=json) to the Resource Group for safety.

The following environment variables (or "Configuration" in the Azure Portal) can be set to configure the Function:

| Variable                     | Description                                                    | Default       |
| :--------------------------- | :------------------------------------------------------------- | :------------ |
| `EXPIRY_DAYS`                | The number of days before deleting the Resource Group          | `14`          |
| `MANAGED_IDENTITY_CLIENT_ID` | The Client ID of the associated Managed Identity               |               |
| `AZURE_SUBSCRIPTION_ID`      | The ID of the Azure Subscription that will be iterated over    |               |

The [function.json](function.json) file contains the configuration for the Function. The `schedule` property can be changed to configure how often the Function is run. The default is every 5 minutes.

## Pipeline
An Azure DevOps pipeline is included in [azure-pipelines.yml](azure-pipelines.yml) that will build and deploy the Azure Function to Azure, using a Free Consumption Plan. This makes [the first 1 million executions](https://azure.microsoft.com/en-us/pricing/details/functions/)* free. The pipeline requires the following parameters to be set:

| Parameters                | Description                                                                                                 | Default       |
| :------------------------ | :---------------------------------------------------------------------------------------------------------- | :------------ |
| `azureSubscription`       | The name of the Azure Service Connection                                                                    |               |
| `resourceGroupName`       | The name of the Resource Group to deploy the Azure Function to                                              |               |
| `functionAppName`         | The name of the Azure Function App                                                                          |               |
| `storageAccountName`      | The name of the Storage Account to use for the Azure Function                                               |               |
| `serviceConnection`       | The name of the Azure Service Connection                                                                    |               |
| `subscriptionId`          | The Azure Subscription ID                                                                                   |               |
| `location`                | The Azure Region to deploy the Azure Function to                                                            | `westeurope`  |
| `managedIdentityRoleName` | The name of the Role to assign to the Managed Identity                                                      | `Contributor` |
| `expiryDays`              | The number of days before cleaning the Subscription                                                         | `14`          |
| `createInfrastructure`    | Deploys required infrastructure first, set this to false if you want to deploy to your own App Service Plan | `true`        |


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.