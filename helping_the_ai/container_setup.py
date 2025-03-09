from azure.identity import DefaultAzureCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient

COSMOSDB_NAME = "memeql-nosql"
CONTAINER_NAME = "memes2"
DATABASE_NAME = "memeql"
SUBSCRIPTION_ID = "6cb3cd2c-4f4a-48ba-a7d2-eba4abf948ab"
RG_NAME = "memeql"
LOCATION = "eastus2"


vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/imageVector",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 1536
        }
    ]
}

indexing_policy = {
    "includedPaths": [
        {
            "path": "/*"
        }
    ],
    "excludedPaths": [
        {
            "path": "/\"_etag\"/?",
            "path": "/imageVector/*"

        }
    ],
    "vectorIndexes": [
        {"path": "/imageVector",
         "type": "quantizedFlat"
         }
    ],
    "fullTextIndexes": {
        "indexingMode": "consistent",
        "automatic": True,
        "includedPaths": [
            {
                "path": "/is_meme/is_meme_response/*"
            }
        ],
        "excludedPaths": [
            {
                "path": "/\"_etag\"/?"
            },
        ],
    }
}

full_text_policy = {
    "defaultLanguage": "en-US",
    "fullTextPaths": [
        {
            "path": "/is_meme/is_meme_response/*",
            "language": "en-US"
        }
    ]
}

container_parameters = {
    "location": LOCATION,
    "resource": {
        "id": CONTAINER_NAME,
        "indexing_policy": indexing_policy,
        "partition_key": {
            "paths": [
                "/id"
            ]
        },
        "vector_embedding_policy": vector_embedding_policy,
        "full_text_policy": full_text_policy
    }
}

credential = DefaultAzureCredential()

management_client = CosmosDBManagementClient(
    credential=credential, subscription_id=SUBSCRIPTION_ID)

container = management_client.sql_resources.begin_create_update_sql_container(
    resource_group_name=RG_NAME, account_name=COSMOSDB_NAME, database_name=DATABASE_NAME,
    container_name=CONTAINER_NAME, create_update_sql_container_parameters=container_parameters).result()
print("Create sql container:\n{}".format(container))
