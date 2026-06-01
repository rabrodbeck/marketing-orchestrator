
// Define the interface contract matching our backend database payload shape
interface AuditLog {
    id: string;
    actionId: string;
    propertyId: string;
    eventType: "EXECUTION_STARTED" | "SYNC_SUCCESS" | "SYNC_FAILED";
    message: string;
    timestamp: string;
}

interface TelemetryPanelProps {
    logs: AuditLog[];
}

export default function TelemetryPanel({ logs }: TelemetryPanelProps) {
    return (
        <div className="bg-slate-950 border border-slate-800 rounded-xl mt-8 shadow-2xl overflow-hidden font-mono text-left">
            {/* Console Bar Header */}
            <div className="bg-slate-900 border-b border-slate-800 px-4 py-2.5 flex justify-between items-center">
                <div className="flex items-center space-x-2">
                    <span className="2-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping"></span>
                    <span className="text-xs font-semibold tracking-wider text-slate-200 uppercase">System Telemetry Feed Stream</span>
                </div>
                <span className="text-[10px] text-slate-500">Live Buffer Logs: {logs.length}</span>
            </div>

            {/* Code Display Monitor Terminal Window */}
            <div className="p-4 max-h-60 overflow-y-auto space-y-2 text-xs leading-relaxed">
                {logs.length === 0 ? (
                    <p className="text-slate-600 italic">Ledger standing by. Awaiting system execution triggers...</p>
                ) : ( 
                    logs.map((log) => {
                        // Apply unique styles depending on the type oflog transition ecnountered
                        const colorMap = {
                            EXECUTION_STARTED: 'text-amber-400',
                            SYNC_SUCCESS: 'text-emerald-400',
                            SYNC_FAILED: 'text-rose-400'
                        };

                        return (
                            <div key={log.id} className="border-b border-slate-900/40 pb-1.5 flex items-start space-x-2">
                                <span className="text-slate-500 text-[10px] select-none">
                                    [{new Date(log.timestamp).toLocaleTimeString()}]
                                </span>
                                                                <span className={`font-bold ${colorMap[log.eventType]} text-[10px] tracking-wide uppercase min-w-32.5 inline-block`}>
                                    {log.eventType}
                                </span>
                                <span className="text-slate-300 flex-1">{log.message}</span>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}