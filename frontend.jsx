import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, Wallet, ShieldCheck, MessageSquare, FileText, 
  Smartphone, Award, Milestone, AlertTriangle, Bell, User,
  ArrowUpRight, ArrowDownRight, Sparkles, CheckCircle, BrainCircuit, Mic
} from 'lucide-react';

export default function WealthPathDashboard() {
  // --- STATE ---
  const [activeTab, setActiveTab] = useState('dashboard');
  const [crisisMode, setCrisisMode] = useState(false);
  const [scoreData, setScoreData] = useState({ financial_score: 68, target_year: 2048, nest_egg_needed: 750000 });
  
  const [profile, setProfile] = useState({
    name: "Alex Mercer",
    occupation: "Software Support",
    location: "Austin, USA",
    knowledge_level: "Beginner",
    income: 4500,
    expenses: 2800,
    debts: 12000,
    investments: 8500
  });

  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([
    { sender: 'ai', text: "Hi Alex! I'm your AI mentor. Ask me anything about budgeting, investments, or plans in plain language!" }
  ]);

  const [simScenario, setSimScenario] = useState('car');
  const [simCost, setSimCost] = useState(25000);
  const [smsTestMessage, setSmsTestMessage] = useState("Txn alert: Debited $42.50 at Grocery Mart on card xx41.");
  const [smsResult, setSmsResult] = useState(null);

  // --- API COMMUNICATIONS ---
  const fetchMetrics = async () => {
    try {
      // Modify dynamic expenses if crisis mode is flagged active
      const adjustedProfile = {
        ...profile,
        expenses: crisisMode ? profile.expenses * 0.6 : profile.expenses
      };

      const res = await fetch('http://127.0.0.1:8000/api/finance/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adjustedProfile)
      });
      const data = await res.json();
      setScoreData(data);
    } catch (err) {
      console.error("Backend offline. Using standard fallback calculations.");
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [profile, crisisMode]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/ai/mentor-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userMsg, profile })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { sender: 'ai', text: data.response }]);
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'ai', text: "I'm having trouble hitting my main AI matrix brains right now, but always remember: keeping expenses below income is the key asset rule!" }]);
    }
  };

  const testSmsParsing = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/sms/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: smsTestMessage })
      });
      const data = await res.json();
      setSmsResult(data);
    } catch (err) {
      alert("Backend API is offline.");
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${crisisMode ? 'bg-red-950 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      
      {/* CRISIS MODE NOTICE BANNER */}
      {crisisMode && (
        <div className="bg-red-600 text-white px-4 py-2 text-center text-xs font-bold flex items-center justify-center gap-2 animate-pulse">
          <AlertTriangle size={14} /> Crisis Survival Mode Active: Non-essential budgets locked to zero.
        </div>
      )}

      {/* HEADER SECTION */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-50 px-6 py-4 flex justify-between items-center shadow-xs">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-purple-600 to-indigo-600 p-2 rounded-xl text-white shadow-md">
            <BrainCircuit size={22} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900">WealthPath <span className="bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">AI</span></h1>
            <p className="text-[10px] tracking-wider uppercase text-slate-400 font-semibold">Plan Smarter. Retire Earlier.</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => setCrisisMode(!crisisMode)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${crisisMode ? 'bg-red-500 text-white' : 'bg-amber-100 text-amber-800 hover:bg-amber-200'}`}
          >
            <AlertTriangle size={12} /> {crisisMode ? "Exit Crisis Mode" : "Crisis Emergency Mode"}
          </button>
          <div className="flex items-center gap-2 border-l pl-4 border-slate-200">
            <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-700 font-bold flex items-center justify-center text-xs">AM</div>
            <span className="text-xs font-medium text-slate-700 max-sm:hidden">{profile.name}</span>
          </div>
        </div>
      </header>

      {/* APP WRAPPER GRID */}
      <div className="max-w-7xl mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* SIDE BAR BUTTON NAVIGATION */}
        <nav className="lg:col-span-3 flex lg:flex-col overflow-x-auto gap-1 bg-white p-2 rounded-xl h-fit border border-slate-200">
          {[
            { id: 'dashboard', label: 'Dashboard Horizon', icon: Wallet },
            { id: 'profile', label: 'Personal Financial Profile', icon: User },
            { id: 'ai-mentor', label: 'AI Mentor System', icon: MessageSquare },
            { id: 'sms-tracker', label: 'Smart Safe SMS Link', icon: Smartphone }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg font-medium text-xs transition-all w-full text-left whitespace-nowrap ${activeTab === tab.id ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'}`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* CONTAINER MAIN DASH VIEWS */}
        <main className="lg:col-span-9 space-y-6">

          {/* TAB 1: CORE DASHBOARD */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Score component card */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
                  <span className="text-xs font-bold tracking-wider text-slate-400 uppercase">Health Score</span>
                  <div className="flex items-baseline gap-1 mt-2">
                    <span className="text-4xl font-black text-slate-900">{scoreData.financial_score}</span>
                    <span className="text-xs text-slate-400">/100</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full mt-3">
                    <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${scoreData.financial_score}%` }}></div>
                  </div>
                </div>

                {/* Cash flow details */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
                  <span className="text-xs font-bold tracking-wider text-slate-400 uppercase">Cash Matrix</span>
                  <div className="space-y-1.5 mt-2 text-xs">
                    <div className="flex justify-between"><span className="text-slate-400">Inbound:</span><span className="font-bold text-emerald-600">${profile.income}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Outbound:</span><span className="font-bold text-rose-600">${crisisMode ? (profile.expenses * 0.6).toFixed(0) : profile.expenses}</span></div>
                  </div>
                </div>

                {/* Target Projection Card */}
                <div className="bg-gradient-to-tr from-purple-900 to-indigo-950 text-white p-5 rounded-xl shadow-xs">
                  <span className="text-xs text-purple-300 uppercase tracking-wider font-bold">Freedom Horizon</span>
                  <p className="text-3xl font-black my-1 text-transparent bg-clip-text bg-gradient-to-r from-white to-purple-200">{scoreData.target_year}</p>
                  <p className="text-[11px] text-purple-300">Nest Egg Needed: <span className="font-bold text-white">${scoreData.nest_egg_needed.toLocaleString()}</span></p>
                </div>
              </div>

              {/* ROADMAP SECTIONS */}
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
                <h3 className="text-sm font-bold text-slate-900 mb-4">Personalized Step-by-Step Freedom Road</h3>
                <div className="relative border-l border-purple-200 ml-2 pl-4 space-y-4 text-xs">
                  <div>
                    <h4 className="font-bold text-slate-800">1. Setup Starter Cash Reserve Pile</h4>
                    <p className="text-slate-500">Keep emergency cash safe before handling stock or index markets.</p>
                  </div>
                  <div>
                    <h4 className="font-bold text-purple-600">2. Wipe Out Debt Arbitrage Matrix</h4>
                    <p className="text-slate-500">Your total active debt sits at ${profile.debts}. Focus on the smallest card balance first.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PROFILE PROFILE */}
          {activeTab === 'profile' && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs space-y-4">
              <h3 className="text-sm font-bold text-slate-900">Your Financial Parameters</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-bold mb-1">Monthly Income ($)</label>
                  <input type="number" className="w-full border p-2 rounded-lg" value={profile.income} onChange={e => setProfile({...profile, income: Number(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-400 font-bold mb-1">Monthly Expenses ($)</label>
                  <input type="number" className="w-full border p-2 rounded-lg" value={profile.expenses} onChange={e => setProfile({...profile, expenses: Number(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-400 font-bold mb-1">Active Debt Total ($)</label>
                  <input type="number" className="w-full border p-2 rounded-lg" value={profile.debts} onChange={e => setProfile({...profile, debts: Number(e.target.value)})} />
                </div>
                <div>
                  <label className="block text-slate-400 font-bold mb-1">Investments Pool ($)</label>
                  <input type="number" className="w-full border p-2 rounded-lg" value={profile.investments} onChange={e => setProfile({...profile, investments: Number(e.target.value)})} />
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: CHAT MODULE */}
          {activeTab === 'ai-mentor' && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-2xs h-[450px] flex flex-col overflow-hidden">
              <div className="p-4 bg-slate-50 border-b text-xs font-bold text-slate-700">AI Financial Mentor Chat Sandbox</div>
              <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] px-3 py-2 rounded-xl ${msg.sender === 'user' ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-800'}`}>{msg.text}</div>
                  </div>
                ))}
              </div>
              <form onSubmit={handleSendMessage} className="p-3 border-t bg-slate-50 flex gap-2">
                <input type="text" className="flex-1 text-xs px-3 py-2 border rounded-xl" placeholder="Ask about stocks, mutual funds, index funds..." value={chatInput} onChange={e => setChatInput(e.target.value)} />
                <button type="submit" className="bg-purple-600 hover:bg-purple-700 text-white text-xs px-4 py-1.5 rounded-xl font-bold">Ask Mentor</button>
              </form>
            </div>
          )}

          {/* TAB 4: SMS PRIVACY ASSURANCE TESTER */}
          {activeTab === 'sms-tracker' && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs space-y-4">
              <h3 className="text-sm font-bold text-slate-900">SMS Sync Security Gate Engine</h3>
              <p className="text-xs text-slate-500">Test how messages with sensitive credentials are dropped instantly by our security parser.</p>
              
              <div className="space-y-2">
                <textarea className="w-full text-xs font-mono border p-2 rounded-lg" rows={2} value={smsTestMessage} onChange={e => setSmsTestMessage(e.target.value)} />
                <div className="flex gap-2">
                  <button onClick={testSmsParsing} className="bg-purple-600 text-white text-xs px-4 py-2 rounded-lg font-bold">Scan Message Security</button>
                  <button onClick={() => setSmsTestMessage("Your single sign-on authentication OTP security token is: 954102.")} className="border text-xs px-3 py-2 rounded-lg">Load Mock OTP Alert</button>
                </div>
              </div>

              {smsResult && (
                <div className="bg-slate-50 border p-3 rounded-lg text-xs space-y-1">
                  <div><strong>System Response Action:</strong> <span className={smsResult.status === 'PARSED_SUCCESSFULLY' ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold'}>{smsResult.status}</span></div>
                  <div><strong>Calculated Matrix Category:</strong> {smsResult.category}</div>
                  {smsResult.amount > 0 && <div><strong>Extracted Balance Figure:</strong> ${smsResult.amount}</div>}
                  <div className="text-slate-400 text-[11px] italic">{smsResult.description}</div>
                </div>
              )}
            </div>
          )}

        </main>
      </div>
    </div>
  );
}