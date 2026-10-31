'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Send, SlidersHorizontal } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task })
      });
      const data = await res.json();
      router.push(`/session/${data.id}`);
    } catch (err: any) {
      alert('Make sure backend is running on http://localhost:8000');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto pt-16 space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Browser Use Cloud
        </h1>
        <p className="text-sm text-slate-500">
          Autonomous browser execution with real-time screen streaming.
        </p>
      </div>

      <form onSubmit={handleStart} className="glass-card rounded-2xl p-6 shadow-sm border border-slate-200/80 space-y-4">
        <textarea
          rows={4}
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder="Ask the browser agent to do something..."
          className="w-full text-sm bg-transparent placeholder:text-slate-400 focus:outline-none resize-none"
        />

        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <span className="text-xs text-slate-400">Milestone 1 Ready</span>
          <button
            type="submit"
            disabled={loading || !task.trim()}
            className="flex items-center gap-2 bg-slate-900 text-white text-xs font-medium px-4 py-2 rounded-lg hover:bg-slate-800 transition"
          >
            <span>{loading ? 'Starting...' : 'Run Agent'}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
}
