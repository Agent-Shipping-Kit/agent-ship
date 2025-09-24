"""Main entry point for the medical followup generation agent."""

import asyncio
import hashlib
from src.agents.followups_generation.main_agent import MedicalFollowupAgent
from src.agents.followups_generation.main_agent import FollowupQuestionsInput
from src.agents.followups_generation.main_agent import FollowupQuestionsOutput
from src.agents.models import ConversationTurn
from src.log_settings import configure_logging
import logging


configure_logging()
logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating the medical followup agent."""
    
    agent = MedicalFollowupAgent()
        
    # Generate a deterministic session ID
    user_id = "123"
    query = "Patient: I have chest pain. Doctor: Can you describe it?"
    session_id = hashlib.md5(f"{user_id}_{query}".encode()).hexdigest()[:8]
    print(f"Generated session ID: {session_id}")
    
    # Create proper input using the schema
    input_data: FollowupQuestionsInput = FollowupQuestionsInput(
        conversation=[
            ConversationTurn(speaker="Patient", text=query),
            ConversationTurn(speaker="Doctor", text="Can you describe it?"),
            ConversationTurn(speaker="Patient", text="It's a sharp, stabbing pain. It started after I lifted some heavy boxes at work."),
            ConversationTurn(speaker="Doctor", text="Have you had any shortness of breath or difficulty breathing?"),
            ConversationTurn(speaker="Patient", text="Yes, I feel a bit short of breath, especially when I walk up stairs."),
            ConversationTurn(speaker="Doctor", text="Any fever or cough?"),
            ConversationTurn(speaker="Patient", text="No fever, but I do have a dry cough that started yesterday."),
        ],
        max_followups=5
    )
    
    result: FollowupQuestionsOutput = await agent.run(
        user_id=user_id,
        session_id=session_id,
        input_data=input_data
    )
    print(f"Agent response: {result}")
    print(f"Followup questions: {result.followup_questions}")
    print(f"Number of questions: {result.count}")

if __name__ == "__main__":
    asyncio.run(main())
