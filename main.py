from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import traceback
from dotenv import load_dotenv
from openai import OpenAI


import tools

load_dotenv()

app = FastAPI(
    title="Khana Darbaar API",
    description=" Agentic Dining Engine with fallback heuristics.",
    version="2.1.0"
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]


class AgentResponse(BaseModel):
    answer: str
    intent: str
    params: Dict[str, Any]
    data_source: str




@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "2.1.0"}


@app.get("/restaurants")
async def get_restaurants():
    return tools.RESTAURANTS


@app.get("/reservations")
async def get_reservations():
    return tools.RESERVATIONS if hasattr(tools, 'RESERVATIONS') else []


@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Executing Agentic Loop for: {request.message}")

       
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_restaurants",
                    "description": "Searches for real-world dining venues. Use this for specific cuisines, ratings, or general discovery.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cuisine": {"type": "string",
                                        "description": "Specific food type. Broaden this (e.g., 'Asian') if the specific one (e.g., 'Sushi') might be niche."},
                            "location": {"type": "string", "description": "City or specific neighborhood."},
                            "min_rating": {"type": "number"}
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "make_reservation",
                    "description": "Finalizes a table booking.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "restaurant_id": {"type": "integer"},
                            "party_size": {"type": "integer"},
                            "time": {"type": "string"}
                        },
                        "required": ["restaurant_id", "party_size", "time"]
                    }
                }
            }
        ]

        
        system_instructions = (
            "You are a Pro-Tier Concierge for 'Khana Darbaar'. "
            "Strategy: If search results are sparse or niche (like Sushi in a small city), "
            "do NOT say data is unavailable. Instead, identify the best Pan-Asian or "
            "International venues from the results and present them confidently as the top alternatives. "
            "Always prioritize actionable advice over vague disclaimers."
        )

        messages = [{"role": "system", "content": system_instructions}]
        messages.extend([m.model_dump() for m in request.history])
        messages.append({"role": "user", "content": request.message})

  
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            temperature=0.2  
        )

        response_message = response.choices[0].message


        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            intent = tool_call.function.name

      

            if intent == "search_restaurants":
                result = await tools.search_restaurants_pro_free(args)
                data_source = "Hybrid-Engine (OSM+Scraper)"
            else:
                result = tools.make_reservation_logic(args)
                data_source = "Internal-Booking-System"

       
            final_resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    *messages,
                    response_message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    }
                ]
            )

            return AgentResponse(
                answer=final_resp.choices[0].message.content,
                intent=intent,
                params=args,
                data_source=data_source
            )


        return AgentResponse(
            answer=response_message.content,
            intent="general",
            params={},
            data_source="Internal-LLM"
        )

    except Exception as e:
        print("CRITICAL BACKEND ERROR ")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
