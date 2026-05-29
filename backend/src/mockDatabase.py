import os
import json
import random
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field

# Persistence file location (same as node db)
DB_FILE = os.path.join(os.getcwd(), "db.json")

# 1. Core Data Interfaces
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
    recommendation: str
    proposedValue: int
    status: Literal["PENDING", "EXECUTING", "SUCCESS", "FAILED"]
    version: int
    createdAt: str

class AuditLog(BaseModel):
    id: str
    actionId: str
    propertId: str
    eventType: Literal["EXECUTION_STARTING", "SYNC_SUCCESS", "SYNC_FAILED"]
    messsage: str
    timestamp: str

class LeaseExpiration(BaseModel):
    id: str
    propertyId: str
    unitType: str
    expirationDate: str
    monthlyRent: int

class OccupancyTarget(BaseModel):
    propertyId: int
    targetRate: float

# 2. In-Memory Datasets
propertiesDb: List[Dict[str, Any]] = [
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

# 3. Persistence Handlers
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

# 4. Semantic Cube Definitions (Cube.js Simulation)
cubeSchemaDB = [
    {
        "name": "OccupancyCube",
        "description": "Contains property occupancy performance data (occupied units, total units, occupancy ratios).",
        "fields": [
            {"name": "id", "type": "dimension", "description": "Unique property identifier"},
            {"name": "name", "type": "dimension", "description": "Property Name"},
            {"name": "totalUnits", "type": "measure", "description": "Total physical units in building"},
            {"name": "occupiedUnits", "type": "measure", "description": "Number of currently leased units"},
            {"name": "occupancyRate", "type": "measure", "description": "Calculated ratio: occupiedUnits/totalUnits"}
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

# 5 Semantic Query Processor
class QueryFilter(BaseModel):
    field: str
    operator: Literal["equals", "greaterThan", "lessThan"]
    value: Any

class CubeQueryModel(BaseModel):
    cube: Literal["OccupancyCube", "MarketingSpendCube", "LeaseRiskCube"]
    measures: List[str]
    dimensions: Optional[List[str]] = None
    filter: Optional[QueryFilter] = None

def execute_semantic_query(query: Dict[str, Any]) -> List[Dict[str, Any]]:
    cube_name = query.get("cube")
    measures = query.get("measures", [])
    dimensions = query.get("dimensions", [])
    query_filter = query.get("filter")

    dataset = []

    # Map target datasets
    if cube_name == "OccupancyCube":
        dataset = [
            {
                "id": p["id"],
                "name": p["name"],
                "totalUnits": p["totalUnits"],
                "occupiedUnits": p["occupiedUnits"],
                "occupancyRates": round(p["occupiedUnits"] / p["totalUnits"], 3)
            }
            for p in propertiesDb
        ]
    elif cube_name == "MarketingSpendCube":
        dataset = marketingSpendDB
    elif cube_name == "LeaseRiskCube":
        dataset = leaseExpirationsDB

    # Apply Filter logic
    if query_filter:
        field = query.filter.get("field")
        op = query_filter.get("operator")
        val = query_filter.get("value")

        filtered_dataset = []
        for item in dataset:
            if field in item:
                if op == "equals" and item[field] == val:
                    filtered_dataset.append(item)
                elif op == "greaterThan" and item[field] > val:
                    filtered_dataset.append(item)
                elif op == "lessThan" and item[field] < val:
                    filtered_dataset.append(item)
        dataset = filtered_dataset

    # Projection selection
    selected_fields = list(measures) + list(dimensions or [])
    projected_dataset = []
    for item in dataset:
        projection = {}
        for f in selected_fields:
            if f in item:
                projection[f] = item[f]

    return projected_dataset
