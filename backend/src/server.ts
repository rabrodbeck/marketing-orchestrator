import express from "express"; // Import the Express.js framework to build the server
import cors from "cors"; // Import CORS to allow cross-origin requests from the frontend
import { propertiesDB, marketingSpendDB, actionsDB, actionsAuditLogDB, AuditLog }from "./mockDatabase"; // Import mock data for properties, marketing spend, and actions
import { saveActions } from "./mockDatabase";

// Initialize the Express application
const app = express();

// Enable CORS for all routes, allowing the frontend (running on a different port) to communicate with this backend.
app.use(cors());

function createAuditLog(actionId: string, propertyId: string, eventType: "EXECUTION_STARTED" | "SYNC_SUCCESS" | "SYNC_FAILED", message: string): void {
    const newLog: AuditLog = {
        id: `log-${Math.random().toString(36).substr(2, 9)}`,
        actionId,
        propertyId,
        eventType,
        message,
        timestamp: new Date().toISOString()
    };

    actionsAuditLogDB.push(newLog);
    console.log(`[AUDIT LEDGER] [${eventType}] - ${message}`);
}

// Enable Express to parse JSON formatted request bodies. This is crucial for POST requests.
app.use(express.json());

// --- API Endpoints ---

/**
 * GET /api/actions
 * Purpose: Fetches the current list of automated actions.
 * This endpoint provides the frontend with the latest state of pending, executing, successful, or failed actions.
 */
app.get("/api/actions", (req, res) => {
    res.status(200).json({ success: true, actions: actionsDB });
});

/**
 * POST /api/analyze
 * Purpose: Triggers a data analysis process to identify potential budget optimizations (e.g., "budget leaks").
 * This endpoint iterates through properties and applies specific business logic to determine if an action is needed.
 */
app.post("/api/analyze", (req, res) => {
    // Iterate through each property in the mock database to perform analysis.
    for (const property of propertiesDB) {
        // Edge case: Skip analysis for properties with zero total units to prevent division by zero errors.
        if (property.totalUnits === 0) {
            continue; 
        }

        // Calculate the occupancy rate for the current property.
        const occupancyRate = property.occupiedUnits / property.totalUnits;
        // Find the corresponding marketing spend data for this property.
        const marketing = marketingSpendDB.find(m => m.propertyId === property.id);
    
        // Core Logic: Determine if an automated action should be created.
        // An action is suggested if:
        // 1. Marketing data exists for the property.
        // 2. The occupancy rate is high (>= 92%).
        // 3. The monthly marketing spend is significant (>= $3000).
        if (marketing && occupancyRate >= 0.92 && marketing.monthlySpend >= 3000) {
            // Prevent duplicate actions: Only create a new action if there isn't already a PENDING action for this property.
            // Upgraded constraint: Also blocks generation if an action is currently EXECUTING or was successfully synced within the last 24 hours.
            const hasRecentAction = actionsDB.some(a => {
                const isSameProperty = a.propertyId === property.id;
                const isPendingOrExecuting = a.status === "PENDING" || a.status === "EXECUTING";
                const isRecentSuccess = a.status === "SUCCESS" && 
                    (new Date().getTime() - new Date(a.createdAt).getTime() < 24 * 60 * 60 * 1000);

                return isSameProperty && (isPendingOrExecuting || isRecentSuccess);
            });

            if (!hasRecentAction) {
                // Calculate the proposed reduction in marketing spend.
                const proposedReduction = Math.round(marketing.monthlySpend * 0.50);
                
                // Add a new automated action to the actions database.
                actionsDB.push({
                    id: `act-${Math.random().toString(36).substr(2, 9)}`, // Generate a unique ID for the action.
                    propertyId: property.id,
                    insight: `${property.name} matches high stability constraints at ${(occupancyRate * 100).toFixed(0)}% occupancy, 
                        but marketing spend remains unthrottled at $${marketing.monthlySpend}/mo.`, // Detailed insight for the user.
                    recommendation: `Scale back channel budget by 50% to $${proposedReduction}/mo to safeguard operational margins.`, // Actionable recommendation.
                    proposedValue: proposedReduction, // The numerical value for the proposed change.
                    status: "PENDING", // Initial status of the action.
                    version: 1, // Every optimization item initializes at version 1
                    createdAt: new Date().toISOString() // Timestamp for when the action was created.
                });

                // Instantly write newly detected anomalies directly to db.json
                saveActions(actionsDB);
            }
        }
    }

    // After analysis, respond with a success status and the updated list of actions.
    res.json({ success: true, actions: actionsDB });
});

/**
 * POST /api/actions/:id/execute
 * Purpose: Executes a specific automated action identified by its ID.
 * This endpoint simulates an asynchronous operation (e.g., writing back to an external system).
 */
app.post("/api/actions/:id/execute", (req, res) => {
    const { id } = req.params; // Extract the action ID from the URL parameters.
    const { incomingVersion } = req.body; // Capture the version tag submitted by the UI
    const action = actionsDB.find(a => a.id === id); // Find the action the the database

    // Safeguard 1 - Basic Existence Verification
    if (!action) {
        return res.status(404).json({ success: false, error: "Target action record not found" });
    }

    // Safeguard 2 - Core Staus Boundary Check
    if (action.status !== "PENDING") {
        createAuditLog(
            action.id,
            action.propertyId,
            "SYNC_FAILED",
            `Execution rejected: operation is already running or completed. Status is ${action.status}.`
        );
        return res.status(400).json({ success: false, error: "Action state must be PENDING for execution."});
    }

    // Safeguard 3 - Optimistic Concurrency Match Check (Blocks Race Conditions)
    if (action.version !== incomingVersion) {
        createAuditLog(
            action.id,
            action.propertyId,
            "SYNC_FAILED",
            `Concurrency Collision: Client snapshot (v${incomingVersion}) is out of sync with memory state (v${action.version}).`
        );
        return res.status(409).json({ success: false, error: "Concurrency conflict encountered. App state out of sync." });
    }

    // --- Acquire Lock Safe & Mutate Version
    // 1. Immediate State Update:
    // Change the action's status to EXECUTING immediately and increment its database version.
    // This instantly breaks paralle execution threads if a multi-click slips through.
    action.status = "EXECUTING";
    action.version += 1; // increment version instantly to secure the db lock
    saveActions(actionsDB); // Lock this change down to disk so duplicate race requests get rejected even if the server reboots

    // Log that the user approved the budget change, lock was secured, and version was updated
    createAuditLog(
        action.id,
        action.propertyId,
        "EXECUTION_STARTED",
        `User authorized budget modification writeback. Version lock secured at v${action.version}. Handshake sequence dispatched.`
    );

    // 2. Simulate Asynchronous Work
    // Use setTimeout to mimic a long-running, decoupled background process.
    setTimeout(() => {
        action.status = "SUCCESS";

        saveActions(actionsDB); // Save the successful completion status down to disk

        // Log that our third-party network finished syncing parameters safely
        createAuditLog(
            action.id,
            action.propertyId,
            "SYNC_SUCCESS",
            `Successfully synced optimized budget parameters for ${action.id}. External API returned status 200 OK.`
        );
    }, 3000); // the simulated background task takes 3 seconds

    // 3. Fast Response for Non-Blocking UI:
    // Send a "202 Accepted" response immediately. This allows the frontend to remain responsive.
    res.status(202).json({ success: true, action });

});

// Endpoint to fetch the entire audit logging history trail
app.get("/api/audit-logs", (req, res) => {
    // Hand back the global array data wrapped cleanly in a success object
    res.json({ success: true, logs: actionsAuditLogDB });
});

/**
 * Server Startup
 * The Express app starts listening for incoming requests on port 4000.
 */
app.listen(4000, () => console.log("Backend engine listening on port 4000"));
