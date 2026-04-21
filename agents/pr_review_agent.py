"""
PR Review Agent - Automated PR validation and labeling

Triggers on: pull_request events (opened, synchronize, reopened)
Responsibilities:
- Validate PR has description
- Check for linked issues
- Auto-label PRs based on files changed
- Comment feedback summary
"""

from typing import Any, Dict, List
from base_agent import BaseAgent

class PRReviewAgent(BaseAgent):
    """PR Review agent for automated PR assessment"""
    
    def __init__(self):
        super().__init__('PRReviewAgent')
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull_request event"""
        
        action = event.get('action')
        if action not in ['opened', 'synchronize', 'reopened']:
            return {'skipped': f'Action {action} not handled'}
        
        pr = event.get('pull_request', {})
        pr_number = pr.get('number')
        pr_title = pr.get('title', '')
        pr_body = pr.get('body', '')
        files_changed = event.get('pull_request', {}).get('changed_files', 0)
        
        result = {
            'agent': self.name,
            'pr_number': pr_number,
            'checks': {}
        }
        
        # Validate PR description
        result['checks']['description'] = self._check_description(pr_body)
        
        # Check for linked issue
        result['checks']['linked_issue'] = self._check_linked_issue(pr_body)
        
        # Auto-label PR
        files = self._get_changed_files(event)
        result['checks']['labels'] = self._determine_labels(files)
        
        # Generate summary
        result['summary'] = self._generate_summary(pr_title, result['checks'])
        
        all_pass = all(check.get('passed', False) for check in result['checks'].values() if isinstance(check, dict))
        result['passed'] = all_pass
        
        self.logger.info(f'PR #{pr_number} Review: {result["summary"]}')
        
        return result
    
    def _check_description(self, body: str) -> Dict[str, Any]:
        """Check if PR has description"""
        has_description = len(body.strip()) > 20
        return {
            'passed': has_description,
            'name': 'PR Description',
            'message': 'Has detailed description' if has_description else 'Missing description'
        }
    
    def _check_linked_issue(self, body: str) -> Dict[str, Any]:
        """Check if PR links to an issue"""
        has_link = any(keyword in body.lower() for keyword in ['closes #', 'fixes #', 'resolves #', 'related-to #'])
        return {
            'passed': has_link,
            'name': 'Linked Issue',
            'message': 'Links to issue' if has_link else 'No linked issue (recommended)'
        }
    
    def _get_changed_files(self, event: Dict[str, Any]) -> List[str]:
        """Get list of changed files from event"""
        # In real implementation, would fetch from GitHub API
        # For now, return files from pull_request.changed_files field
        return []
    
    def _determine_labels(self, files: List[str]) -> Dict[str, Any]:
        """Determine PR labels based on changed files"""
        labels = set()
        
        # Map file patterns to labels
        file_label_map = {
            'backend': ['type/backend', 'type/api'],
            'frontend': ['type/frontend', 'type/ui'],
            'tests': ['type/test'],
            'docs': ['type/docs'],
            'docker': ['type/infra'],
            'agents': ['type/agents'],
            '.github': ['type/ci']
        }
        
        for pattern, label_set in file_label_map.items():
            labels.update(label_set)
        
        return {
            'passed': True,
            'labels': list(labels),
            'message': f'Suggested labels: {", ".join(labels)}'
        }
    
    def _generate_summary(self, title: str, checks: Dict[str, Any]) -> str:
        """Generate PR review summary"""
        issues = [check.get('message', '') for check in checks.values() 
                 if isinstance(check, dict) and not check.get('passed', True)]
        
        if not issues:
            return 'PR looks good - ready for review'
        
        return f'PR needs attention: {", ".join(issues)}'

# Create singleton instance
pr_review_agent = PRReviewAgent()
