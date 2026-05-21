import React, { useState, useEffect } from "react"; // Import React core, and the useState/useEffect hooks for managing component state and side effects.
import ActionCard from "./components/ActionCard"; // Import the ActionCard component to display individual automated actions.
import TelemetryPanel from "./components/TelemetryPanel";

/**
 * Defines the structure for an AutomatedAction object.
 * This interface ensures type safety for action data across the application.
 */
export interface AutomatedAction {
  id: string; // A unique identifier for the action.
  insight: string; // A descriptive text explaining why the action was generated.
  recommendation: string; // The suggested action to be taken.
  status: "PENDING" | "EXECUTING" | "SUCCESS" | "FAILED"; // The current status of the action.
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

  /**
   * --- Core Logic: Triggering the Analysis Pipeline ---
   * This asynchronous function is called when the "Execute System Diagnostics" button is clicked.
   * It makes a POST request to the backend's /api/analyze endpoint to initiate the data analysis.
   */
  const triggerPipeline = async () => {
    setRunning(true); // Set running to true to disable the button and show loading text.

    // Make a POST request to the backend to trigger the analysis.
    const res = await fetch("http://localhost:4000/api/analyze", {
      method: "POST" // Specify the HTTP method as POST.
    });
    const data = await res.json(); // Parse the JSON response from the backend.

    // If the analysis was successful, update the `actions` state with the new list of actions.
    if (data.success) setActions(data.actions);
    
    setRunning(false); // Set running back to false to re-enable the button.
  };

  const fetchTelemetryLogs = async () => {
    try {
      const res = await fetch("http://localhost:4000/api/audit-logs");
      const data = await res.json();
      if (data.success) {
        // Reverse the array records so that the newest logs are always pinned at the top
        setLogs(data.logs.reverse());
      }
    } catch (err) {
      console.error("Telemetry data frame connection broken.", err);
    }
  };

  /**
   * --- React Lifecycle: Polling for Asynchronous Updates ---
   * This `useEffect` hook sets up a polling mechanism to regularly fetch updated action statuses from the backend.
   * It's crucial for reflecting asynchronous updates (like an action changing from "EXECUTING" to "SUCCESS").
   */
  useEffect(() => {
    // Condition for polling: Only poll if there is at least one action with "EXECUTING" status.
    // This optimizes by not polling unnecessarily.
    if (actions.some(a => a.status === 'EXECUTING')) {
      // Fire an immediate capture hook to seize the inital starting log event
      fetchTelemetryLogs();

      const interval = window.setInterval(async () => {
        // Worker Task A: Query updated status properties for state cards
        try {
          // Make a GET request to the backend's /api/actions endpoint to get the latest actions.
          const res = await fetch('http://localhost:4000/api/actions');
          const data = await res.json(); // Parse the JSON response.
          
          // If successful, update the `actions` state with the freshest data from the backend.
          if (data.success) setActions(data.actions);
        } catch (e) {
          // Log any errors that occur during the fetch operation.
          console.error(e);
        }

        // Worker Task B: Ingest the latest systemic audit logs from backend memory
        fetchTelemetryLogs();
      }, 1500); // Polling interval.

      // Cleanup function: This is vital to prevent memory leaks.
      // When the component unmounts or the `actions` dependency changes (and polling is no longer needed),
      // this function clears the interval, stopping the polling.
      return () => clearInterval(interval);
    }
  }, [actions]); // Dependency array: This effect re-runs whenever the `actions` state changes.

  // --- Component Rendering ---
  return (
 	<div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
    {/* Header Section */}
   	<div className="max-w-4xl mx-auto flex justify-between items-center border-b border-slate-800 pb-6 mb-8">
     	<div>
       	<h1 className="text-2xl font-bold tracking-tight text-white">Marketing Orchestrator Engine</h1>
       	<p className="text-xs text-slate-400 mt-0.5">Asynchronous Data Orchestration Proof of Concept</p>
     	</div>
       {/* Button to trigger the analysis pipeline */}
     	<button 
          onClick={triggerPipeline} // Calls `triggerPipeline` when clicked.
          disabled={running} // Button is disabled if `running` state is true (pipeline is active).
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 font-medium text-xs px-4 py-2 rounded-md shadow"
        >
       	{running ? 'Ingesting Feeds...' : 'Execute System Diagnostics'} {/* Dynamic button text based on `running` state. */}
     	</button>
   	</div>

    {/* Action Cards Display Section */}
   	<div className="max-w-4xl mx-auto space-y-4">
        {/* Map through the `actions` array and render an `ActionCard` for each action. */}
     	{actions.map(a => (
            // `key` prop is important for React to efficiently update lists.
            // `action` prop passes the individual action data to the ActionCard.
            // `setActions` prop allows ActionCard to update the global actions state.
       	<ActionCard key={a.id} action={a} setActions={setActions} />
     	))}
   	</div>

    {/* Mount log tracking element */}
    <footer className="max-w-5xl mx-auto pb-12">
      <TelemetryPanel logs={logs} />
    </footer>
 	</div>
   );
 }
