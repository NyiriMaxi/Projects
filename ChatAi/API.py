from fastapi import FastAPI,HTTPException
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import uuid

load_dotenv()

API_KEY=os.getenv("GEMINI_API_KEY")

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


genai.configure(api_key=API_KEY)
model=genai.GenerativeModel('gemini-3-flash-preview')

sessions={}

class Message(BaseModel):

    session_id:str =None
    message:str

@app.post("/chat")
async def Chat(request:Message):
    if not request.session_id or request.session_id not in sessions:
        session_id=str(uuid.uuid4())
        sessions[session_id]=model.start_chat(history=[])
    else:
        session_id=request.session_id
    
    chat_session=sessions[session_id]

    try:
        response=chat_session.send_message(request.message)

        return{
            "session_id": session_id,
            "response": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@app.post("/reset")
async def Reset(session_id:str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message":"Session reset"}

@app.get("/")
async def root():
    return {"message": "Gemini Chatbot API running"}
    


