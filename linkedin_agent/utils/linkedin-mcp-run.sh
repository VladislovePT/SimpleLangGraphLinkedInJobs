# This is an example script to run the LinkedIn MCP server using Docker.
# Make sure to replace the placeholder values for LINKEDIN_COOKIE and USER_AGENT, this was tested on a local network.
docker run -it --rm \
  -e LINKEDIN_COOKIE="li_at=xxx" \
    -e USER_AGENT="xxx" \
  -p 8080:8080 \
  stickerdaniel/linkedin-mcp-server:latest \
  --transport streamable-http --host 0.0.0.0 --port 8080 --path /mcp