"""
Base Agent Class
Provides common functionality for all agents
"""

import logging
import uuid
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all AI agents"""

    def __init__(self, name: str):
        """Initialize agent"""
        self.name = name
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now()

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """Execute agent logic - must be implemented by subclasses"""
        pass

    def log_execution(self, step_name: str, status: str, data: dict = None):
        """Log agent execution"""
        logger.info(f"[{self.name}] {step_name}: {status}")
        if data:
            logger.debug(f"[{self.name}] Data: {data}")

    def __repr__(self):
        return f"{self.name} (ID: {self.agent_id})"
