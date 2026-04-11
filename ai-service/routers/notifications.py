import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter()

class NotificationRequest(BaseModel):
    student_name: str
    event_type: str
    event_data: str

class NotificationResponse(BaseModel):
    message: str
    metadata: dict = {}

NOTIFICATION_PROMPT = """
You are ARIA generating a short, friendly push notification for {student_name}.

## Event Type: {event_type}
Possible values: application_status_changed, new_project_matching_profile, supervisor_message, deadline_reminder, skill_gap_report_ready

## Event Data
{event_data}

## Task
Write a single notification message (max 2 sentences) that:
- Is warm and personal (use the student's first name)
- Clearly states what happened and what action to take (if any)
- Matches the urgency of the event (deadline reminders are more urgent than new project alerts)

Return only the notification text. No JSON, no markdown.
"""

def get_llm(temperature: float = 0.5):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

@router.post("/generate-notification", response_model=NotificationResponse)
async def generate_notification(request: NotificationRequest):
    """Generate dynamic AI notification text."""
    llm = get_llm(temperature=0.5)
    if not llm:
        # Simple fallback template
        return NotificationResponse(
            message=f"Bonjour {request.student_name}, vous avez une nouvelle notification concernant : {request.event_type}.",
            metadata={"provider": "fallback"}
        )

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", NOTIFICATION_PROMPT)
        ])
        chain = prompt | llm
        
        response = chain.invoke(request.dict())
        
        return NotificationResponse(
            message=response.content.strip(),
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Notification error: {e}")
        return NotificationResponse(
            message=f"Nouvelle notification : {request.event_type}",
            metadata={"provider": "fallback"}
        )
