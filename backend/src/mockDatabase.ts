import fs from "fs";
import path from "path";
const DB_FILE = path.resolve(process.cwd(), "db.json");

export interface Property {
    id: string;
    name: string;
    totalUnits: number;
    occupiedUnits: number;
}

export const propertiesDB: Property[] = [
   { id: 'prop-101', name: 'Oakridge Luxury Apartments', totalUnits: 200, occupiedUnits: 194 }, // 97% Occupancy (High - Budget Leak)
   { id: 'prop-102', name: 'Riverfront Micro-Lofts', totalUnits: 100, occupiedUnits: 95 },      // 95% Occupancy (High - Budget Leak)
   { id: 'prop-103', name: 'Highland Heights Townhomes', totalUnits: 150, occupiedUnits: 120 },  // 80% Occupancy (Low - Spend justified)
   { id: 'prop-104', name: 'Summit Ridge Apartments', totalUnits: 300, occupiedUnits: 291 },     // 97% Occupancy (High - Budget Leak)
   { id: 'prop-105', name: 'Bella Vista Condos', totalUnits: 80, occupiedUnits: 78 },           // 97.5% Occupancy (High, but low spend)
   { id: 'prop-106', name: 'Pinnacle Plaza Lofts', totalUnits: 250, occupiedUnits: 245 }         // 98% Occupancy (High - Budget Leak)
 ];

export interface MarketingSpend {
    propertyId: string;
    channel: "Google Ads" | "Meta Ads" | "ILS Listing";
    monthlySpend: number;
}

export const marketingSpendDB: MarketingSpend[] = [
    { propertyId: "prop-101", channel: "Google Ads", monthlySpend: 5400 },
    { propertyId: "prop-102", channel: "ILS Listing", monthlySpend: 3200 },
    { propertyId: "prop-103", channel: "Google Ads", monthlySpend: 6200 }, // High spend but low occupancy, so this is valid spend!
    { propertyId: "prop-104", channel: "Google Ads", monthlySpend: 6000 }, // High occupancy & high spend = Budget Leak!
    { propertyId: "prop-105", channel: "Meta Ads", monthlySpend: 1200 },   // High occupancy but low spend = No Leak.
    { propertyId: "prop-106", channel: "Meta Ads", monthlySpend: 4500 }    // High occupancy & high spend = Budget Leak!
 ];

export interface AutomatedAction {
    id: string;
    propertyId: string;
    insight: string;
    recommendation: string;
    proposedValue: number;
    status: "PENDING" | "EXECUTING" | "SUCCESS" | "FAILED";
    version: number;
    createdAt: string;
}

export let actionsDB: AutomatedAction[] = loadActions();

// Helper to load actions safely off disk on engine startup
export function loadActions(): AutomatedAction[] {
    try {
        if (fs.existsSync(DB_FILE)) {
            const fileData = fs.readFileSync(DB_FILE, "utf-8");
            return JSON.parse(fileData);
        }
    } catch (error) {
        console.error("Failed to read persistence file. Initializing empty collection.", error);
    }
    return [];
}

// Helper to flush mutations straight down to disk
export function saveActions(actions: AutomatedAction[]): void {
    try {
        fs.writeFileSync(DB_FILE, JSON.stringify(actions, null, 2), "utf-8");
    } catch (error) {
        console.error("Critical I/O error writing to file storage layer.", error);
    }
}

export interface AuditLog {
    id: string;
    actionId: string;
    propertyId: string;
    eventType: "EXECUTION_STARTED" | "SYNC_SUCCESS" | "SYNC_FAILED";
    message:string;
    timestamp: string;
}

export const actionsAuditLogDB: AuditLog[] = [];

export interface LeaseExpiration {
    id: string;
    propertyId: string;
    unitType: string;
    expirationDate: string;
    monthlyRent: number;
}

export const leaseExpirationsDB: LeaseExpiration[] = [
    // Oakridge Expirations
    { id: "lease-1", propertyId: "prop-101", unitType: "2BR Luxury", expirationDate: "2026-06-15", monthlyRent: 2800 },
    { id: "lease-2", propertyId: "prop-101", unitType: "1BR Classic", expirationDate: "2026-07-01", monthlyRent: 2100 },
    
    // Riverfront Expirations
    { id: "lease-3", propertyId: "prop-102", unitType: "Studio Loft", expirationDate: "2026-06-30", monthlyRent: 1800 },
    
    // Highland Heights (Low occupancy - high upcoming lease roll off risk!)
    { id: "lease-4", propertyId: "prop-103", unitType: "3BR Townhome", expirationDate: "2026-06-10", monthlyRent: 3200 },
    { id: "lease-5", propertyId: "prop-103", unitType: "2BR Townhome", expirationDate: "2026-07-15", monthlyRent: 2600 },
    
    // Summit Ridge Expirations
    { id: "lease-6", propertyId: "prop-104", unitType: "1BR Standard", expirationDate: "2026-06-25", monthlyRent: 1950 },
    { id: "lease-7", propertyId: "prop-104", unitType: "2BR Deluxe", expirationDate: "2026-08-01", monthlyRent: 2500 },
    // Pinnacle Plaza Expirations
    { id: "lease-8", propertyId: "prop-106", unitType: "Penthouse", expirationDate: "2026-06-20", monthlyRent: 4800 }
];

export interface OccupancyTarget {
    propertyId: string;
    targetRate: number;     // example: 0.95
}

export const occupancyTargetDB: OccupancyTarget[] = [
    { propertyId: "prop-101", targetRate: 0.95 },
    { propertyId: "prop-102", targetRate: 0.90 },
    { propertyId: "prop-103", targetRate: 0.92 }, // Low occupancy property is failing its target
    { propertyId: "prop-104", targetRate: 0.95 },
    { propertyId: "prop-105", targetRate: 0.94 },
    { propertyId: "prop-106", targetRate: 0.95 }
];

// Semantic Cube Metadata Definitions (Cube.js simulation)
export interface CubeField {
    name: string;
    type: "measure" | "dimension";
    description: string;
}

export interface CubeSchema {
    name: string;
    description: string;
    fields: CubeField[];
}

export const cubeSchemaDB: CubeSchema[] = [
    {
        name: "OccupancyCube",
        description: "Contains property occupancy performance data (occupied units, total units, occupancy ratios).",
        fields: [
            { name: "id", type: "dimension", description: "Unique property identifier" },
            { name: "name", type: "dimension", description: "Property Name" },
            { name: "totalUnits", type: "measure", description: "Total physical units in building" },
            { name: "occupiedUnits", type: "measure", description: "Number of currently leased units" },
            { name: "occupancyRate", type: "measure", description: "Calculated ratio: occupiedUnits/totalUnits" }
        ]
    },
    {
        name: "MarketingSpendCube",
        description: "Tracks active monthly advertising channel budgets by property.",
        fields: [
            { name: "propertyId", type: "dimension", description: "Associated property identifier" },
            { name: "channel", type: "dimension", description: "Advertising channel (Google Ads, Meta Ads, etc.)" },
            { name: "monthlySpend", type: "measure", description: "Monthly financial investment in dollars" }
        ]
    },
    {
        name: "LeaseRiskCube",
        description: "Aggregates upcoming lease expirations and rent values.",
        fields: [
            { name: "id", type: "dimension", description: "Lease contract identifier" },
            { name: "propertyId", type: "dimension", description: "Associated property identifier" },
            { name: "unitType", type: "dimension" , description: "Unit floor plan type" },
            { name: "expirationDate", type: "dimension", description: "Date of contract lease termination" },
            { name: "monthlyRent", type: "measure", description: "Monthly lease rent charge" }
        ]
    }
];

// Structured Semantic Query Processor
export interface CubeQuery {
    cube: "OccupancyCube" | "MarketingSpendCube" | "LeaseRiskCube";
    measures: string[];
    dimensions?: string[];
    filter?: {
        field: string;
        operator: "equals" | "greaterThan" | "lessThan";
        value: any;
    };
}

export function executeSemanticQuery(query: CubeQuery): any[] {
    let dataset: any[] = [];

    // Select core dataset based on cube name
    if (query.cube === "OccupancyCube") {
        dataset = propertiesDB.map(p => ({
            id: p.id,
            name: p.name,
            totalUnits: p.totalUnits,
            occupiedUnits: p.occupiedUnits,
            occupancyRate: +(p.occupiedUnits / p.totalUnits).toFixed(3)
        }));
    } else if (query.cube === "MarketingSpendCube") {
        dataset = marketingSpendDB;
    } else if (query.cube === "LeaseRiskCube") {
        dataset = leaseExpirationsDB;
    }

    // Apply filter if present
    if (query.filter) {
        const { field, operator, value } = query.filter;
        dataset = dataset.filter(item => {
            if (operator === "equals") return item[field] === value;
            if (operator === "greaterThan") return item[field] > value;
            if (operator === "lessThan") return item[field] < value;
            return true;
        });
    }

    // Project only requested dimensions and measures
    const selectedFields = [...query.measures, ...(query.dimensions || [])];
    return dataset.map(item => {
        const projection: any = {};
        selectedFields.forEach(f => {
            if (f in item) projection[f] = item[f];
        });
        return projection;
    });
}



