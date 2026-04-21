"""
Base Agent class and Event Dispatcher

All agents inherit from BaseAgent and register their event handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f'agents.{name}')
    
    @abstractmethod
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an event. Should be overridden by subclasses.
        
        Args:
            event: GitHub webhook event
            
        Returns:
            Result of handling the event
        """
        pass
    
    def log_action(self, action_type: str, resource_type: str, 
                  resource_id: str, details: Dict[str, Any]) -> None:
        """Log agent action to database"""
        try:
            from backend.models import AuditLog
            from backend.app import db
            
            # This will be called in the context of the Flask app
            audit = AuditLog(
                action_type=action_type,
                actor=self.name,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                organization_id=None  # Will be set based on context
            )
            # Note: actual database write happens in dispatcher context
        except Exception as e:
            self.logger.error(f'Failed to log action: {e}')

class EventDispatcher:
    """Central event dispatcher for agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger('agents.dispatcher')
    
    def register_agent(self, agent: BaseAgent, events: List[str]) -> None:
        """
        Register an agent to handle specific events
        
        Args:
            agent: Agent instance
            events: List of event types to handle (e.g., 'pull_request', 'push')
        """
        self.agents[agent.name] = agent
        for event_type in events:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(agent.handle_event)
        self.logger.info(f'Registered {agent.name} for events: {events}')
    
    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch an event to registered handlers
        
        Args:
            event_type: Type of event (e.g., 'pull_request')
            payload: Event payload from GitHub
            
        Returns:
            Dictionary with results from all handlers
        """
        self.logger.info(f'Dispatching {event_type} event')
        
        results = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'handlers': {}
        }
        
        if event_type not in self.handlers:
            self.logger.warning(f'No handlers registered for {event_type}')
            return results
        
        for handler in self.handlers[event_type]:
            try:
                agent_name = handler.__self__.name  # Get agent name from bound method
                result = handler(payload)
                results['handlers'][agent_name] = result
                self.logger.info(f'{agent_name} handled {event_type} successfully')
            except Exception as e:
                self.logger.error(f'Agent handler failed: {e}', exc_info=True)
                results['handlers'][agent_name] = {'error': str(e)}
        
        return results

# Global dispatcher instance
dispatcher = EventDispatcher()
