import logging
import os
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, llm
from livekit.agents import Agent, AgentSession
from livekit.plugins import google, silero

from local_stt import LocalEnglishSpeechSTT
from local_tts import LocalEdgeTTS

load_dotenv(dotenv_path=".env")

logger = logging.getLogger("voice-agent")

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    instructions = (
        "You are a helpful voice assistant created by Team DeepThinkers. "
        "You understand and speak English very well. "
        "Always respond in English unless specifically asked to respond in a different language. "
        "Keep your responses concise, natural, and conversational."
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    # Initialize STT with your Colab Gradio URL
    # IMPORTANT: Replace this URL with your actual Gradio URL from Colab
    

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt = LocalEnglishSpeechSTT(
            api_url="https://d79ddf2d47a05d98d8.gradio.live/",
            username="deepthinkers",
            password="english2025",
            timeout=30,  # Optional: request timeout
            max_retries=3  # Optional: retry attempts
        ),
        llm=google.LLM(model="gemini-2.5-flash"),  # Gemini LLM
        tts=LocalEdgeTTS(voice="en-US-AriaNeural"),  # Edge TTS with English female voice
    )

    agent = Agent(instructions=instructions)

    await session.start(agent, room=ctx.room)

    await session.say("Hello! How can I assist you?", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))