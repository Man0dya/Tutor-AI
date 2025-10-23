"""
Agent Communication Protocol

This module implements the communication infrastructure for the multi-agent
AI tutoring system. It provides a protocol for agents to communicate with
each other, coordinate tasks, and collaborate on complex educational workflows.

Key Features:
- Agent registration and status tracking
- Message passing between agents
- Broadcast messaging to all agents
- Collaboration workflows for complex tasks
- HTTP server interface for external communication
- Communication logging and history tracking

Classes:
    AgentCommunicationProtocol: Core communication protocol implementation
    HTTPAgentServer: HTTP interface for agent communication (simplified demo version)

The system supports different message types including content generation,
question setting, answer evaluation, and health checks.
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class AgentCommunicationProtocol:
    
    """
    Communication protocol for multi-agent system.

    This class manages the registration, messaging, and coordination of multiple
    AI agents in the tutoring system. It provides both direct method calls and
    message-based communication patterns.

    Attributes:
        agents (dict): Registered agents with their capabilities and status
        message_history (list): History of all messages sent between agents
        communication_logs (list): Logs of communication events and system actions
    """

    def __init__(self):
        """Initialize the communication protocol with empty agent registry."""
        self.agents = {}
        self.message_history = []
        self.communication_logs = []

    def register_agent(self, agent_id: str, agent_instance, capabilities: List[str]):
        """
        Register an agent with the communication system.

        Args:
            agent_id (str): Unique identifier for the agent
            agent_instance: The actual agent object/instance
            capabilities (List[str]): List of capabilities this agent provides
        """
        self.agents[agent_id] = {
            'instance': agent_instance,
            'capabilities': capabilities,
            'status': 'active',
            'last_seen': datetime.now().isoformat()
        }

        self._log_communication(
            'system',
            'agent_registration',
            f"Agent {agent_id} registered with capabilities: {', '.join(capabilities)}"
        )

    def send_message(self, sender_id: str, receiver_id: str, message_type: str, content: Dict[str, Any]):
        """
        Send a message between agents.

        Args:
            sender_id (str): ID of the sending agent
            receiver_id (str): ID of the receiving agent
            message_type (str): Type of message (e.g., 'generate_content', 'evaluate_answers')
            content (Dict[str, Any]): Message payload/data

        Returns:
            Dict[str, Any]: Response from the receiving agent

        Raises:
            ValueError: If receiver agent is not registered
        """
        if receiver_id not in self.agents:
            raise ValueError(f"Agent {receiver_id} not found")

        message = {
            'id': f"msg_{int(time.time())}_{len(self.message_history)}",
            'sender': sender_id,
            'receiver': receiver_id,
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }

        try:
            # Process the message through the receiver agent
            response = self._process_message(message)
            message['status'] = 'delivered'
            message['response'] = response

            self.message_history.append(message)
            self._log_communication(sender_id, message_type, f"Message sent to {receiver_id}")

            return response

        except Exception as e:
            message['status'] = 'failed'
            message['error'] = str(e)
            self.message_history.append(message)
            self._log_communication(sender_id, 'error', f"Failed to send message to {receiver_id}: {str(e)}")
            raise

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message and route it to the appropriate agent method.

        Args:
            message (Dict[str, Any]): The message to process

        Returns:
            Dict[str, Any]: Processing result with status and data
        """
        receiver_id = message['receiver']
        message_type = message['type']
        content = message['content']

        receiver_agent = self.agents[receiver_id]['instance']

        # Route message based on type and agent capabilities
        if message_type == 'generate_content':
            if hasattr(receiver_agent, 'generate_content'):
                result = receiver_agent.generate_content(**content)
                return {'status': 'success', 'data': result}

        elif message_type == 'generate_questions':
            if hasattr(receiver_agent, 'generate_questions'):
                result = receiver_agent.generate_questions(**content)
                return {'status': 'success', 'data': result}

        elif message_type == 'evaluate_answers':
            if hasattr(receiver_agent, 'evaluate_answers'):
                result = receiver_agent.evaluate_answers(**content)
                return {'status': 'success', 'data': result}

        elif message_type == 'health_check':
            return {'status': 'success', 'agent_id': receiver_id, 'timestamp': datetime.now().isoformat()}

        else:
            return {'status': 'error', 'message': f"Unknown message type: {message_type}"}

        return {'status': 'error', 'message': 'Unknown processing error'}

    def broadcast_message(self, sender_id: str, message_type: str, content: Dict[str, Any]) -> Dict[str, List]:
        """
        Broadcast a message to all registered agents.

        Args:
            sender_id (str): ID of the broadcasting agent
            message_type (str): Type of message to broadcast
            content (Dict[str, Any]): Message payload

        Returns:
            Dict[str, List]: Responses from all agents keyed by agent ID
        """
        responses = {}

        for agent_id in self.agents:
            if agent_id != sender_id:  # Don't send to self
                try:
                    response = self.send_message(sender_id, agent_id, message_type, content)
                    responses[agent_id] = response
                except Exception as e:
                    responses[agent_id] = {'status': 'error', 'message': str(e)}

        return responses

    def request_collaboration(self, initiator_id: str, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request collaboration between multiple agents for a complex task.

        Args:
            initiator_id (str): ID of the agent initiating collaboration
            task_type (str): Type of collaborative task
            task_data (Dict[str, Any]): Task parameters and data

        Returns:
            Dict[str, Any]: Collaboration result

        Supported task types:
            - 'complete_tutoring_session': Full content + questions workflow
            - 'content_and_assessment': Content generation + assessment
        """
        if task_type == 'complete_tutoring_session':
            return self._handle_tutoring_collaboration(initiator_id, task_data)
        elif task_type == 'content_and_assessment':
            return self._handle_content_assessment_collaboration(initiator_id, task_data)
        else:
            raise ValueError(f"Unknown collaboration task type: {task_type}")

    def _handle_tutoring_collaboration(self, initiator_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a complete tutoring session collaboration workflow.

        This coordinates content generation followed by question generation
        to create a complete learning session.
        """
        result = {
            'session_id': f"session_{int(time.time())}",
            'status': 'in_progress',
            'steps': []
        }

        try:
            # Step 1: Generate content using content generator agent
            if 'content_generator' in self.agents:
                content_response = self.send_message(
                    initiator_id,
                    'content_generator',
                    'generate_content',
                    {
                        'topic': task_data.get('topic'),
                        'difficulty': task_data.get('difficulty', 'Intermediate'),
                        'subject': task_data.get('subject', 'General')
                    }
                )
                result['steps'].append({
                    'step': 'content_generation',
                    'status': 'completed',
                    'data': content_response
                })

                # Step 2: Generate questions based on generated content
                if 'question_setter' in self.agents and content_response.get('status') == 'success':
                    questions_response = self.send_message(
                        initiator_id,
                        'question_setter',
                        'generate_questions',
                        {
                            'content': content_response['data'],
                            'question_count': task_data.get('question_count', 5),
                            'question_types': task_data.get('question_types', ['Multiple Choice', 'Short Answer'])
                        }
                    )
                    result['steps'].append({
                        'step': 'question_generation',
                        'status': 'completed',
                        'data': questions_response
                    })

            result['status'] = 'completed'
            return result

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            return result

    def _handle_content_assessment_collaboration(self, initiator_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content generation and assessment collaboration.

        Coordinates content creation followed by question generation for assessment.
        """
        result = {
            'collaboration_id': f"collab_{int(time.time())}",
            'status': 'in_progress',
            'phases': []
        }

        try:
            # Phase 1: Content Creation
            content_result = self.send_message(
                initiator_id,
                'content_generator',
                'generate_content',
                task_data.get('content_params', {})
            )

            result['phases'].append({
                'phase': 'content_creation',
                'result': content_result
            })

            # Phase 2: Question Generation for assessment
            if content_result.get('status') == 'success':
                question_result = self.send_message(
                    initiator_id,
                    'question_setter',
                    'generate_questions',
                    {
                        'content': content_result['data'],
                        **task_data.get('question_params', {})
                    }
                )

                result['phases'].append({
                    'phase': 'question_generation',
                    'result': question_result
                })

            result['status'] = 'completed'
            return result

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            return result

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific agent.

        Args:
            agent_id (str): ID of the agent to check

        Returns:
            Dict[str, Any]: Agent status information including responsiveness
        """
        if agent_id not in self.agents:
            return {'status': 'not_found'}

        agent_info = self.agents[agent_id].copy()

        # Check if agent is responsive by sending health check
        try:
            health_response = self.send_message('system', agent_id, 'health_check', {})
            agent_info['responsive'] = health_response.get('status') == 'success'
        except:
            agent_info['responsive'] = False

        return agent_info

    def get_communication_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent communication logs.

        Args:
            limit (int): Maximum number of log entries to return

        Returns:
            List[Dict[str, Any]]: Recent communication log entries
        """
        return self.communication_logs[-limit:]

    def get_message_history(self, agent_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get message history, optionally filtered by agent.

        Args:
            agent_id (Optional[str]): Filter messages for specific agent, or None for all
            limit (int): Maximum number of messages to return

        Returns:
            List[Dict[str, Any]]: Message history
        """
        history = self.message_history

        if agent_id:
            history = [msg for msg in history if msg['sender'] == agent_id or msg['receiver'] == agent_id]

        return history[-limit:]

    def _log_communication(self, agent_id: str, action: str, details: str):
        """
        Log communication events for monitoring and debugging.

        Args:
            agent_id (str): ID of the agent involved
            action (str): Type of action performed
            details (str): Detailed description of the event
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'action': action,
            'details': details
        }

        self.communication_logs.append(log_entry)

        # Keep only recent logs to prevent memory issues
        if len(self.communication_logs) > 1000:
            self.communication_logs = self.communication_logs[-500:]

    def clear_history(self, older_than_hours: int = 24):
        """
        Clear old message history and logs to manage memory usage.

        Args:
            older_than_hours (int): Remove entries older than this many hours
        """
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)

        self.message_history = [
            msg for msg in self.message_history
            if datetime.fromisoformat(msg['timestamp']).timestamp() > cutoff_time
        ]

        self.communication_logs = [
            log for log in self.communication_logs
            if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_time
        ]

class HTTPAgentServer:

    """
    HTTP server for agent communication (simplified mock for demonstration).

    This class provides an HTTP interface for external systems to communicate
    with the agent network. In production, this would be a full HTTP server
    implementation using frameworks like FastAPI or Flask.

    Note: This is a simplified demonstration version for the tutoring system.

    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):

        """
        Initialize the HTTP server.

        Args:
            host (str): Host address to bind to
            port (int): Port number to listen on

        """
        self.host = host
        self.port = port
        self.communication_protocol = AgentCommunicationProtocol()
        self.routes = {
            '/send_message': self._handle_send_message,
            '/broadcast': self._handle_broadcast,
            '/agent_status': self._handle_agent_status,
            '/health': self._handle_health_check
        }

    def _handle_send_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:

        """Handle send message HTTP requests."""

        try:
            response = self.communication_protocol.send_message(
                request_data['sender'],
                request_data['receiver'],
                request_data['message_type'],
                request_data['content']
            )
            return {'status': 'success', 'response': response}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _handle_broadcast(self, request_data: Dict[str, Any]) -> Dict[str, Any]:

        """Handle broadcast message HTTP requests."""
        
        try:
            responses = self.communication_protocol.broadcast_message(
                request_data['sender'],
                request_data['message_type'],
                request_data['content']
            )
            return {'status': 'success', 'responses': responses}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _handle_agent_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent status HTTP requests."""
        agent_id = request_data.get('agent_id')
        if agent_id:
            status = self.communication_protocol.get_agent_status(agent_id)
            return {'status': 'success', 'agent_status': status}
        else:
            # Return all agents status
            all_status = {
                agent_id: self.communication_protocol.get_agent_status(agent_id)
                for agent_id in self.communication_protocol.agents
            }
            return {'status': 'success', 'all_agents': all_status}

    def _handle_health_check(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check HTTP requests."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self.communication_protocol.agents),
            'message_count': len(self.communication_protocol.message_history)
        }

    def process_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process HTTP-like requests (simplified for demonstration).

        Args:
            endpoint (str): API endpoint path
            request_data (Dict[str, Any]): Request payload

        Returns:
            Dict[str, Any]: Response data
        """
        if endpoint in self.routes:
            return self.routes[endpoint](request_data)
        else:
            return {'status': 'error', 'message': f'Unknown endpoint: {endpoint}'} 