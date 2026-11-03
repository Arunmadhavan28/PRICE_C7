import React, { useState } from 'react';
import { Sliders, ShieldCheck, ShieldAlert, Target } from 'lucide-react';

export const SimulatorTab: React.FC = () => {
  const [selectedZip, setSelectedZip] = useState<number>(90210);
  const [category, setCategory] = useState<string>("Luxury Goods");
  const [consentGranted, setConsentGranted] = useState<boolean>(true);

  const zipMedians: Record<number, { mean: number; income: string; tier: string }> = {
    90210: { mean: 240.0, income: "$180k Avg", tier: "Affluent" },
    10021: { mean: 280.0, income: "$210k Avg", tier: "High Affluence" },
    30310: { mean: 55.0, income: "$45k Avg", tier: "Low-to-Mid Income" },
    48206: { mean: 42.0, income: "$38k Avg", tier: "Low Income" },
  };

  const catMultipliers: Record<string, number> = {
    "Luxury Goods": 1.4,
    "Footwear": 1.1,
    "Apparel": 0.9,
    "Accessories": 0.8,
  };

  const currentZip = zipMedians[selectedZip] || { mean: 100.0, income: "N/A", tier: "Standard" };
  const simulatedPrice = (currentZip.mean * (catMultipliers[category] || 1.0));
  const isAffluent = selectedZip === 90210 || selectedZip === 10021;

  return (
    <div className="space-y-6">
      {/* Module Badges */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#134074]/10 text-[#134074] border border-[#134074]/20 px-2.5 py-0.5 rounded">
          Stress-Testing Console
        </span>
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#C5A059]/15 text-[#7A5B15] border border-[#C5A059]/30 px-2.5 py-0.5 rounded">
          Synthetic Inference Bias Detection
        </span>
      </div>

      <div className="bg-white rounded-xl border border-[#C5A059]/30 p-6 shadow-sm">
        <div className="mb-6">
          <h2 className="font-serif-royal text-base font-bold text-[#0B2545] flex items-center gap-2">
            <Sliders className="w-4 h-4 text-[#C5A059]" />
            Interactive Demographic Red-Teaming Simulator
          </h2>
          <p className="text-xs text-[#5C677D] mt-0.5">
            Interactively probe the recommendation model to inspect if input demographic signals trigger disparate price steering.
          </p>
        </div>

        {/* Simulator Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 p-5 bg-[#FAF7F2] rounded-xl border border-[#C5A059]/30 mb-6">
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#0B2545] mb-2">
              Customer Demographic Zip Code:
            </label>
            <select
              value={selectedZip}
              onChange={(e) => setSelectedZip(Number(e.target.value))}
              className="w-full bg-white text-xs px-3 py-2 rounded-lg border border-[#C5A059]/40 text-[#0B2545] focus:outline-none focus:border-[#0B2545]"
            >
              <option value={90210}>90210 — Beverly Hills ($180k Avg)</option>
              <option value={10021}>10021 — Upper East Side ($210k Avg)</option>
              <option value={30310}>30310 — Atlanta West End ($45k Avg)</option>
              <option value={48206}>48206 — Detroit Central ($38k Avg)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#0B2545] mb-2">
              Product Catalog Category:
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-white text-xs px-3 py-2 rounded-lg border border-[#C5A059]/40 text-[#0B2545] focus:outline-none focus:border-[#0B2545]"
            >
              <option value="Luxury Goods">Luxury Goods</option>
              <option value="Apparel">Apparel</option>
              <option value="Footwear">Footwear</option>
              <option value="Accessories">Accessories</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#0B2545] mb-2">
              GDPR / CCPA Consent Status:
            </label>
            <label className="flex items-center gap-2 mt-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={consentGranted}
                onChange={(e) => setConsentGranted(e.target.checked)}
                className="w-4 h-4 rounded text-[#0B2545] focus:ring-[#C5A059] border-[#C5A059]"
              />
              <span className="text-xs text-[#0B2545] font-medium">
                Simulate Affirmative User Opt-In
              </span>
            </label>
          </div>
        </div>

        {/* Results Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
          {/* Price Output */}
          <div className="md:col-span-5 bg-white rounded-xl border border-[#C5A059]/40 border-t-[3px] border-t-[#C5A059] p-5 shadow-sm">
            <div className="text-[10px] uppercase font-bold tracking-wider text-[#5C677D] mb-1">
              Simulated AI Recommended Price
            </div>
            <div className="flex items-baseline gap-1">
              <span className="font-serif-royal text-3xl font-bold text-[#0B2545]">
                ${simulatedPrice.toFixed(2)}
              </span>
              <span className="text-xs text-[#5C677D]">USD</span>
            </div>
            <div className="text-xs text-[#5C677D] mt-1">
              Demographic Proxy: <strong>{currentZip.income}</strong> ({currentZip.tier})
            </div>

            <div className="mt-4 pt-3 border-t border-[#C5A059]/20 flex items-center justify-between">
              <span className="text-[11px] text-[#5C677D]">Consent Enforcement:</span>
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 ${
                consentGranted ? 'bg-[#1B4931]/10 text-[#1B4931]' : 'bg-[#9E2A2B]/10 text-[#9E2A2B]'
              }`}>
                {consentGranted ? <ShieldCheck className="w-3 h-3" /> : <ShieldAlert className="w-3 h-3" />}
                {consentGranted ? "CONSENT GRANTED" : "QUARANTINE TRIGGERED"}
              </span>
            </div>
          </div>

          {/* Governance Risk Evaluation */}
          <div className="md:col-span-7 bg-[#FAF7F2] rounded-xl border border-[#C5A059]/30 p-5">
            <div className="text-[10px] uppercase font-bold tracking-wider text-[#0B2545] mb-2 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-[#C5A059]" />
              Algorithmic Risk Assessment
            </div>
            <div className="text-xs text-[#0B2545] leading-relaxed space-y-2">
              <p>
                • <strong>Demographic Impact</strong>: Customer assigned to zip code {selectedZip} receives a recommendation benchmark of <strong>${simulatedPrice.toFixed(2)}</strong>.
              </p>
              <p>
                • <strong>Steering Finding</strong>: {isAffluent 
                  ? "Predatory steering: Affluent zip code received premium price multiplier, reflecting demographic price discrimination." 
                  : "Disparate exclusion: Lower-income demographic proxy steered toward clearance tier, depriving user of premium catalog exposure."}
              </p>
              <p>
                • <strong>Compliance Action</strong>: {consentGranted 
                  ? "Passed consent gating under GDPR Article 6." 
                  : "Model invocation without opt-in is a direct GDPR Article 6 & CCPA violation; transaction must be immediately halted."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
