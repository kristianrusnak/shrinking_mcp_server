import sys
import logging
from mcp.server.fastmcp import FastMCP
import io
import os

sys.path.insert(0, "/app")  # /app is a package at the container root

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

from app.main import process_puml

mcp = FastMCP("shrinking-algorithm")

@mcp.tool()
def shrink_diagram_by_kruskal(puml_content: str) -> str:
    """Shrinks a PlantUML diagram using Kruskal's algorithm. Provide the absolute path to a .puml file."""
    try:
        f = io.StringIO(puml_content)
        logger.info(f"Receiving file and sending to shrinking algorithms...")
        result = process_puml(file=f, algorithm="kruskals", settings="{}")
        logger.info("Shrinking completed successfully")
        if result is None:
            logger.info("Shrinking completed but returned no output.")
            return "Shrinking completed but returned no output."
        logger.info(f"Result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return f"Error processing diagram: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
