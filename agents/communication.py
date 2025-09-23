import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

class AgentCommunicationProtocol:
    """
    Communication protocol for multi-agent system
    Handles HTTP-based API communication between agents
    """
    
    def __init__(self):
        self.agents = {}
        self.message_history = []
        self.communication_logs = []
    
    def register_agent(self, agent_id: str, agent_instance, capabilities: List[str]):
        """Register an agent with the communication system"""
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
        """Send a message between agents"""
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
            # Process the message
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
        """Process a message and route it to the appropriate agent"""
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
        """Broadcast a message to all registered agents"""
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
        """Request collaboration between multiple agents for a complex task"""
        
        if task_type == 'complete_tutoring_session':
            return self._handle_tutoring_collaboration(initiator_id, task_data)
        elif task_type == 'content_and_assessment':
            return self._handle_content_assessment_collaboration(initiator_id, task_data)
        else:
            raise ValueError(f"Unknown collaboration task type: {task_type}")
    
    def _handle_tutoring_collaboration(self, initiator_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a complete tutoring session collaboration"""
        result = {
            'session_id': f"session_{int(time.time())}",
            'status': 'in_progress',
            'steps': []
        }
        
        try:
            # Step 1: Generate content
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
                
                # Step 2: Generate questions based on content
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
        """Handle content generation and assessment collaboration"""
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
            
            # Phase 2: Question Generation
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
        """Get the status of a specific agent"""
        if agent_id not in self.agents:
            return {'status': 'not_found'}
        
        agent_info = self.agents[agent_id].copy()
        
        # Check if agent is responsive
        try:
            health_response = self.send_message('system', agent_id, 'health_check', {})
            agent_info['responsive'] = health_response.get('status') == 'success'
        except:
            agent_info['responsive'] = False
        
        return agent_info
    
    def get_communication_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent communication logs"""
        return self.communication_logs[-limit:]
    
    def get_message_history(self, agent_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get message history, optionally filtered by agent"""
        history = self.message_history
        
        if agent_id:
            history = [msg for msg in history if msg['sender'] == agent_id or msg['receiver'] == agent_id]
        
        return history[-limit:]
    
    def _log_communication(self, agent_id: str, action: str, details: str):
        """Log communication events"""
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
        """Clear old message history and logs"""
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
    HTTP server for agent communication (simplified mock for demonstration)
    In production, this would be a full HTTP server implementation
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
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
        """Handle send message requests"""
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
        """Handle broadcast requests"""
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
        """Handle agent status requests"""
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
        """Handle health check requests"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self.communication_protocol.agents),
            'message_count': len(self.communication_protocol.message_history)
        }
    
    def process_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process HTTP-like requests (simplified for demonstration)"""
        if endpoint in self.routes:
            return self.routes[endpoint](request_data)
        else:
            return {'status': 'error', 'message': f'Unknown endpoint: {endpoint}'}
