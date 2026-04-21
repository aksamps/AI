"""
Agent Dispatcher and Webhook Handler

This module sets up the GitHub webhook listener and routes events to agents.
"""

import os
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
from functools import wraps

# Import agents
from coding_agent import coding_agent
from pr_review_agent import pr_review_agent
from workflow_agent import workflow_agent
from base_agent import dispatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('agents.dispatcher')

# Initialize Flask app for webhook
app = Flask(__name__)

# Register agents with dispatcher
dispatcher.register_agent(coding_agent, ['push', 'pull_request'])
dispatcher.register_agent(pr_review_agent, ['pull_request'])
dispatcher.register_agent(workflow_agent, ['workflow_run', 'pull_request_review'])

def verify_github_signature(f):
    """Decorator to verify GitHub webhook signature"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        if not signature:
            logger.warning('No signature provided')
            return jsonify({'error': 'No signature'}), 401
        
        # Get webhook secret
        secret = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-secret')
        
        # Verify signature
        payload = request.get_data()
        expected_signature = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning('Invalid signature')
            return jsonify({'error': 'Invalid signature'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/webhooks/github', methods=['POST'])
@verify_github_signature
def handle_github_webhook():
    """Handle GitHub webhook events"""
    
    event_type = request.headers.get('X-GitHub-Event', '')
    payload = request.get_json()
    
    if not event_type or not payload:
        return jsonify({'error': 'Missing event type or payload'}), 400
    
    logger.info(f'Received GitHub event: {event_type}')
    
    # Check if event is action-based (pull_request, workflow_run, etc.)
    action = payload.get('action')
    
    # Enhance payload with event type
    payload['event_type'] = event_type
    
    # Dispatch to agents
    try:
        result = dispatcher.dispatch(event_type, payload)
        logger.info(f'Event {event_type} processed successfully')
        return jsonify(result), 200
    except Exception as e:
        logger.error(f'Error processing event: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'agents-dispatcher',
        'agents': list(dispatcher.agents.keys())
    }), 200

if __name__ == '__main__':
    logger.info('Starting Agents Dispatcher Service')
    app.run(host='0.0.0.0', port=5001, debug=False)
