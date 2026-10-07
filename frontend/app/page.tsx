"use client";

import { FormEvent, useMemo, useState } from "react";

type WorkflowResult = {
  workflow_id?: string;
  workflow_status?: string;
  intent?: string;
  confidence?: number;
  validation_result?: {
    status?: string;
    requires_human_review?: boolean;
    reasons?: string[];
  };
  ml_prediction?: {
    predicted_class?: string;
    probability?: number;
    probability_band?: string;
    reason_codes?: string[];
  };
  investigation_result?: {
    policy_reference?: string[];
    recommended_action?: string;
  };
  retrieved_data?: {
    policy_documents?: Array<{ citation?: string; title?: string; excerpt?: string }>;
  };
  final_response?: string;
};

const stages = ["Triage", "Data Retrieval", "ML Classification", "Policy RAG", "Investigation", "Validation", "Approval", "Response"];
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  const [query, setQuery] = useState("Customer CUS-016 reported a damaged electronics item. Order ORD-889 was delivered 3 days late and the product was received in damaged condition. Please classify and review the return.");
  const [workflow, setWorkflow] = useState<WorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [approvalMessage, setApprovalMessage] = useState("");

  const stageIndex = useMemo(() => {
    if (!workflow) return 0;
    if (workflow.workflow_status === "PENDING_HUMAN_REVIEW") return 6;
    if (workflow.workflow_status === "RESOLVED") return 7;
    return 5;
  }, [workflow]);

  async function runWorkflow(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setApprovalMessage("");
    try {
      const response = await fetch(`${API_URL}/api/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_message: query, session_id: "dashboard-session" }),
      });
      if (!response.ok) throw new Error((await response.json()).detail || "Workflow request failed");
      const data = (await response.json()) as { workflow: WorkflowResult };
      setWorkflow(data.workflow);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to run workflow");
    } finally {
      setLoading(false);
    }
  }

  async function submitApproval(action: "approve" | "reject") {
    if (!workflow?.workflow_id) return;
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/approval/${workflow.workflow_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, notes: "Reviewed by the assigned return operations reviewer." }),
      });
      if (!response.ok) throw new Error((await response.json()).detail || "Approval request failed");
      const data = (await response.json()) as { status: string; final_response?: string };
      setWorkflow((current) => current ? { ...current, workflow_status: data.status, final_response: data.final_response } : current);
      setApprovalMessage(`${action === "approve" ? "Approved" : "Rejected"} and workflow resolved.`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to submit approval");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 p-5 text-slate-900 md:p-10">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="rounded-2xl border border-violet-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-600">Retail operations</p>
              <h1 className="mt-2 text-3xl font-bold">Return Eligibility Exception Agent</h1>
              <p className="mt-2 text-sm text-slate-500">Explainable classification with policy-grounded evidence and human approval.</p>
            </div>
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">Backend: {API_URL}</span>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Return investigation</h2>
            <form onSubmit={runWorkflow} className="mt-5 space-y-4">
              <label className="block text-sm font-medium text-slate-600" htmlFor="query">Return request</label>
              <textarea id="query" value={query} onChange={(event) => setQuery(event.target.value)} className="min-h-32 w-full rounded-xl border border-slate-200 bg-slate-50 p-4 outline-none transition focus:border-violet-500 focus:ring-4 focus:ring-violet-100" required />
              <button disabled={loading || !query.trim()} className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50">
                {loading ? "Running workflow…" : "Run investigation"}
              </button>
            </form>
            {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

            {workflow && (
              <div className="mt-6 space-y-4">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Prediction</p><p className="mt-2 font-semibold">{workflow.ml_prediction?.predicted_class || "—"}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Probability</p><p className="mt-2 font-semibold">{workflow.ml_prediction?.probability === undefined ? "—" : `${Math.round(workflow.ml_prediction.probability * 100)}%`}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Status</p><p className="mt-2 font-semibold">{workflow.workflow_status}</p></div>
                </div>
                <div className="rounded-xl border border-slate-200 p-4">
                  <h3 className="font-semibold">Reason codes</h3>
                  <div className="mt-3 flex flex-wrap gap-2">{(workflow.ml_prediction?.reason_codes || []).map((code) => <span key={code} className="rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">{code}</span>)}</div>
                </div>
                {workflow.validation_result && <div className="rounded-xl border border-slate-200 p-4"><h3 className="font-semibold">Validation</h3><ul className="mt-3 space-y-2 text-sm text-slate-600">{workflow.validation_result.reasons?.map((reason) => <li key={reason}>• {reason}</li>)}</ul></div>}
                {workflow.workflow_status === "PENDING_HUMAN_REVIEW" && (
                  <div className="rounded-xl border border-amber-300 bg-amber-50 p-4">
                    <h3 className="font-semibold text-amber-800">Human review required</h3>
                    <p className="mt-2 text-sm text-amber-700">No consequential action has been executed. Review the evidence before resolving the case.</p>
                    <div className="mt-4 flex flex-wrap gap-3"><button onClick={() => submitApproval("approve")} disabled={loading} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white">Approve</button><button onClick={() => submitApproval("reject")} disabled={loading} className="rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-semibold text-red-700">Reject</button></div>
                  </div>
                )}
                {approvalMessage && <p className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">{approvalMessage}</p>}
              </div>
            )}
          </section>

          <aside className="space-y-6">
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Workflow status</h2>
              <div className="mt-5 space-y-3">{stages.map((stage, index) => { const complete = index < stageIndex; const active = index === stageIndex; return <div key={stage} className={`flex items-center gap-3 rounded-lg border p-3 ${complete ? "border-emerald-200 bg-emerald-50 text-emerald-700" : active ? "border-violet-300 bg-violet-50 text-violet-700" : "border-slate-200 bg-slate-50 text-slate-500"}`}><span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${complete ? "bg-emerald-600 text-white" : active ? "bg-violet-600 text-white" : "bg-slate-200 text-slate-600"}`}>{complete ? "✓" : index + 1}</span><span>{stage}</span></div>; })}</div>
            </section>
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Policy citations</h2>
              <div className="mt-4 space-y-3">{(workflow?.retrieved_data?.policy_documents || []).map((document) => <div key={`${document.citation}-${document.title}`} className="rounded-xl bg-slate-50 p-4"><p className="font-medium">{document.citation || document.title}</p><p className="mt-2 text-xs text-slate-500">{document.title}</p><p className="mt-2 text-sm leading-6 text-slate-600">{document.excerpt}</p></div>)}{!workflow?.retrieved_data?.policy_documents?.length && <p className="text-sm text-slate-500">Run the workflow to retrieve policy evidence.</p>}</div>
            </section>
            {workflow?.final_response && <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold">Final response</h2><pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-200">{workflow.final_response}</pre></section>}
          </aside>
        </div>
      </div>
    </main>
  );
}
