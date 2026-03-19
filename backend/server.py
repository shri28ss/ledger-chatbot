from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from chatbot import chatbot # Import the existing bot logic

app = FastAPI()

# Enable CORS for the local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    user_id: str

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    try:
        response_text = chatbot(req.query, req.user_id)
        return {"response": response_text}
    except Exception as e:
        return {"response": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting Chatbot API Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
