import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

from .ai_agent import AIAgent
from .chat_manager import ChatManager
from .config import config
from chat_app.database.database import Database
from .llm_providers.ollama_llm import OllamaLLM
from .llm_providers.openai_llm import OpenAIResponsesLLM

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.start()
    # run the AI agent in the background
    logger.info("Starting AI agent ...")
    asyncio.create_task(ai_agent.run())
    yield
    logger.info("Stopping AI agent ...")
    ai_agent.stop()
    db.stop()


# Initialize components
db = Database()
chat_manager = ChatManager(db)
event_bus = asyncio.Queue()
ai_agent = AIAgent(
    event_bus,
    chat_manager,
    llm=OllamaLLM(chat_manager) if config.use_ollama else OpenAIResponsesLLM(chat_manager),
)


app = FastAPI(lifespan=lifespan)


# simple HTML frontend, taken from FastAPI documentation
# https://fastapi.tiangolo.com/advanced/websockets/#websockets
# Later, modified by an LLM to add client_id logic.
@app.get("/")
async def get():
    with open(config.index_html) as f:
        return HTMLResponse(f.read())


# The client passes a `client_id` in the query string (stored in sessionStorage on the client)
# Initially, I had the server generate a UUID as the client_id (just to get something working).
# The problem with that approach is that the client_id would change every time the page is reloaded,
# which would break the chat history.
# By moving that logic to the client-side, and storing it in sessionStorage, we can maintain the chat history
# across page reloads.
# Note: this is meant to be a simple approach to maintain chat history only across page reloads. If a tab is
# closed and reopened the client_id will change, and the chat history will not be preserved.

# I used the help of an LLM to consider different approaches, and to modify the HTML and JS.
# I also used the LLM to modify the HTML and JS to separate chat history from live messages.
# I developed the logic in the server (in `chat_manager.connect()`) to retrieve the chat history (if it exists)
# when a client connects and send it to the websocket.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str = Query(...)):
    await chat_manager.connect(client_id, websocket)
    logger.info(f"Session created with client_id: '{client_id}'")

    try:
        while True:
            message = await websocket.receive_text()

            # persist message
            chat_manager.store_message(client_id, "user", message)
            # display the user's message on the UI (live conversation)
            await chat_manager.send_live_message(client_id, "user", message)

            # publish to event bus for AI agent to process
            await event_bus.put((client_id, message))
    except WebSocketDisconnect:
        chat_manager.disconnect(client_id)
