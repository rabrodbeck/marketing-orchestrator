import React from "react"
import { type AutomatedAction } from "../App"

interface CardProps {
	action: AutomatedAction;
	setActions: React.Dispatch<React.SetStateAction<AutomatedAction[]>>;
}

export default function ActionCard({ action, setActions }: CardProps) {
	const commitExecution = async () => {
		// 1 - Local State Mutates Instantly (optimistic ux update)
		setActions(prev => prev.map(a => a.id === action.id ? { ...a, status: "EXECUTING" } : a));

		try {
			// Dispatch POST payload attaching current version integer context
			const res = await fetch(`http://localhost:8000/api/actions/${action.id}/execute`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json" // required to inform express parser middleware
				},
				body: JSON.stringify({ incomingVersion: action.version }) // deliver local snapshot version
			});

			const data = await res.json();

			// If the server explicitly rejected the operation (ex. concurrency collision), fail the card state locally
			if (!data.success) {
				setActions(prev => prev.map(a => a.id === action.id ? { ...a, status: "FAILED" } : a));
			}
		} catch {
			setActions(prev => prev.map(a => a.id === action.id ? { ...a, status: "FAILED" } : a));
		}
	};

	return (
		<div className="bg-slate-950 border border-slate-800 rounded-xl p-5 shadow flex flex-col gap-4">
			<div className="flex justify-between items-start">
				<p className="text-slate-300 text-sm font-medium pr-4">{action.insight}</p>
				<span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
					action.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
					action.status === 'EXECUTING' ? 'bg-blue-500/10 text-blue-400 animate-pulse' :
					'bg-emerald-500/10 text-emerald-400'
				}`}>{action.status}</span>
			</div>
			<div className="bg-slate-900 border border-slate-800/50 rounded-lg p-3 text-xs text-slate-200">
				{action.recommendation}
			</div>
			{action.status === "PENDING" && (
				<button onClick={commitExecution} className="self-end bg-white hover:bg-slate-100 text-slate-950 text-xs font-bold px-3 py-1.5 rounded transition">
					Approve & Sync Parameters
				</button>
			)}
		</div>
	);
}