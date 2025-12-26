"""
Main entry point for RIN
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rin import Agent
from rin.utils import setup_logging


def main():
    """Main entry point"""
    setup_logging("INFO")
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Rhyzomic Intelligence Node (RIN)")
    logger.info("Version: 1.2.0 (Stable)")
    logger.info("Status: Active Development")
    logger.info("Classification: Sovereign AI Infrastructure")
    logger.info("=" * 60)

    # Initialize the agent
    agent = Agent()

    # Display status
    status = agent.get_status()
    logger.info("\nAgent Status:")
    for key, value in status.items():
        logger.info(f"  {key}: {value}")

    # Example usage
    logger.info("\n" + "=" * 60)
    logger.info("Example Query")
    logger.info("=" * 60)
    response = agent.query("What is the status of the Rhyzomic Intelligence Node?")
    logger.info(f"Response: {response}")

    # Example task execution
    logger.info("\n" + "=" * 60)
    logger.info("Example Task Execution")
    logger.info("=" * 60)
    task_result = agent.execute_task("Monitor and analyze AI developments")
    logger.info(f"Task Status: {task_result}")

    logger.info("\n" + "=" * 60)
    logger.info("RIN is ready for sovereign operations")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
