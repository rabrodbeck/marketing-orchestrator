import React, { useState, useEffect } from "react"; // Import React core, and the useState/useEffect hooks for managing component state and side effects.
import ActionCard from "./components/ActionCard"; // Import the ActionCard component to display individual automated actions.
import TelemetryPanel from "./components/TelemetryPanel";
import ChatCopilot from "./components/ChatCopilot";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Defines the structure for an AutomatedAction object.
 * This interface ensures type safety for action data across the application.
 */
export interface AutomatedAction {
  id: string; // A unique identifier for the action.
  insight: string; // A descriptive text explaining why the action was generated.
  recommendation: string; // The suggested action to be taken.
  status: "PENDING" | "EXECUTING" | "SUCCESS" | "FAILED"; // The current status of the action.
  version: number;
}

/**
 * The main application component.
 * This component manages the overall state, triggers the analysis pipeline, and displays automated actions.
 */
export default function App() {
  // --- React State Management ---

  // `actions` state variable holds an array of AutomatedAction objects.
  // `setActions` is the function used to update this state.
  const [actions, setActions] = useState<AutomatedAction[]>([]);
  
  // `running` state variable tracks whether the system diagnostics pipeline is currently executing.
  // This is used to disable the button and show loading feedback.
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = React.useState<any[]>([]);

  // `globalError` state variable handles error string capture for structural UI fallback rendering.
  const [globalError, setGlobalError] = useState<string | null>(null);

  const [copilotOpen, setCopilotOpen] = useState(false);

  /**
   * --- Core Logic: Triggering the Analysis Pipeline ---
   * This asynchronous function is called when the "Execute System Diagnostics" button is clicked.
   * It makes a POST request to the backend's /api/analyze endpoint to initiate the data analysis.
   */
  const triggerPipeline = async () => {
    setRunning(true); // Set running to true to disable the button and show loading text.
    setGlobalError(null); // Clear out any previous pipeline connection error states.

    try {
      // Make a POST request to the backend to trigger the analysis.
      const res = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: "POST" // Specify the HTTP method as POST.
      });

      if (!res.ok) {
        throw new Error(`Server responded with an unexpected status code: ${res.status}`);
      }

      const data = await res.json(); // Parse the JSON response from the backend.

      // If the analysis was successful, update the `actions` state with the new list of actions.
      if (data.success) setActions(data.actions);
    } catch (err) {
      console.error("Pipeline triggering failure", err);
      // Populate the UI alert state variable with a clean notification string.
      setGlobalError("Failed to synchronize with the diagnostics engine. Please check if your local backend server is running.");
    } finally {
      setRunning(false); // Set running back to false to re-enable the button.
    }
  };

  const fetchTelemetryLogs = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/audit-logs`);
      const data = await res.json();
      if (data.success) {
        // Reverse the array records so that the newest logs are always pinned at the top
        setLogs(data.logs.reverse());
      }
    } catch (err) {
      console.error("Telemetry data frame connection broken.", err);
    }
  };

  useEffect(() => {
    const hydrateDashboardOnBoot = async () => {
      try {
        // Fetch any existing actions from db.json
        const actionRes = await fetch(`${API_BASE_URL}/api/actions`);
        const actionsData = await actionRes.json();
        if (actionsData.success) setActions(actionsData.actions);

        // Fetch the historical log timeline
        await fetchTelemetryLogs();
      } catch (err) {
        console.error("Failed to hydrate dashboard on boot:", err);
      }
    }

    hydrateDashboardOnBoot();
  }, []); // empty dependency array => run one on initial page mount

  /**
   * React Lifecycle: Polls if there is an executing card OR if the copilot drawer is active
   * to ensure we pull both sync logs and chat agent reasoning logs in real-time.
   */
  useEffect(() => {
    if (actions.some(a => a.status === 'EXECUTING') || copilotOpen) {
      fetchTelemetryLogs();
      const interval = window.setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/actions`);
          const data = await res.json();
          if (data.success) setActions(data.actions);
        } catch (e) {
          console.error(e);
        }
        fetchTelemetryLogs();
      }, 1500);
      return () => clearInterval(interval);
    }
  }, [actions, copilotOpen]); // Added copilotOpen to trigger polling when chat starts

  // --- Component Rendering ---
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      {/* Header Section */}
      <div className="max-w-4xl mx-auto flex justify-between items-center border-b border-slate-800 pb-6 mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Marketing Orchestrator Engine</h1>
          <p className="text-xs text-slate-400 mt-0.5">Asynchronous Data Orchestration Proof of Concept</p>
        </div>
                  {/* Buttons to trigger the new Copilot and the analysis pipeline */}
         <div className="flex space-x-3">
           <button 
             onClick={() => setCopilotOpen(true)}
             className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-4 py-2 rounded-md shadow border border-slate-700"
           >
             💬 Launch AI Copilot
           </button>
           <button 
             onClick={triggerPipeline} 
             disabled={running} 
             className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 font-medium text-xs px-4 py-2 rounded-md shadow"
           >
             {running ? 'Ingesting Feeds...' : 'Execute System Diagnostics'}
           </button>
         </div>
      </div>

      {/* Global Application Systemic Alert Error Banner Block */}
      {globalError && (
        <div className="max-w-4xl mx-auto mb-6 bg-rose-500/10 border border-rose-500/20 rounded-xl p-4 flex justify-between items-center text-rose-400 text-sm animate-fade-in">
          <div className="flex items-center space-x-3">
            <span className="text-base">⚠️</span>
            <p className="font-medium">{globalError}</p>
          </div>
          <button 
            onClick={() => setGlobalError(null)}
            className="text-rose-400/50 hover:text-rose-400 font-semibold px-2 py-1 text-xs uppercase tracking-wider transition-colors"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Action Cards Display Section */}
      <div className="max-w-4xl mx-auto space-y-4">
          {/* Map through the `actions` array and render an `ActionCard` for each action. */}
        {actions.length === 0 && !running && (
          <div className="border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500 text-sm font-medium">
            No optimization entries generated. Execute diagnostics above to parse PMS systems.
          </div>
        )}
        {actions.map(a => (
              // `key` prop is important for React to efficiently update lists.
              // `action` prop passes the individual action data to the ActionCard.
              // `setActions` prop allows ActionCard to update the global actions state.
          <ActionCard key={a.id} action={a} setActions={setActions} />
        ))}
      </div>

      {/* Mount log tracking element */}
      <footer className="max-w-4xl mx-auto mt-8 pb-12">
        <TelemetryPanel logs={logs} />
      </footer>
      <ChatCopilot isOpen={copilotOpen} onClose={() => setCopilotOpen(false)} />
    </div>
  );
}