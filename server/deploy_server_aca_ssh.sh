#!/bin/bash
# deploy_server_aca_ssh.sh
# Deploy the Azure MCP server as an Azure Container App and open an SSH session

# Ask for region first
read -p "Enter Azure Region (e.g., eastus): " REGION
read -p "Enter Azure Resource Group: " RESOURCE_GROUP
read -p "Enter Container App Name: " APP_NAME
read -p "Enter Container App Environment Name: " ENV_NAME

# Generate a random API key
API_KEY=$(openssl rand -hex 32)
echo "Generated API Key: $API_KEY"

set -e

# Create resource group if it doesn't exist
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
  echo "Resource group $RESOURCE_GROUP does not exist. Creating..."
  az group create --name "$RESOURCE_GROUP" --location "$REGION"
else
  echo "Resource group $RESOURCE_GROUP already exists."
fi

# Deploy the container app
az containerapp up \
  -g "$RESOURCE_GROUP" \
  -n "$APP_NAME" \
  --environment "$ENV_NAME" \
  -l "$REGION" \
  --env-vars API_KEYS="$API_KEY" \
  --source .

# Enable external ingress
az containerapp ingress enable \
  -n "$APP_NAME" \
  -g "$RESOURCE_GROUP" \
  --type external \
  --target-port 8000 \
  --transport auto

# Get the FQDN (URL) of the deployed container app
MCP_URL=$(az containerapp show -n "$APP_NAME" -g "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" -o tsv)
MCP_URL_FULL="https://$MCP_URL/mcp/"

# Print the values for the user to add to their client .env
cat <<EOF

========================================
Add the following to your MCP client .env file:

MCP_API_KEYS="$API_KEY"
MCP_URL="$MCP_URL_FULL"
========================================
EOF