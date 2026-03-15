from nodes.state import meemory
from nodes.pdf_gen import generate_meeting_pdf_bytes
async def pdf_node(state:meemory):
    pdf_bytes=generate_meeting_pdf_bytes(
        state.get("transcription"),
        state.get("summary")

    )
    return {"pdf_bytes": pdf_bytes  }
