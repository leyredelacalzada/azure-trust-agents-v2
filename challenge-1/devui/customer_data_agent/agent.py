import asyncio
import os
from typing import Annotated
from azure.identity.aio import AzureCliCredential
from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureAIAgentClient
from agent_framework import ChatAgent
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
from pydantic import Field

load_dotenv(override=True)

# Configuration
project_endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME")
cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT")
customer_data_agent_id = os.environ.get("CUSTOMER_DATA_AGENT_ID")

# Initialize Cosmos DB clients globally for function tools
cosmos_credential = DefaultAzureCredential()
cosmos_client = CosmosClient(cosmos_endpoint, cosmos_credential)
database = cosmos_client.get_database_client("EnergyComplianceDB")
customers_container = database.get_container_client("Customers")
transactions_container = database.get_container_client("Transactions")

def get_customer_data(customer_id: str) -> dict:
    """Get customer data from Cosmos DB"""
    try:
        query = f"SELECT * FROM c WHERE c.customer_id = '{customer_id}'"
        items = list(customers_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items[0] if items else {"error": f"Customer {customer_id} not found"}
    except Exception as e:
        return {"error": str(e)}

def get_customer_transactions(customer_id: str) -> list:
    """Get all transactions for a customer from Cosmos DB"""
    try:
        query = f"SELECT * FROM c WHERE c.customer_id = '{customer_id}'"
        items = list(transactions_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items
    except Exception as e:
        return [{"error": str(e)}]

def get_transaction_data(transaction_id: str) -> dict:
    """Get transaction data from Cosmos DB"""
    try:
        query = f"SELECT * FROM c WHERE c.transaction_id = '{transaction_id}'"
        items = list(transactions_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items[0] if items else {"error": f"Transaction {transaction_id} not found"}
    except Exception as e:
        return {"error": str(e)}

# Create the agent instance following Agent Framework DevUI conventions
agent = ChatAgent(
    name="CustomerDataAgent",
    description="Data ingestion agent for retrieving and enriching customer and energy consumption reading data from Cosmos DB",
    instructions="""You are a Data Ingestion Agent responsible for preparing structured input for energy fraud detection. 
    You will receive energy consumption readings and customer profiles. Your task is to:
    - Normalize fields (e.g., consumption units, timestamps, meter readings)
    - Remove or flag incomplete data
    - Enrich each reading with relevant customer metadata (e.g., account age, region, meter info, property type, baseline consumption)
    - Output a clean JSON object per reading with unified structure

    You have access to the following functions:
    - get_customer_data: Fetch customer details by customer_id
    - get_customer_transactions: Get all consumption readings for a customer
    - get_transaction_data: Get specific consumption reading by reading_id

    Use these functions to enrich and validate the consumption data.
    Ensure the format is consistent and ready for analysis.
    """,
    chat_client=AzureAIAgentClient(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        async_credential=AzureCliCredential(),
        agent_id=customer_data_agent_id
    ),
    tools=[
        get_customer_data,
        get_customer_transactions,
        get_transaction_data,
    ],
)


def main():
    """Launch the Customer Data Agent in DevUI."""
    import logging
    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Customer Data Agent")
    logger.info("Available at: http://localhost:8090")
    logger.info("Entity ID: agent_CustomerDataAgent")

    # Launch server with the agent
    serve(entities=[agent], port=8090, auto_open=True)


if __name__ == "__main__":
    main()