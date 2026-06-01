import os
import time 
import random 
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load env variables and setup database
from mockDatabase import (
    propertiesDB,
    marketingSpendDB,
    actionsDB,
    actionsAuditLogDB,
    cubeSchemaDB,
    execute_semantic_query,
    save_actions,
    occupancyTargetsDB
)

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Marketing Orchestrator FastAPI Gateway")

# Enable CORS (same mapping as Node.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"], # React dev server
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# 1. Payload Models
class ActionExecutionPayload(BaseModel):
    incomingVersion: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]

# 2. Shared Audit Logger
def create_audit_log(action_id: str, property_id: str, event_type: str, message: str):
    new_log = {
        "id": f"log-{int(time.time())}-{random.randint(1000, 9999)}",
        "actionId": action_id,
        "propertyId": property_id,
        "eventType": event_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    actionsAuditLogDB.append(new_log)
    print(f"[AUDIT LEDGER] [{event_type}] - {message}")

# 3. Async Decoupled Backgroun Task simulation
def simulate_background_sync(action_id: str, property_id: str):
    # Mimic a 3-second writeback process
    time.sleep(3)

    # Locate and transition status
    for action in actionsDB:
        if action["id"] == action_id:
            action["status"] = "SUCCESS"
            save_actions(actionsDB)
            create_audit_log(
                action_id,
                property_id, 
                "SYNC SUCCESS",
                f"Successfully synced optimized budget parameters for {action_id}. External API returned status 200 OK."
            )
            break

# 4. API Endpoint Handlers
@app.get("/api/actions")
def get_actions():
    return { "success": True, "actions": actionsDB}

@app.post("/api/analyze")
def trigger_analysis():
    # FIXED: Renamed loop variable from 'property' to 'prop' to avoid Python keyword collision
    for prop in propertiesDB:
        if prop["totalUnits"] == 0:
            continue
            
        occupancy_rate = prop["occupiedUnits"] / prop["totalUnits"]
        marketing = next((m for m in marketingSpendDB if m["propertyId"] == prop["id"]), None)

        # Anomaly criteria (matching original rules)
        if marketing and occupancy_rate >= 0.92 and marketing["monthlySpend"] >= 3000:
            # Check for existing action locks
            has_recent = False
            for a in actionsDB:
                if a["propertyId"] == prop["id"]:
                    is_pending_or_executing = a["status"] in ["PENDING", "EXECUTING"]
                    if is_pending_or_executing:
                        has_recent = True
                        break
            
            if not has_recent:
                proposed_reduction = round(marketing["monthlySpend"] * 0.50)
                new_action = {
                    "id": f"act-{random.randint(100000, 999999)}",
                    "propertyId": prop["id"],
                    "insight": f"{prop['name']} matches high stability constraints at {int(occupancy_rate * 100)}% occupancy, but marketing spend remains unthrottled at ${marketing['monthlySpend']}/mo.",
                    "recommendation": f"Scale back channel budget by 50% to ${proposed_reduction}/mo to safeguard operational margins.",
                    "proposedValue": proposed_reduction,
                    "status": "PENDING",
                    "version": 1,
                    "createdAt": datetime.utcnow().isoformat() + "Z"
                }
                actionsDB.append(new_action)
                save_actions(actionsDB)
                
    return {"success": True, "actions": actionsDB}

@app.post("/api/actions/{action_id}/execute")
def execute_action(action_id: str, payload: ActionExecutionPayload, background_tasks: BackgroundTasks):
    target_action = next((a for a in actionsDB if a["id"] == action_id), None)
    
    if not target_action:
        raise HTTPException(status_code=404, detail="Target action record not found")
        
    if target_action["status"] != "PENDING":
        create_audit_log(
            action_id,
            target_action["propertyId"],
            "SYNC_FAILED",
            f"Execution rejected: operation is already running. Status is {target_action['status']}."
        )
        raise HTTPException(status_code=400, detail="Action state must be PENDING for execution.")
    # Concurrency match check
    if target_action["version"] != payload.incomingVersion:
        create_audit_log(
            action_id,
            target_action["propertyId"],
            "SYNC_FAILED",
            f"Concurrency Collision: Client snapshot (v{payload.incomingVersion}) is out of sync with memory state (v{target_action['version']})."
        )
        raise HTTPException(status_code=409, detail="Concurrency conflict encountered.")
    # Secure the version lock
    target_action["status"] = "EXECUTING"
    target_action["version"] += 1
    save_actions(actionsDB)
    create_audit_log(
        action_id,
        target_action["propertyId"],
        "EXECUTION_STARTED",
        f"User authorized budget modification writeback. Version lock secured at v{target_action['version']}."
    )
    # Queue the simulated sync in a background task thread
    background_tasks.add_task(simulate_background_sync, action_id, target_action["propertyId"])
    # Respond with HTTP 202 (Accepted) immediately to keep the UX fast and non-blocking
    return {"success": True, "action": target_action}
@app.get("/api/audit-logs")
def get_audit_logs():
    # Reverse audit logs so newest items show on top
    return {"success": True, "logs": list(reversed(actionsAuditLogDB))}
@app.get("/api/cube-metadata")
def get_cube_metadata():
    return {"success": True, "cubes": cubeSchemaDB}
@app.post("/api/query-analytics")
def query_analytics(payload: Dict[str, Any]):
    try:
        query = payload.get("query")
        if not query or "cube" not in query or "measures" not in query:
            raise HTTPException(status_code=400, detail="Invalid semantic query structural schema.")
        results = execute_semantic_query(query)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- 5. OpenAI Agent Integration ---
@app.post("/api/copilot/chat")
async def copilot_chat(payload: ChatPayload):
    messages = payload.messages
    
    if not messages:
        raise HTTPException(status_code=400, detail="Conversation history cannot be empty.")
        
    last_message = messages[-1]
    action_id = f"chat-agent-{random.randint(10000, 99999)}"
    # Unified telemetry tracing
    def log_trace(msg: str):
        actionsAuditLogDB.append({
            "id": f"log-{int(time.time())}-{random.randint(100, 999)}",
            "actionId": action_id,
            "propertyId": "AGENT_ORCHESTRATOR",
            "eventType": "EXECUTION_STARTED",
            "message": msg,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        print(f"[AGENT TELEMETRY] {msg}")
    log_trace(f"Inbound chat query acquired: \"{last_message.content}\"")
    try:
        system_prompt = """You are a specialized occupancy analyst and conversational assistant. Your role is to answer questions about occupancy performance with precision and expert insight.
Use your analytical tools to pull live data. Always call the appropriate tool before forming your response.
## Output Formatting Rules
- Present rates as percentages (e.g., 94.2%, not 0.942)
- Present currency with a dollar sign and two decimal places (e.g. $2,800.00)
- Round unit counts to whole numbers
- Never reference tool names, cube names, field identifiers, or internal system terms in your conversation (e.g., do NOT mention 'OccupancyCube' or 'execute_semantic_query')
- Never use underscores or code-style identifiers in your responses
- Do not explain which tools you called - say "your data shows" or "the analytics indicate"
- For period-over-period comparisons: run two queries, compute the delta, and state the direction and magnitude of change clearly
- Security: never reference organization identifiers, user identifiers, or system names"""
        # Map complete chat context
        conversation = [{"role": "system", "content": system_prompt}]
        for m in messages:
            conversation.append({"role": m.role, "content": m.content})
        # OpenAI Tool schemas
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_semantic_query",
                    "description": "Queries the property data semantic layer. Use this to pull occupancy performance, marketing spend, or upcoming lease expirations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cube": {
                                "type": "string",
                                "enum": ["OccupancyCube", "MarketingSpendCube", "LeaseRiskCube"],
                                "description": "The target cube name to query"
                            },
                            "measures": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "The analytical metrics to retrieve (e.g., occupancyRate, targetRate, totalUnits, occupiedUnits, monthlySpend, monthlyRent). ALWAYS include 'targetRate' when comparing occupancy performance against target goals."
                            },
                            "dimensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "The grouping attributes to retrieve (e.g., name, propertyId, channel, unitType, expirationDate). ALWAYS include 'name' when querying OccupancyCube so that you have the human-readable property names for the user."
                            }
                        },
                        "required": ["cube", "measures"]
                    }
                }
            }
        ]
        log_trace("Step 1: Contacting OpenAI Agent Orchestrator with system and history prompts...")
        # Request initial chat generation
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation, # type: ignore
            tools=tools, # type: ignore
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        # Check for OpenAI tool dispatch
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            log_trace(f"Step 2: OpenAI dispatched Tool Call: {tool_call.function.name}")
            import json
            function_args = json.loads(tool_call.function.arguments)
            log_trace(f"[TOOL CALL] Executing semantic query: {json.dumps(function_args)}")
            # Run query
            query_results = execute_semantic_query(function_args)
            log_trace(f"Step 3: Query success. Retrieved: {json.dumps(query_results)}")
            log_trace("Step 4: Feeding data payload back to OpenAI to finalize the analysis...")
            # Run second call providing tool feedback
            conversation.append(response_message) # type: ignore
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(query_results)
            }) # type: ignore
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation # type: ignore
            )
            final_content = second_response.choices[0].message.content or ""
            log_trace("Step 5: Formatting rules applied. Dispatched finalized response back to interface.")
            return {
                "success": True,
                "message": {
                    "role": "assistant",
                    "content": final_content
                }
            }
        # Otherwise standard chat
        log_trace("Step 2: No tool call required. Yielding standard informational prompt.")
        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": response_message.content or "Standing by as your occupancy analyst."
            }
        }
    except Exception as e:
        log_trace(f"CRITICAL AGENT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)