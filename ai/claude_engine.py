"""
Claude AI Engine
================

The brain of the AI Task Assistant.

Handles all communication with Claude API and manages context.
Provides intelligent, context-aware responses.

By OkayYouGotMe
"""

import logging
from anthropic import Anthropic
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from config.settings import (
    CLAUDE_API_KEY, CLAUDE_MODEL, AI_TEMPERATURE,
    MAX_CONVERSATION_MEMORY, BRUTAL_HONESTY_LEVEL
)
from database.models import User, MotivationStyle
from database.operations import get_conversation_history

logger = logging.getLogger(__name__)


class ClaudeEngine:
    """
    Main AI engine powered by Claude.
    
    Handles:
    - Natural conversation
    - Intent detection
    - Context awareness
    - Personalized responses
    """
    
    def __init__(self):
        """Initialize Claude AI client"""
        self.client = Anthropic(api_key=CLAUDE_API_KEY)
        self.model = CLAUDE_MODEL
        logger.info("🧠 Claude AI Engine initialized")
    
    
    def _build_system_prompt(self, user: User) -> str:
        """
        Build personalized system prompt based on user profile.
        
        This is where we give Claude context about the user
        and how to respond to them.
        
        Args:
            user: User object with profile info
        
        Returns:
            System prompt string
        """
        # Base identity
        prompt = f"""You are an AI Task Assistant helping {user.name or 'a user'}.

Your purpose is to help them stay productive through:
- Natural conversation (no robotic commands)
- Smart task management
- Honest feedback
- Goal accountability

"""
        
        # Add user context
        if user.profession:
            prompt += f"USER CONTEXT:\n- Profession: {user.profession}\n"
        
        if user.work_schedule:
            prompt += f"- Schedule: {user.work_schedule}\n"
        
        if user.goals:
            goals_text = "\n  ".join([f"• {goal}" for goal in user.goals])
            prompt += f"- Goals:\n  {goals_text}\n"
        
        prompt += "\n"
        
        # Add motivation style
        motivation_style = user.motivation_style.value if user.motivation_style else "direct"
        
        prompt += f"COMMUNICATION STYLE:\n"
        
        if motivation_style == "gentle":
            prompt += """- Use soft, encouraging language
- Gentle nudges, not harsh criticism
- Focus on progress, not perfection
- Be patient and understanding
"""
        
        elif motivation_style == "direct":
            prompt += """- Be brutally honest - no sugarcoating
- Call out procrastination and excuses
- Direct, straightforward feedback
- Challenge them to do better
"""
        
        elif motivation_style == "celebrate":
            prompt += """- Celebrate every win, big or small
- High energy, enthusiastic tone
- Focus on achievements
- Build momentum with positivity
"""
        
        else:  # factual
            prompt += """- Just the facts, no fluff
- Concise, clear communication
- Data-driven feedback
- Minimal emotional language
"""
        
        # Add behavioral guidelines
        prompt += f"""
GUIDELINES:
1. Understand context - remember what you talked about before
2. Detect intent - figure out what they want (add task, complete, chat, etc.)
3. Be proactive - offer to help before they ask
4. Break down overwhelm - simplify big tasks
5. Redirect distractions - guide back to goals when off-track
6. Stay natural - talk like a human, not a robot

BRUTAL HONESTY LEVEL: {BRUTAL_HONESTY_LEVEL}
- If "high": Be very direct about failures and patterns
- If "medium": Balanced honesty with encouragement  
- If "low": Gentle feedback, focus on positives

Remember: You're helping them WIN at life, not just manage tasks.
"""
        
        return prompt
    
    
    def _format_conversation_history(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Get formatted conversation history for context.
        
        Args:
            user_id: User's database ID
            limit: Number of recent messages to include
        
        Returns:
            List of message dicts for Claude API
        """
        history = get_conversation_history(user_id, limit=limit)
        
        # Convert to Claude message format (newest last)
        messages = []
        for conv in reversed(history):
            messages.append({"role": "user", "content": conv.user_message})
            messages.append({"role": "assistant", "content": conv.ai_response})
        
        return messages
    
    
    def analyze_intent(
        self,
        user_message: str,
        user: User,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Analyze what the user wants to do.
        
        Detects intent like:
        - add_task
        - complete_task
        - add_idea
        - view_tasks
        - chat
        - etc.
        
        Args:
            user_message: What the user said
            user: User object
            conversation_history: Recent conversation (optional)
        
        Returns:
            Dict with intent, confidence, extracted_data
        """
        try:
            # Build analysis prompt
            analysis_prompt = f"""Analyze this message and determine the user's intent.

User message: "{user_message}"

Possible intents:
- add_task: User wants to add a new task/reminder
- complete_task: User completed a task
- add_idea: User wants to save an idea (OTR)
- view_tasks: User wants to see their tasks
- view_ideas: User wants to see their ideas
- ask_question: User has a question (weather, news, how-to, etc.)
- chat: Just casual conversation

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "intent": "the_detected_intent",
  "confidence": 85,
  "task_name": "extracted task name if applicable",
  "task_id": "task number if mentioned (like 'task 1')",
  "idea": "extracted idea if applicable",
  "category": "auto-detected category",
  "question_topic": "topic of question if asking something",
  "reasoning": "brief explanation of why you chose this intent"
}}
"""
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.3,  # Lower temperature for analysis
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            # Parse response
            import json
            result_text = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            logger.info(f"💡 Intent detected: {result.get('intent')} (confidence: {result.get('confidence')}%)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing intent: {e}")
            # Default to chat if analysis fails
            return {
                "intent": "chat",
                "confidence": 50,
                "reasoning": "Failed to analyze, defaulting to chat"
            }
    
    
    def generate_response(
        self,
        user_message: str,
        user: User,
        context: Dict = None
    ) -> str:
        """
        Generate a natural, context-aware response.
        
        Args:
            user_message: What the user said
            user: User object with profile
            context: Additional context (tasks, stats, etc.)
        
        Returns:
            AI-generated response string
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(user)
            
            # Get conversation history
            history = self._format_conversation_history(user.id, limit=5)
            
            # Add current message
            current_messages = history + [{"role": "user", "content": user_message}]
            
            # Add context if provided
            if context:
                context_str = "\n\nCURRENT CONTEXT:\n"
                
                if "pending_tasks" in context:
                    context_str += f"- Pending tasks: {context['pending_tasks']}\n"
                
                if "completion_rate" in context:
                    context_str += f"- Completion rate: {context['completion_rate']}%\n"
                
                if "recent_pattern" in context:
                    context_str += f"- Recent pattern: {context['recent_pattern']}\n"
                
                # Add context to system prompt
                system_prompt += context_str
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=AI_TEMPERATURE,
                system=system_prompt,
                messages=current_messages
            )
            
            # Extract response text
            response_text = response.content[0].text.strip()
            
            logger.info(f"💬 Generated response ({len(response_text)} chars)")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "Sorry, I encountered an error. Can you try that again?"
    
    
    def break_down_task(
        self,
        task_name: str,
        user: User,
        estimated_time: int = None
    ) -> Dict:
        """
        Break a big task into smaller subtasks.
        
        Args:
            task_name: The task to break down
            user: User object
            estimated_time: Estimated time in minutes (optional)
        
        Returns:
            Dict with breakdown info (subtasks, total_time, etc.)
        """
        try:
            prompt = f"""Break down this task into manageable subtasks.

Task: "{task_name}"
{f"Estimated time: {estimated_time} minutes" if estimated_time else ""}

User context:
- Profession: {user.profession or 'Not specified'}
- Working style: {user.motivation_style.value if user.motivation_style else 'Unknown'}

Create 3-5 subtasks that:
1. Are specific and actionable
2. Have realistic time estimates
3. Follow a logical order
4. Are each under 60 minutes

Respond ONLY with valid JSON:
{{
  "should_break_down": true/false,
  "reasoning": "why this should/shouldn't be broken down",
  "subtasks": [
    {{"name": "Subtask 1", "estimated_time": 30, "order": 1}},
    {{"name": "Subtask 2", "estimated_time": 45, "order": 2}}
  ],
  "total_estimated_time": 75
}}
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            import json
            result_text = response.content[0].text.strip()
            
            # Clean markdown if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            logger.info(f"📋 Task breakdown: {len(result.get('subtasks', []))} subtasks")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error breaking down task: {e}")
            return {
                "should_break_down": False,
                "reasoning": "Error occurred during breakdown",
                "subtasks": [],
                "total_estimated_time": estimated_time or 0
            }
    
    
    def categorize_idea(self, idea_text: str, user: User) -> str:
        """
        Auto-categorize an idea.
        
        Args:
            idea_text: The idea to categorize
            user: User object for context
        
        Returns:
            Category string
        """
        try:
            prompt = f"""Categorize this idea into ONE category:

Idea: "{idea_text}"

User profession: {user.profession or 'Not specified'}

Available categories:
- Business
- Personal
- Creative
- Technology
- Health/Fitness
- Learning
- Finance
- Career
- Other

Respond with ONLY the category name, nothing else.
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            category = response.content[0].text.strip()
            
            logger.info(f"🏷️ Idea categorized as: {category}")
            return category
            
        except Exception as e:
            logger.error(f"❌ Error categorizing idea: {e}")
            return "General"
    
    
    def detect_procrastination(
        self,
        user_message: str,
        user: User,
        pending_urgent_tasks: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect if user is procrastinating.
        
        Args:
            user_message: What the user is asking about
            user: User object
            pending_urgent_tasks: Number of urgent tasks pending
        
        Returns:
            (is_procrastinating, redirect_message)
        """
        try:
            if pending_urgent_tasks == 0:
                return False, None
            
            prompt = f"""Is this person procrastinating?

They have {pending_urgent_tasks} urgent tasks pending.

They just asked: "{user_message}"

Is this:
a) Productive (relevant to their work/goals)
b) Procrastination (distraction from what they should do)

Respond with JSON:
{{
  "is_procrastinating": true/false,
  "reasoning": "brief explanation",
  "redirect_suggestion": "what they should focus on instead"
}}
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            result_text = response.content[0].text.strip()
            
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            is_procrastinating = result.get("is_procrastinating", False)
            redirect = result.get("redirect_suggestion") if is_procrastinating else None
            
            if is_procrastinating:
                logger.info(f"🎯 Procrastination detected: {result.get('reasoning')}")
            
            return is_procrastinating, redirect
            
        except Exception as e:
            logger.error(f"❌ Error detecting procrastination: {e}")
            return False, None


# Create global instance
claude = ClaudeEngine()
