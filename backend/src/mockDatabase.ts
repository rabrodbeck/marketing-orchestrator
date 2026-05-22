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
   { id: 'prop-101', name: 'Oakridge Luxury Apartments', totalUnits: 200, occupiedUnits: 194 },
   { id: 'prop-102', name: 'Riverfront Micro-Lofts', totalUnits: 100, occupiedUnits: 95 }
 ];

export interface MarketingSpend {
    propertyId: string;
    channel: "Google Ads" | "Meta Ads" | "ILS Listing";
    monthlySpend: number;
}

 export const marketingSpendDB: MarketingSpend[] = [
    { propertyId: "prop-101", channel: "Google Ads", monthlySpend: 5400 },
    { propertyId: "prop-102", channel: "ILS Listing", monthlySpend: 3200 }
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



