"""
Coding Agent - Automated code quality checks

Triggers on: push events (commits to PR branches)
Responsibilities:
- Run linting checks
- Run unit tests
- Check code style
- Add PR comments with results
"""

from typing import Any, Dict
from base_agent import BaseAgent
import subprocess
import json

class CodingAgent(BaseAgent):
    """Coding agent for automated quality checks"""
    
    def __init__(self):
        super().__init__('CodingAgent')
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push event and run code checks"""
        
        # Extract commit info
        ref = event.get('ref', '')
        if not ref.startswith('refs/heads/'):
            return {'skipped': 'Not a branch push'}
        
        branch_name = ref.replace('refs/heads/', '')
        commits = event.get('commits', [])
        
        if not commits:
            return {'skipped': 'No commits'}
        
        result = {
            'agent': self.name,
            'branch': branch_name,
            'checks': {}
        }
        
        # Run code quality checks
        result['checks']['lint'] = self._run_linting()
        result['checks']['tests'] = self._run_tests()
        result['checks']['formatting'] = self._check_formatting()
        
        # Overall result
        all_passed = all(check.get('passed', False) for check in result['checks'].values())
        result['passed'] = all_passed
        result['message'] = '✓ All checks passed' if all_passed else '✗ Some checks failed'
        
        self.logger.info(f'Coding checks on {branch_name}: {result["message"]}')
        
        return result
    
    def _run_linting(self) -> Dict[str, Any]:
        """Run flake8 linting"""
        try:
            result = subprocess.run(
                ['flake8', 'backend/', '--max-line-length=120'],
                capture_output=True,
                text=True,
                timeout=30
            )
            passed = result.returncode == 0
            return {
                'passed': passed,
                'tool': 'flake8',
                'output': result.stdout or result.stderr
            }
        except Exception as e:
            return {'passed': False, 'tool': 'flake8', 'error': str(e)}
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run pytest unit tests"""
        try:
            result = subprocess.run(
                ['pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            passed = result.returncode == 0
            return {
                'passed': passed,
                'tool': 'pytest',
                'output': result.stdout[-500:] if result.stdout else ''  # Last 500 chars
            }
        except Exception as e:
            return {'passed': False, 'tool': 'pytest', 'error': str(e)}
    
    def _check_formatting(self) -> Dict[str, Any]:
        """Check Python code formatting with black"""
        try:
            result = subprocess.run(
                ['black', 'backend/', '--check', '--quiet'],
                capture_output=True,
                text=True,
                timeout=30
            )
            passed = result.returncode == 0
            return {
                'passed': passed,
                'tool': 'black',
                'message': 'Code is properly formatted' if passed else 'Code needs formatting'
            }
        except Exception as e:
            return {'passed': False, 'tool': 'black', 'error': str(e)}

# Create singleton instance
coding_agent = CodingAgent()
