import os
import json
import random
import time
import jwt  # For signing CubeJS REST credentials
import httpx  # For dispatching secure requests to the CubeJS API
import psycopg2
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel

# Load credentials from .env
load_dotenv()

DB_HOST = os.getenv("SUPABASE_DB_HOST") 
DB_NAME = os.getenv("SUPABASE_DB_NAME")
DB_USER = os.getenv("SUPABASE_DB_USER")
DB_PASS = os.getenv("SUPABASE_DB_PASS") 
DB_PORT = os.getenv("SUPABASE_DB_PORT")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode="require"
    )

# --- 1. Core Data Interfaces ---

class Property(BaseModel):
    id: str
    name: str
    totalUnits: int
    occupiedUnits: int

class MarketingSpend(BaseModel):
    propertyId: str
    channel: str
    monthlySpend: int

class AutomatedAction(BaseModel):
    id: str
    propertyId: str
    insight: str
    recommendation: str
    proposedValue: int
    status: Literal["PENDING", "EXECUTING", "SUCCESS", "FAILED"]
    version: int
    createdAt: str

class AuditLog(BaseModel):
    id: str
    actionId: str
    propertyId: str
    eventType: Literal["EXECUTION_STARTED", "SYNC_SUCCESS", "SYNC_FAILED"]
    message: str
    timestamp: str

class LeaseExpiration(BaseModel):
    id: str
    propertyId: str
    unitType: str
    expirationDate: str
    monthlyRent: int

class OccupancyTarget(BaseModel):
    propertyId: str
    targetRate: float

# --- 2. Database Fetchers for properties and spend ---

def get_all_properties() -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, totalunits, occupiedunits FROM properties")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"id": r[0], "name": r[1], "totalUnits": r[2], "occupiedUnits": r[3]} for r in rows]
    except Exception as e:
        print("Error fetching properties from DB:", e)
        return []

def get_all_marketing_spend() -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT propertyid, channel, monthlyspend FROM marketing_spend")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"propertyId": r[0], "channel": r[1], "monthlySpend": r[2]} for r in rows]
    except Exception as e:
        print("Error fetching marketing spend from DB:", e)
        return []

# --- 3. Persistence Handlers using Supabase Cloud PostgreSQL ---

def get_actions() -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, propertyid, insight, recommendation, proposedvalue, status, version, createdat FROM automated_actions ORDER BY createdat DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{
            "id": r[0],
            "propertyId": r[1],
            "insight": r[2],
            "recommendation": r[3],
            "proposedValue": r[4],
            "status": r[5],
            "version": r[6],
            "createdAt": r[7]
        } for r in rows]
    except Exception as e:
        print("Error fetching actions from DB:", e)
        return []

def get_action_by_id(action_id: str) -> Optional[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, propertyid, insight, recommendation, proposedvalue, status, version, createdat FROM automated_actions WHERE id = %s", (action_id,))
        r = cursor.fetchone()
        cursor.close()
        conn.close()
        if not r:
            return None
        return {
            "id": r[0],
            "propertyId": r[1],
            "insight": r[2],
            "recommendation": r[3],
            "proposedValue": r[4],
            "status": r[5],
            "version": r[6],
            "createdAt": r[7]
        }
    except Exception as e:
        print(f"Error fetching action {action_id} from DB:", e)
        return None

def has_active_action(property_id: str) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM automated_actions WHERE propertyid = %s AND status IN ('PENDING', 'EXECUTING')", (property_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"Error checking active actions for {property_id} from DB:", e)
        return False

def insert_action(action: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO automated_actions (id, propertyid, insight, recommendation, proposedvalue, status, version, createdat) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (action["id"], action["propertyId"], action["insight"], action["recommendation"], action["proposedValue"], action["status"], action["version"], action["createdAt"])
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error inserting action into DB:", e)

def update_action_status_and_version(action_id: str, status: str, new_version: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE automated_actions SET status = %s, version = %s WHERE id = %s", (status, new_version, action_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error updating action {action_id} to status {status} / v{new_version}:", e)

def update_action_status(action_id: str, status: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE automated_actions SET status = %s WHERE id = %s", (status, action_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error updating action {action_id} status to {status}:", e)

def get_audit_logs() -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, actionid, propertyid, eventtype, message, timestamp FROM actions_audit_log ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{
            "id": r[0],
            "actionId": r[1],
            "propertyId": r[2],
            "eventType": r[3],
            "message": r[4],
            "timestamp": r[5]
        } for r in rows]
    except Exception as e:
        print("Error fetching audit logs from DB:", e)
        return []

def insert_audit_log(log: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO actions_audit_log (id, actionid, propertyid, eventtype, message, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (log["id"], log["actionId"], log["propertyId"], log["eventType"], log["message"], log["timestamp"])
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error inserting audit log into DB:", e)

# --- 4. Semantic Cube Definitions (Cube.js Simulation) ---

cubeSchemaDB = [
    {
        "name": "OccupancyCube",
        "description": "Contains property occupancy performance data (occupied units, total units, occupancy ratios).",
        "fields": [
            {"name": "id", "type": "dimension", "description": "Unique property identifier"},
            {"name": "name", "type": "dimension", "description": "Property Name"},
            {"name": "totalUnits", "type": "measure", "description": "Total physical units in building"},
            {"name": "occupiedUnits", "type": "measure", "description": "Number of currently leased units"},
            {"name": "occupancyRate", "type": "measure", "description": "Calculated ratio: occupiedUnits/totalUnits"},
            {"name": "targetRate", "type": "measure", "description": "The target occupancy rate for this property"}
        ]
    },
    {
        "name": "MarketingSpendCube",
        "description": "Tracks active monthly advertising channel budgets by property.",
        "fields": [
            {"name": "propertyId", "type": "dimension", "description": "Associated property identifier"},
            {"name": "channel", "type": "dimension", "description": "Advertising channel (Google Ads, Meta Ads, etc.)"},
            {"name": "monthlySpend", "type": "measure", "description": "Monthly financial investment in dollars"}
        ]
    },
    {
        "name": "LeaseRiskCube",
        "description": "Aggregates upcoming lease expirations and rent values.",
        "fields": [
            {"name": "id", "type": "dimension", "description": "Lease contract identifier"},
            {"name": "propertyId", "type": "dimension", "description": "Associated property identifier"},
            {"name": "unitType", "type": "dimension" , "description": "Unit floor plan type"},
            {"name": "expirationDate", "type": "dimension", "description": "Date of contract lease termination"},
            {"name": "monthlyRent", "type": "measure", "description": "Monthly lease rent charge"}
        ]
    }
]

# --- 5. Real CubeJS REST Integration ---

CUBEJS_API_SECRET = os.getenv("CUBEJS_API_SECRET", "super_secret_token_1234567890")

def generate_cube_token() -> str:
    # Sign a JWT payload that CubeJS expects for authentication
    payload = {
        "exp": int(time.time()) + 3600  # Token expires in 1 hour
    }
    return jwt.encode(payload, CUBEJS_API_SECRET, algorithm="HS256")

def execute_semantic_query(query: Dict[str, Any]) -> List[Dict[str, Any]]:
    # 1. Format query for official CubeJS REST specifications
    cube_name = query.get("cube")
    raw_measures = query.get("measures", [])
    raw_dimensions = query.get("dimensions", [])
    
    # Exact dimension/measure schemas to perform auto-correction for LLM type hallucinations
    cube_fields = {
        "OccupancyCube": {
            "measures": {"totalUnits", "occupiedUnits", "occupancyRate", "targetRate"},
            "dimensions": {"id", "name"}
        },
        "MarketingSpendCube": {
            "measures": {"monthlySpend"},
            "dimensions": {"propertyId", "name", "channel"}
        },
        "LeaseRiskCube": {
            "measures": {"monthlyRent"},
            "dimensions": {"id", "propertyId", "name", "unitType", "expirationDate"}
        }
    }
    
    if cube_name in cube_fields:
        schema = cube_fields[cube_name]
        # Combine all requested fields to re-sort them into their correct categories
        all_requested = set(raw_measures) | set(raw_dimensions)
        
        corrected_measures = [f for f in all_requested if f in schema["measures"]]
        corrected_dimensions = [f for f in all_requested if f in schema["dimensions"]]
        
        # Fallback to keep original arrays if auto-sorting results in empty sets
        if not corrected_measures and raw_measures:
            corrected_measures = raw_measures
        if not corrected_dimensions and raw_dimensions:
            corrected_dimensions = raw_dimensions
            
        measures = [f"{cube_name}.{m}" for m in corrected_measures]
        dimensions = [f"{cube_name}.{d}" for d in corrected_dimensions]
    else:
        measures = [f"{cube_name}.{m}" for m in raw_measures]
        dimensions = [f"{cube_name}.{d}" for d in raw_dimensions]
    
    cube_query = {
        "measures": measures,
        "dimensions": dimensions
    }

    # Format filters
    if query.get("filter"):
        f = query["filter"]
        op_map = {
            "equals": "equals",
            "greaterThan": "gt",
            "lessThan": "lt"
        }
        cube_query["filters"] = [{
            "member": f"{cube_name}.{f['field']}",
            "operator": op_map.get(f["operator"], "equals"),
            "values": [str(f["value"])]
        }]

    # 2. Fire HTTP request to local CubeJS REST port 4000
    token = generate_cube_token()
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    with httpx.Client() as client:
        response = client.post(
            "http://localhost:4000/cubejs-api/v1/load",
            json={"query": cube_query},
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"CubeJS returned error status {response.status_code}: {response.text}")
            
        data = response.json()
        
        # 3. Clean up keys from "OccupancyCube.occupancyRate" back to "occupancyRate" for LLM output compatibility!
        raw_results = data.get("data", [])
        cleaned_results = []
        
        for row in raw_results:
            cleaned_row = {}
            for k, v in row.items():
                cleaned_key = k.split(".")[-1] # strips 'OccupancyCube.' prefix
                cleaned_row[cleaned_key] = v
            cleaned_results.append(cleaned_row)
            
        return cleaned_results