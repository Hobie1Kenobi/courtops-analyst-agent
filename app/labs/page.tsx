"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface Exercise {
  id: string;
  title: string;
  instruction: string;
  expected_answer: string;
  explanation: string;
  oracle_equivalent?: string;
  tip?: string;
}

interface Lab {
  id: string;
  name: string;
  domain: string;
  description: string;
  exercises: Exercise[];
}

interface LabSummary {
  id: string;
  name: string;
  domain: string;
  description: string;
  exercise_count: number;
}

const DOMAIN_COLORS: Record<string, string> = {
  sql_server: "border-green-400 bg-green-50",
  crystal_reports: "border-blue-400 bg-blue-50",
  web_services: "border-orange-400 bg-orange-50",
  debugging: "border-red-400 bg-red-50",
  requirements: "border-violet-400 bg-violet-50",
};

const DOMAIN_ICONS: Record<string, string> = {
  sql_server: "💾",
  crystal_reports: "📊",
  web_services: "🔗",
  debugging: "🔍",
  requirements: "📋",
};

export default function LabsPage() {
  const [labList, setLabList] = useState<Record<string, LabSummary>>({});
  const [activeLab, setActiveLab] = useState<Lab | null>(null);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [showAnswer, setShowAnswer] = useState(false);
  const [feedback, setFeedback] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/training/labs`).then((r) => r.json()).then(setLabList).catch(() => {});
  }, []);

  const loadLab = async (labId: string) => {
    const res = await fetch(`${API}/training/labs/${labId}`);
    const data = await res.json();
    setActiveLab(data);
    setActiveExercise(data.exercises[0] || null);
    setShowAnswer(false);
    setFeedback(null);
    setUserAnswer("");
  };

  const handleSubmit = async () => {
    if (!activeLab || !activeExercise) return;
    const res = await fetch(`${API}/training/labs/${activeLab.id}/submit?exercise_id=${activeExercise.id}&answer=${encodeURIComponent(userAnswer)}`, { method: "POST" });
    const data = await res.json();
    setFeedback(data);
    setShowAnswer(true);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-lg border-2 border-teal-300 bg-teal-50 px-4 py-3">
        <h2 className="text-lg font-bold text-teal-900">Hands-On Training Labs</h2>
        <p className="text-xs text-teal-700">Practice enterprise analyst skills: SQL, reporting, integrations, debugging, requirements</p>
      </div>

      {!activeLab ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Object.entries(labList).map(([key, lab]) => (
            <button key={key} onClick={() => loadLab(key)} className={`rounded-lg border-2 p-4 text-left transition-all hover:shadow-md ${DOMAIN_COLORS[lab.domain] || "border-slate-300 bg-slate-50"}`}>
              <div className="text-2xl mb-2">{DOMAIN_ICONS[lab.domain] || "📁"}</div>
              <h3 className="text-sm font-bold">{lab.name}</h3>
              <p className="text-xs text-slate-600 mt-1">{lab.description}</p>
              <div className="mt-2 text-[10px] font-semibold text-slate-500">{lab.exercise_count} exercise{lab.exercise_count !== 1 ? "s" : ""}</div>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <button onClick={() => { setActiveLab(null); setActiveExercise(null); setShowAnswer(false); setFeedback(null); }} className="rounded bg-slate-200 px-2 py-1 text-xs hover:bg-slate-300">← All Labs</button>
            <h3 className="text-sm font-bold">{activeLab.name}</h3>
          </div>

          {/* Exercise selector */}
          <div className="flex gap-1 flex-wrap">
            {activeLab.exercises.map((ex, i) => (
              <button key={ex.id} onClick={() => { setActiveExercise(ex); setShowAnswer(false); setFeedback(null); setUserAnswer(""); }} className={`rounded px-2 py-1 text-[10px] font-medium ${activeExercise?.id === ex.id ? "bg-teal-600 text-white" : "bg-slate-100 hover:bg-slate-200"}`}>
                {i + 1}. {ex.title}
              </button>
            ))}
          </div>

          {activeExercise && (
            <div className="grid gap-3 lg:grid-cols-2">
              {/* Left: Exercise */}
              <div className="space-y-3">
                <div className="rounded-md border bg-white p-4">
                  <h4 className="text-sm font-bold text-slate-900">{activeExercise.title}</h4>
                  <div className="mt-2 text-xs text-slate-700 whitespace-pre-wrap bg-slate-50 rounded p-3">{activeExercise.instruction}</div>
                </div>

                <div className="rounded-md border bg-white p-4">
                  <h4 className="text-xs font-semibold text-slate-700 mb-2">Your Answer</h4>
                  <textarea value={userAnswer} onChange={(e) => setUserAnswer(e.target.value)} className="w-full rounded border px-3 py-2 text-xs font-mono min-h-[120px] bg-slate-900 text-green-400" placeholder="Write your SQL, config, or answer here..." />
                  <div className="flex gap-2 mt-2">
                    <button onClick={handleSubmit} className="rounded bg-teal-600 px-3 py-1 text-xs text-white hover:bg-teal-700">Submit & Check</button>
                    <button onClick={() => setShowAnswer(!showAnswer)} className="rounded bg-slate-200 px-3 py-1 text-xs hover:bg-slate-300">{showAnswer ? "Hide" : "Show"} Answer</button>
                  </div>
                </div>
              </div>

              {/* Right: Feedback */}
              <div className="space-y-3">
                {showAnswer && (
                  <div className="rounded-md border bg-white p-4">
                    <h4 className="text-xs font-semibold text-green-700 mb-2">✅ Expected Answer</h4>
                    <pre className="rounded bg-slate-900 text-emerald-400 p-3 overflow-x-auto text-[11px] whitespace-pre-wrap">{activeExercise.expected_answer}</pre>
                  </div>
                )}

                {(showAnswer || feedback) && (
                  <div className="rounded-md border border-indigo-200 bg-indigo-50 p-4">
                    <h4 className="text-xs font-semibold text-indigo-800 mb-2">🎓 Explanation</h4>
                    <p className="text-xs text-indigo-700 whitespace-pre-wrap">{activeExercise.explanation}</p>
                  </div>
                )}

                {activeExercise.tip && (showAnswer || feedback) && (
                  <div className="rounded-md border border-amber-200 bg-amber-50 p-4">
                    <h4 className="text-xs font-semibold text-amber-800 mb-2">💡 Pro Tip</h4>
                    <p className="text-xs text-amber-700">{activeExercise.tip}</p>
                  </div>
                )}

                {activeExercise.oracle_equivalent && (showAnswer || feedback) && (
                  <div className="rounded-md border bg-white p-4">
                    <h4 className="text-xs font-semibold text-slate-700 mb-2">Oracle Equivalent</h4>
                    <pre className="rounded bg-slate-900 text-orange-400 p-3 overflow-x-auto text-[11px] whitespace-pre-wrap">{activeExercise.oracle_equivalent}</pre>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="text-center text-[9px] text-slate-400">Training Twin – Synthetic Records – Demonstration Only</div>
    </div>
  );
}
