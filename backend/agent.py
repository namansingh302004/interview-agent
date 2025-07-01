import logging
import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    metrics,
    RunContext,
)
from livekit.agents.llm import function_tool
from livekit.plugins import openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("interview-agent")
load_dotenv()

user_info = {
    "language": "English",
    "name": "Naman Kumar Singh",
    "role": "Software Engineer",
    "iq": [
        "What is a REST API?",
        "Can you explain how Python's GIL works?",
        "Tell me about a time you debugged a difficult issue.",
        "How do you handle version control conflicts?",
        "What are Python decorators and use cases?"
    ],
}

@dataclass
class InterviewData:
    questions_answered: int = 0
    current_question_index: int = 0

class InterviewAgent(Agent):
    def __init__(self, ctx) -> None:
        super().__init__(
            instructions=f"""
            Your name is Areeva and you are a professional job interviewer conducting an interview in {user_info["language"]} for a {user_info["role"]} position.
            
            You will:
            1. Start by asking for an introduction
            2. Ask technical questions from the provided list
            3. Ask follow-up questions based on responses
            4. Keep responses concise and professional
            5. Use the ask_questions function to move to the next question
            
            You are interviewing {(user_info["name"].split(" "))[0]}.
            Do not evaluate responses during the interview - just acknowledge and move forward.
            Keep your responses brief and to the point.
            """
        )
        self.ctx = ctx
        self.timer_task = None

    async def on_enter(self):
        logger.info("Agent entering session")
        await self.session.say(
            f"Hello {(user_info['name'].split(' '))[0]}, I am Areeva. Let's begin the interview. Please introduce yourself and share your background.",
            add_to_chat_ctx=False
        )

    @function_tool
    async def ask_questions(self, context: RunContext[InterviewData]) -> str:
        """Move to the next interview question
        
        Args:
            context: The current run context with interview data
            
        Returns:
            The next question to ask the candidate
        """
        try:
            context.userdata.questions_answered += 1
            logger.info(f"Questions answered: {context.userdata.questions_answered}")

            # Check if interview is complete
            if context.userdata.questions_answered >= 5:
                await self.session.say("That concludes our interview. Thank you for your time and best of luck!")
                return "Interview completed"

            # Get the next question
            question_index = context.userdata.questions_answered - 1
            if question_index < len(user_info['iq']):
                question = user_info['iq'][question_index]
                return f"Thank you for that answer. Here's your next question: {question}"
            else:
                return "Thank you. Can you elaborate more on your previous answer or share another example?"

        except Exception as e:
            logger.error(f"Error in ask_questions: {e}")
            return "Let me ask you another question."

def prewarm(proc: JobProcess):
    """Preload models for better performance"""
    try:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("VAD model preloaded successfully")
    except Exception as e:
        logger.error(f"Error preloading VAD: {e}")

async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    try:
        logger.info("Starting interview agent...")
        
        # Connect to room and wait for participant
        await ctx.connect()
        logger.info("Connected to room")
        
        await ctx.wait_for_participant()
        logger.info("Participant joined")

        # Create agent session with proper configuration
        session = AgentSession(
            vad=ctx.proc.userdata.get("vad"),
            llm=openai.LLM(
                model="gpt-4o-mini",
                temperature=0.7
            ),
            stt=openai.STT(
                model="whisper-1",
                language="en"
            ),
            tts=openai.TTS(
                voice="shimmer",
                speed=1.0
            ),
            userdata=InterviewData(),  # Initialize userdata here
            turn_detection=MultilingualModel(),
            allow_interruptions=True,
            min_endpointing_delay=1.5,
            max_endpointing_delay=3.0,
        )

        # Set up usage tracking
        usage_collector = metrics.UsageCollector()

        async def log_usage():
            try:
                summary = usage_collector.get_summary()
                logger.info(f"Session usage: {summary}")
            except Exception as e:
                logger.error(f"Error logging usage: {e}")

        ctx.add_shutdown_callback(log_usage)

        # Start the session
        await session.start(
            agent=InterviewAgent(ctx),
            room=ctx.room
        )

    except Exception as e:
        logger.error(f"Error in entrypoint: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm
        )
    )
