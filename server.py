import logging
import anyio
from fastmcp import FastMCP
from notebooklm import NotebookLMClient

# Initialize FastMCP server
mcp = FastMCP("NotebookLM")

# Client instance (singleton for the session)
_client = None

async def get_client():
    global _client
    if _client is None:
        try:
            _client = await NotebookLMClient.from_storage()
            await _client.__aenter__()
        except Exception as e:
            logging.error(f"Failed to initialize NotebookLM client: {e}")
            raise RuntimeError("NotebookLM authentication failed. Please run 'notebooklm login' in your terminal.")
    return _client

@mcp.tool()
async def list_notebooks():
    """List all notebooks in your NotebookLM account."""
    client = await get_client()
    notebooks = await client.notebooks.list()
    return [{"id": nb.id, "title": nb.title, "source_count": nb.source_count} for nb in notebooks]

@mcp.tool()
async def create_notebook(title: str):
    """Create a new notebook with the given title."""
    client = await get_client()
    notebook = await client.notebooks.create(title)
    return {"id": notebook.id, "title": notebook.title}

@mcp.tool()
async def add_source_url(notebook_id: str, url: str):
    """Add a website URL as a source to a notebook."""
    client = await get_client()
    source = await client.sources.add_url(notebook_id, url)
    return {"id": source.id, "title": source.title}

@mcp.tool()
async def add_source_text(notebook_id: str, title: str, text: str):
    """Add raw text as a source to a notebook."""
    client = await get_client()
    source = await client.sources.add_text(notebook_id, title, text)
    return {"id": source.id, "title": source.title}

@mcp.tool()
async def ask_notebook(notebook_id: str, question: str):
    """Ask a question based on the sources in a specific notebook."""
    client = await get_client()
    result = await client.chat.ask(notebook_id, question)
    return {"answer": result.text, "sources": [s.title for s in result.sources]}

@mcp.tool()
async def get_notebook_summary(notebook_id: str):
    """Get the summary and key insights of a notebook."""
    client = await get_client()
    # Using chat to get summary if there's no direct summary API
    result = await client.chat.ask(notebook_id, "Please provide a comprehensive summary and key insights of this notebook.")
    return {"summary": result.text}

@mcp.tool()
async def generate_video_overview(notebook_id: str, instructions: str = "Create an engaging video overview of these sources."):
    """
    Generate a Video Overview artifact in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_video(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_audio_overview(notebook_id: str, instructions: str = "Create a deep dive podcast-style overview."):
    """
    Generate an Audio Overview (Deep Dive podcast) in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_audio(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_slide_deck(notebook_id: str, instructions: str = "Create a comprehensive slide deck."):
    """
    Generate a Slide Deck (PowerPoint style) in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_slide_deck(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_mind_map(notebook_id: str):
    """
    Generate an interactive Mind Map in NotebookLM.
    This creates a mind map and saves it as a note.
    """
    client = await get_client()
    result = await client.artifacts.generate_mind_map(notebook_id)
    return {"note_id": result.get("note_id"), "status": "Mind map generated and saved to notes."}

@mcp.tool()
async def generate_infographic(notebook_id: str, instructions: str = "Create an informative infographic."):
    """
    Generate an Infographic in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_infographic(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_quiz(notebook_id: str, instructions: str = "Create a quiz based on these sources."):
    """
    Generate a Quiz in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_quiz(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_flashcards(notebook_id: str, instructions: str = "Create study flashcards."):
    """
    Generate Flashcards in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_flashcards(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_summary_report(notebook_id: str, instructions: str = "Create a briefing document."):
    """
    Generate a Summary Report (Briefing Doc) in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_report(notebook_id, custom_prompt=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

@mcp.tool()
async def generate_data_table(notebook_id: str, instructions: str = "Extract key data into a table."):
    """
    Generate a Data Table artifact in NotebookLM.
    """
    client = await get_client()
    status = await client.artifacts.generate_data_table(notebook_id, instructions=instructions)
    return {"task_id": status.task_id, "status": "Task started. Check NotebookLM studio."}

if __name__ == "__main__":
    mcp.run()
