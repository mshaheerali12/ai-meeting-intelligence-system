import asyncio
from graph import graph_building
from meeting_nodes import transcription_node, summarizer_node
from pdfs import pdf_node


async def main():

    # Build graph
    app_graph = await graph_building()

    file_path = "2.mp3"

    # Read audio file
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    initial_state = {
        "audio_bytes": audio_bytes
    }

    result = {}

    print("\n🚀 Processing audio...\n")

    # Run graph silently (no node update printing)
    async for chunk in app_graph.astream(initial_state):
        for node_output in chunk.values():
            result.update(node_output)

    # Ensure transcription exists
    if "transcription" not in result:
        raise ValueError("Transcription not found in graph output.")

    print("\n================ FORMATTED TRANSCRIPTION ================\n")
    print(result["transcription"])
    print("\n=========================================================\n")

    # 🔁 Allow user to refine transcription
    while True:

        instruction = input(
            "\nGive instruction to improve transcription "
            "(or type 'approve' to continue):\n> "
        )

        if instruction.lower() == "approve":
            break

        updated = await transcription_node({
            "raw_transcription": result["raw_transcription"],
            "instruction": instruction
        })

        result["transcription"] = updated["transcription"]

        print("\n================ UPDATED TRANSCRIPTION ================\n")
        print(result["transcription"])
        print("\n=======================================================\n")

    # ✅ Generate summary AFTER approval
    print("\n📝 Generating Summary...\n")

    summary = await summarizer_node({
        "transcription": result["transcription"]
    })

    result["summary"] = summary["summary"]

    # ✅ Generate PDF
    print("📄 Generating PDF...\n")

    pdf_result = await pdf_node(result)

    with open("output.pdf", "wb") as f:
        f.write(pdf_result["pdf_bytes"])

    print("✅ PDF Generated Successfully: output.pdf")


if __name__ == "__main__":
    asyncio.run(main())