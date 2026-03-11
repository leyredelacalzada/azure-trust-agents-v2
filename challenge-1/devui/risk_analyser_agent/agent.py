import os
from azure.identity.aio import AzureCliCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuration
project_endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME")
agent_id = os.environ.get("RISK_ANALYSER_AGENT_ID")

# Use the pre-created agent ID from .env instead of creating a new one
agent = ChatAgent(
    name="RiskAnalyserAgent",
    description="Risk analysis agent for evaluating energy consumption patterns for potential fraud using energy regulatory compliance data",
    chat_client=AzureAIAgentClient(
        project_endpoint=project_endpoint,
        model_deployment_name=model_deployment_name,
        async_credential=AzureCliCredential(),
        agent_id=agent_id
    ),
    store=True
)


def main():
    """Launch the Risk Analyser Agent in DevUI."""
    import logging
    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Risk Analyser Agent")
    logger.info("Available at: http://localhost:8091")
    logger.info("Entity ID: agent_RiskAnalyserAgent")

    # Launch server with the agent
    serve(entities=[agent], port=8091, auto_open=True)


if __name__ == "__main__":
    main()
