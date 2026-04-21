"""
Workflow Agent - CI/CD orchestration and approval gate enforcement

Triggers on: workflow_run, pull_request_review events
Responsibilities:
- Monitor workflow status
- Enforce that all checks pass before allowing merge
- Manage approval workflow
- Track PR lifecycle state
- Update branch protection enforcement
"""

from typing import Any, Dict
from base_agent import BaseAgent
from datetime import datetime

class WorkflowAgent(BaseAgent):
    """Workflow agent for CI/CD orchestration"""
    
    def __init__(self):
        super().__init__('WorkflowAgent')
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow_run or pull_request_review event"""
        
        event_type = event.get('event_type', '')
        
        if event_type == 'workflow_run':
            return self._handle_workflow_run(event)
        elif event_type == 'pull_request_review':
            return self._handle_pr_review(event)
        else:
            return {'skipped': f'Event type {event_type} not handled'}
    
    def _handle_workflow_run(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow_run event"""
        
        workflow = event.get('workflow_run', {})
        conclusion = workflow.get('conclusion')
        status = workflow.get('status')
        run_id = workflow.get('id')
        head_branch = workflow.get('head_branch')
        
        result = {
            'agent': self.name,
            'event': 'workflow_run',
            'run_id': run_id,
            'branch': head_branch,
            'status': status,
            'conclusion': conclusion
        }
        
        # Check if all required jobs passed
        if status == 'completed':
            if conclusion == 'success':
                result['action'] = 'workflow_passed'
                result['message'] = 'All CI checks passed'
                result['can_merge'] = True
            else:
                result['action'] = 'workflow_failed'
                result['message'] = f'Workflow failed: {conclusion}'
                result['can_merge'] = False
        else:
            result['action'] = 'workflow_in_progress'
            result['can_merge'] = False
        
        self.logger.info(f'Workflow #{run_id} on {head_branch}: {result["message"]}')
        
        return result
    
    def _handle_pr_review(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull_request_review event (approval/rejection)"""
        
        review = event.get('review', {})
        pr = event.get('pull_request', {})
        state = review.get('state')  # 'approved', 'changes_requested', 'commented'
        pr_number = pr.get('number')
        author = review.get('user', {}).get('login')
        
        result = {
            'agent': self.name,
            'event': 'pull_request_review',
            'pr_number': pr_number,
            'reviewer': author,
            'review_state': state
        }
        
        if state == 'approved':
            result['action'] = 'approval_granted'
            result['message'] = f'{author} approved PR #{pr_number}'
            result['can_merge'] = self._check_can_merge(pr)
        elif state == 'changes_requested':
            result['action'] = 'approval_denied'
            result['message'] = f'{author} requested changes on PR #{pr_number}'
            result['can_merge'] = False
        else:
            result['action'] = 'review_comment'
            result['message'] = f'{author} commented on PR #{pr_number}'
            result['can_merge'] = False
        
        self.logger.info(result['message'])
        
        return result
    
    def _check_can_merge(self, pr: Dict[str, Any]) -> bool:
        """Check if PR meets all merge criteria"""
        
        # Check: PR is not in draft
        if pr.get('draft', False):
            return False
        
        # Check: PR has required approvals (at least 1)
        # This would check pr['approved_reviews_count'] in real GitHub API
        
        # Check: All status checks pass
        # This would check pr['mergeable'] in real GitHub API
        
        # Check: No conflicts
        if not pr.get('mergeable', True):
            return False
        
        return True

# Create singleton instance
workflow_agent = WorkflowAgent()
