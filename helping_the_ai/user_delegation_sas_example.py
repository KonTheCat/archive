from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential
from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas
)
import datetime
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient

#functions start
def get_credential():
    default_credential = DefaultAzureCredential()
    return default_credential

def get_credentialChain(): 
    return ChainedTokenCredential(AzureCliCredential, ManagedIdentityCredential)

def get_primary_storage_account_key(storageAccountName, subscriptionID, credential):
    resource_client = ResourceManagementClient(credential, subscriptionID)
    resourceList = resource_client.resources.list()
    for item in resourceList:
        if(item.type == 'Microsoft.Storage/storageAccounts' and item.name == storageAccountName):
            resource_group_name = (item.id).split('/')[4]
    storageClient = StorageManagementClient(credential, subscriptionID)
    keys = storageClient.storage_accounts.list_keys(resource_group_name, storageAccountName)
    primaryKey = keys.keys[0].value
    return primaryKey

def set_blob_data(data, storageAccountName, credential, containerName, blobName):
    blob_service_client = BlobServiceClient(account_url = f"https://{storageAccountName}.blob.core.windows.net", credential = credential)
    blob_client = blob_service_client.get_blob_client(container = containerName, blob = blobName)
    blob_client.upload_blob(data, blob_type = "BlockBlob", overwrite = True)

def get_blob_data(storageAccountName, credential, containerName, blobName):
    blob_service_client = BlobServiceClient(account_url = f"https://{storageAccountName}.blob.core.windows.net", credential = credential)
    try:
        blob_client = blob_service_client.get_blob_client(container = containerName, blob = blobName)
        downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
    except:
        return None
    data = downloader.readall()
    return data

def download_blob(storageAccountName, credential, containerName, blobName, destinationPath):
    blob_service_client = BlobServiceClient(account_url = f"https://{storageAccountName}.blob.core.windows.net", credential = credential)
    blob_client = blob_service_client.get_blob_client(container = containerName, blob = blobName)
    with open(destinationPath, mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())

def create_user_delegation_sas_blob(blob_client, user_delegation_key):
    # Create a SAS token that's valid for one day, as an example
    start_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= -5)
    expiry_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= 5)

    sas_token = generate_blob_sas(
        account_name=blob_client.account_name,
        container_name=blob_client.container_name,
        blob_name=blob_client.blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time,
        start=start_time
    )

    return sas_token

def get_blob_userDelegationSASUrl(storageAccountName, credential, containerName, blobName):
    blob_service_client = BlobServiceClient(account_url = f"https://{storageAccountName}.blob.core.windows.net", credential = credential)
    delegation_key_start_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= -5)
    delegation_key_expiry_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= 5)

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=delegation_key_start_time,
        key_expiry_time=delegation_key_expiry_time
    )
    blob_client = blob_service_client.get_blob_client(container = containerName, blob = blobName)
    sas_token = create_user_delegation_sas_blob(blob_client, user_delegation_key)
    sas_url = f"{blob_client.url}?{sas_token}"
    return sas_url

def get_blob_sasURL(storageAccountName, storageAccountKey, containerName, blobName):
    sas = generate_blob_sas(account_name=storageAccountName,
                            account_key=storageAccountKey,
                            container_name=containerName,
                            blob_name=blobName,
                            permission=BlobSasPermissions(read=True),
                            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2))
    sas_url = f"https://{storageAccountName}.blob.core.windows.net/{containerName}/{blobName}?{sas}" 
    return sas_url