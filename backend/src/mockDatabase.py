import os
import json
import random
import time
import jwt  # For signing CubeJS REST credentials
import httpx  # For dispatching secure requests to the CubeJS API
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field

# Persistence file location (same as node db)
DB_FILE = os.path.join(os.getcwd(), "db.json")

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

# --- 2. In-Memory Datasets (Kept for FastAPI Diagnostics Card operations) ---

propertiesDB: List[Dict[str, Any]] = [
    {"id": "prop-101", "name": "Oakridge Luxury Apartments", "totalUnits": 200, "occupiedUnits": 194},
    {"id": "prop-102", "name": "Riverfront Micro-Lofts", "totalUnits": 100, "occupiedUnits": 95},
    {"id": "prop-103", "name": "Highland Heights Townhomes", "totalUnits": 150, "occupiedUnits": 120},
    {"id": "prop-104", "name": "Summit Ridge Apartments", "totalUnits": 300, "occupiedUnits": 291},
    {"id": "prop-105", "name": "Bella Vista Condos", "totalUnits": 80, "occupiedUnits": 78},
    {"id": "prop-106", "name": "Pinnacle Plaza Lofts", "totalUnits": 250, "occupiedUnits": 245}
]

marketingSpendDB: List[Dict[str, Any]] = [
    {"propertyId": "prop-101", "channel": "Google Ads", "monthlySpend": 5400},
    {"propertyId": "prop-102", "channel": "ILS Listing", "monthlySpend": 3200},
    {"propertyId": "prop-103", "channel": "Google Ads", "monthlySpend": 6200},
    {"propertyId": "prop-104", "channel": "Google Ads", "monthlySpend": 6000},
    {"propertyId": "prop-105", "channel": "Meta Ads", "monthlySpend": 1200},
    {"propertyId": "prop-106", "channel": "Meta Ads", "monthlySpend": 4500}
]

leaseExpirationsDB: List[Dict[str, Any]] = [
    {"id": "lease-1", "propertyId": "prop-101", "unitType": "2BR Luxury", "expirationDate": "2026-06-15", "monthlyRent": 2800},
    {"id": "lease-2", "propertyId": "prop-101", "unitType": "1BR Classic", "expirationDate": "2026-07-01", "monthlyRent": 2100},
    {"id": "lease-3", "propertyId": "prop-102", "unitType": "Studio Loft", "expirationDate": "2026-06-30", "monthlyRent": 1800},
    {"id": "lease-4", "propertyId": "prop-103", "unitType": "3BR Townhome", "expirationDate": "2026-06-10", "monthlyRent": 3200},
    {"id": "lease-5", "propertyId": "prop-103", "unitType": "2BR Townhome", "expirationDate": "2026-07-15", "monthlyRent": 2600},
    {"id": "lease-6", "propertyId": "prop-104", "unitType": "1BR Standard", "expirationDate": "2026-06-25", "monthlyRent": 1950},
    {"id": "lease-7", "propertyId": "prop-104", "unitType": "2BR Deluxe", "expirationDate": "2026-08-01", "monthlyRent": 2500},
    {"id": "lease-8", "propertyId": "prop-106", "unitType": "2BR Penthouse", "expirationDate": "2026-06-20", "monthlyRent": 4800}
]

occupancyTargetsDB: List[Dict[str, Any]] = [
    {"propertyId": "prop-101", "targetRate": 0.95},
    {"propertyId": "prop-102", "targetRate": 0.90},
    {"propertyId": "prop-103", "targetRate": 0.92},
    {"propertyId": "prop-104", "targetRate": 0.95},
    {"propertyId": "prop-105", "targetRate": 0.94},
    {"propertyId": "prop-106", "targetRate": 0.95}
]

actionsAuditLogDB: List[Dict[str, Any]] = []

# --- 3. Persistence Handlers ---

def load_actions() -> List[Dict[str, Any]]:
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("Failed to read persistence file. Initializing empty collection.", e)
    return []

def save_actions(actions: List[Dict[str, Any]]):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(actions, f, indent=2)
    except Exception as e:
        print("Critical I/O error writing to file storage layer.", e)

actionsDB: List[Dict[str, Any]] = load_actions()

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
    # CubeJS maps names like OccupancyCube.name, OccupancyCube.occupancyRate
    cube_name = query.get("cube")
    measures = [f"{cube_name}.{m}" for m in query.get("measures", [])]
    dimensions = [f"{cube_name}.{d}" for d in query.get("dimensions", [])]
    
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
        # Calls the load endpoint on Docker container running on port 4000
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