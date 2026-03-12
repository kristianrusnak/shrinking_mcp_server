FROM python:3.11-slim

WORKDIR /

# Copy and install the shrinking_algorithm app
COPY shrinking_algorithms /app
# Install numpy first, then the local embedding package
RUN pip install --no-cache-dir numpy
RUN pip install --no-cache-dir -e /app/embedding

# Copy and install the MCP server
COPY mcp_server /mcp_server
RUN pip install --no-cache-dir -r /mcp_server/requirements.txt

WORKDIR /mcp_server

CMD ["python", "server.py"]