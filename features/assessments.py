"""
Assessment Generator
===================

Generates brutally honest productivity assessments.

Creates:
- Daily debriefs (10 PM)
- Weekly reviews (Sundays)
- Monthly analyses (last day of month)
- Quarterly reality checks (every 3 months)

By OkayYouGotMe
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from database.operations import (
    get_user_by_id, get_completion_stats, get_pending_tasks,
    create_assessment, get_user_tasks
)
from database.models import User, MotivationStyle
from config.settings import BRUTAL_HONESTY_LEVEL, SCORE_OUT_OF, COMPLETION_THRESHOLDS
from ai.claude_engine import claude

logger = logging.getLogger(__name__)


class AssessmentGenerator:
    """
    Generates honest productivity assessments.
    
    Analyzes user's performance and provides actionable feedback.
    """
    
    def __init__(self):
        """Initialize assessment generator"""
        logger.info("📊 Assessment Generator initialized")
    
    
    async def generate_daily_assessment(self, user: User) -> str:
        """
        Generate daily assessment.
        
        Runs at 10 PM every day.
        
        Args:
            user: User object
        
        Returns:
            Assessment text
        """
        try:
            # Get stats for today
            stats = get_completion_stats(user.id, days=1)
            pending = get_pending_tasks(user.id)
            
            # Build prompt for Claude
            prompt = self._build_assessment_prompt(
                user=user,
                assessment_type="daily",
                stats=stats,
                pending_count=len(pending)
            )
            
            # Generate assessment with Claude
            assessment_text = await self._generate_with_claude(prompt, user)
            
            # Calculate score
            score = self._calculate_score(stats['completion_rate'])
            
            # Save to database
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = datetime.utcnow()
            
            create_assessment(
                user_id=user.id,
                assessment_type="daily",
                period_start=today_start,
                period_end=today_end,
                assessment_text=assessment_text,
                tasks_completed=stats['completed_count'],
                tasks_planned=stats['tasks_created'],
                completion_rate=stats['completion_rate'],
                score=score
            )
            
            logger.info(f"📊 Daily assessment generated for {user.name}: {score}/10")
            
            return assessment_text
        
        except Exception as e:
            logger.error(f"❌ Error generating daily assessment: {e}")
            return "Couldn't generate assessment today. Try again tomorrow!"
    
    
    async def generate_weekly_assessment(self, user: User) -> str:
        """
        Generate weekly assessment.
        
        Runs on Sundays at 10 PM.
        
        Args:
            user: User object
        
        Returns:
            Assessment text
        """
        try:
            # Get stats for the week
            stats = get_completion_stats(user.id, days=7)
            
            # Build prompt
            prompt = self._build_assessment_prompt(
                user=user,
                assessment_type="weekly",
                stats=stats
            )
            
            # Generate with Claude
            assessment_text = await self._generate_with_claude(prompt, user)
            
            # Calculate score
            score = self._calculate_score(stats['completion_rate'])
            
            # Save to database
            week_start = datetime.utcnow() - timedelta(days=7)
            week_end = datetime.utcnow()
            
            create_assessment(
                user_id=user.id,
                assessment_type="weekly",
                period_start=week_start,
                period_end=week_end,
                assessment_text=assessment_text,
                tasks_completed=stats['completed_count'],
                tasks_planned=stats['tasks_created'],
                completion_rate=stats['completion_rate'],
                score=score
            )
            
            logger.info(f"📊 Weekly assessment generated for {user.name}: {score}/10")
            
            return assessment_text
        
        except Exception as e:
            logger.error(f"❌ Error generating weekly assessment: {e}")
            return "Couldn't generate weekly assessment."
    
    
    def _build_assessment_prompt(
        self,
        user: User,
        assessment_type: str,
        stats: Dict,
        pending_count: int = 0
    ) -> str:
        """
        Build prompt for Claude to generate assessment.
        
        Args:
            user: User object
            assessment_type: daily, weekly, monthly, quarterly
            stats: Completion statistics
            pending_count: Number of pending tasks
        
        Returns:
            Prompt string
        """
        prompt = f"""Generate a {assessment_type} productivity assessment for {user.name}.

USER PROFILE:
- Profession: {user.profession or 'Not specified'}
- Goals: {', '.join(user.goals) if user.goals else 'Not specified'}
- Motivation Style: {user.motivation_style.value if user.motivation_style else 'direct'}

STATISTICS:
- Tasks Created: {stats['tasks_created']}
- Tasks Completed: {stats['completed_count']}
- Completion Rate: {stats['completion_rate']}%
- On-Time Rate: {stats['on_time_rate']}%
{f'- Pending Tasks: {pending_count}' if pending_count > 0 else ''}

BRUTAL HONESTY LEVEL: {BRUTAL_HONESTY_LEVEL}

REQUIREMENTS:
1. Be {BRUTAL_HONESTY_LEVEL}ly honest about their performance
2. Point out specific patterns (procrastination, avoidance, etc.)
3. Acknowledge wins but don't sugarcoat failures
4. Provide actionable next steps
5. Score them out of {SCORE_OUT_OF}
6. Match their motivation style ({user.motivation_style.value if user.motivation_style else 'direct'})

FORMAT:
═══════════════════════════════════════════════════
{assessment_type.upper()} DEBRIEF - {datetime.utcnow().strftime('%B %d, %Y')}
═══════════════════════════════════════════════════

COMPLETED: X/Y tasks (Z%)

THE TRUTH:
[Your honest assessment - no holding back]

WHAT WORKED:
[List specific wins]

WHAT DIDN'T:
[List specific failures/avoidances]

PATTERNS DETECTED:
[Behavior patterns you notice]

TOMORROW'S PRIORITY / NEXT WEEK'S FOCUS:
[Specific actionable steps]

SCORE: X/{SCORE_OUT_OF}
[One sentence justification]

═══════════════════════════════════════════════════

Write the assessment now:
"""
        
        return prompt
    
    
    async def _generate_with_claude(self, prompt: str, user: User) -> str:
        """
        Generate assessment using Claude.
        
        Args:
            prompt: Assessment prompt
            user: User object
        
        Returns:
            Generated assessment text
        """
        try:
            # Use Claude to generate
            from anthropic import Anthropic
            from config.settings import CLAUDE_API_KEY, CLAUDE_MODEL
            
            client = Anthropic(api_key=CLAUDE_API_KEY)
            
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            assessment = response.content[0].text.strip()
            
            return assessment
        
        except Exception as e:
            logger.error(f"❌ Error generating with Claude: {e}")
            return self._generate_fallback_assessment(user, "daily")
    
    
    def _calculate_score(self, completion_rate: int) -> int:
        """
        Calculate score based on completion rate.
        
        Args:
            completion_rate: Percentage (0-100)
        
        Returns:
            Score (0-10)
        """
        if completion_rate >= COMPLETION_THRESHOLDS['excellent']:
            return 9  # 9-10
        elif completion_rate >= COMPLETION_THRESHOLDS['good']:
            return 7  # 7-8
        elif completion_rate >= COMPLETION_THRESHOLDS['average']:
            return 6  # 6
        elif completion_rate >= COMPLETION_THRESHOLDS['below_average']:
            return 4  # 4-5
        else:
            return 3  # 3 or below
    
    
    def _generate_fallback_assessment(
        self,
        user: User,
        assessment_type: str
    ) -> str:
        """
        Generate basic assessment if Claude fails.
        
        Args:
            user: User object
            assessment_type: Type of assessment
        
        Returns:
            Basic assessment text
        """
        stats = get_completion_stats(user.id, days=1 if assessment_type == "daily" else 7)
        
        assessment = f"""═══════════════════════════════════════════════════
{assessment_type.upper()} ASSESSMENT
═══════════════════════════════════════════════════

COMPLETED: {stats['completed_count']}/{stats['tasks_created']} tasks ({stats['completion_rate']}%)

"""
        
        rate = stats['completion_rate']
        
        if rate >= 80:
            assessment += "THE TRUTH:\nStrong performance. You're executing well.\n\n"
        elif rate >= 60:
            assessment += "THE TRUTH:\nDecent work, but there's room for improvement.\n\n"
        else:
            assessment += "THE TRUTH:\nBelow expectations. Time to step it up.\n\n"
        
        score = self._calculate_score(rate)
        assessment += f"SCORE: {score}/{SCORE_OUT_OF}\n"
        
        assessment += "\n═══════════════════════════════════════════════════"
        
        return assessment


# Create global instance
assessor = AssessmentGenerator()
