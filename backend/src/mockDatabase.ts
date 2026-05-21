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
    createdAt: string;
}

export const actionsDB: AutomatedAction[] = [];

export interface AuditLog {
    id: string;
    actionId: string;
    propertyId: string;
    eventType: "EXECUTION_STARTED" | "SYNC_SUCCESS" | "SYNC_FAILED";
    message:string;
    timestamp: string;
}

export const actionsAuditLogDB: AuditLog[] = [];



