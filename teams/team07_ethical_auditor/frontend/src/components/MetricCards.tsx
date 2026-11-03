import React from 'react';
import { Lock, TrendingUp, Scale, Award } from 'lucide-react';
import type { ComplianceReport } from '../types';

interface MetricCardsProps {
  report: ComplianceReport;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ report }) => {
  const { privacy, bias, governance_score } = report;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* 1. Privacy Breaches */}
      <div className="relative group bg-white rounded-xl border border-[#C5A059]/30 border-t-[3px] border-t-[#C5A059] p-5 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1 overflow-hidden">
        <div className="flex items-center justify-between text-[#5C677D] text-[11px] font-bold tracking-wider uppercase mb-2">
          <span>Privacy Breaches</span>
          <Lock className="w-4 h-4 text-[#0B2545]/60 group-hover:text-[#C5A059] transition-colors" />
        </div>
        <div className="font-serif-royal text-2xl font-bold text-[#0B2545]">
          {privacy.breach_count} <span className="text-sm font-sans font-normal text-[#5C677D]">records</span>
        </div>
        <div className="mt-2.5 flex items-center justify-between text-[11px]">
          <span className={`px-2 py-0.5 rounded font-semibold ${
            privacy.breach_count > 0 ? 'bg-[#9E2A2B]/10 text-[#9E2A2B]' : 'bg-[#1B4931]/10 text-[#1B4931]'
          }`}>
            {privacy.breach_rate_pct}% of total
          </span>
          <span className="text-[#5C677D] text-[10px]">GDPR Art. 6</span>
        </div>
      </div>

      {/* 2. Demographic Bias (Pearson r) */}
      <div className="relative group bg-white rounded-xl border border-[#C5A059]/30 border-t-[3px] border-t-[#134074] p-5 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1 overflow-hidden">
        <div className="flex items-center justify-between text-[#5C677D] text-[11px] font-bold tracking-wider uppercase mb-2">
          <span>Demographic Bias (r)</span>
          <TrendingUp className="w-4 h-4 text-[#0B2545]/60 group-hover:text-[#134074] transition-colors" />
        </div>
        <div className="font-serif-royal text-2xl font-bold text-[#0B2545]">
          {bias.pearson_correlation > 0 ? `+${bias.pearson_correlation.toFixed(3)}` : bias.pearson_correlation.toFixed(3)}
        </div>
        <div className="mt-2.5 flex items-center justify-between text-[11px]">
          <span className={`px-2 py-0.5 rounded font-semibold ${
            bias.statistically_significant ? 'bg-[#9E2A2B]/10 text-[#9E2A2B]' : 'bg-[#1B4931]/10 text-[#1B4931]'
          }`}>
            p = {bias.p_value.toFixed(4)} {bias.statistically_significant ? '(Significant)' : '(Insignif)'}
          </span>
          <span className="text-[#5C677D] text-[10px]">Price Steering</span>
        </div>
      </div>

      {/* 3. Disparate Impact Ratio */}
      <div className="relative group bg-white rounded-xl border border-[#C5A059]/30 border-t-[3px] border-t-[#C5A059] p-5 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1 overflow-hidden">
        <div className="flex items-center justify-between text-[#5C677D] text-[11px] font-bold tracking-wider uppercase mb-2">
          <span>Disparate Impact Ratio</span>
          <Scale className="w-4 h-4 text-[#0B2545]/60 group-hover:text-[#C5A059] transition-colors" />
        </div>
        <div className="font-serif-royal text-2xl font-bold text-[#0B2545]">
          {bias.disparate_impact_ratio.toFixed(2)}
        </div>
        <div className="mt-2.5 flex items-center justify-between text-[11px]">
          <span className={`px-2 py-0.5 rounded font-semibold ${
            bias.four_fifths_violation ? 'bg-[#9E2A2B]/10 text-[#9E2A2B]' : 'bg-[#1B4931]/10 text-[#1B4931]'
          }`}>
            Spread: ${bias.price_spread.toFixed(2)}
          </span>
          <span className="text-[#5C677D] text-[10px]">EEOC 80% Rule</span>
        </div>
      </div>

      {/* 4. AI Governance Index Gauge */}
      <div className="relative group bg-white rounded-xl border border-[#C5A059]/30 border-t-[3px] border-t-[#0B2545] p-5 shadow-sm hover:shadow-md transition-all duration-300 hover:-translate-y-1 overflow-hidden">
        <div className="flex items-center justify-between text-[#5C677D] text-[11px] font-bold tracking-wider uppercase mb-2">
          <span>AI Governance Index</span>
          <Award className="w-4 h-4 text-[#0B2545]/60 group-hover:text-[#D4AF37] transition-colors" />
        </div>
        <div className="flex items-center justify-between">
          <div className="font-serif-royal text-2xl font-bold text-[#0B2545]">
            {governance_score} <span className="text-sm font-sans font-normal text-[#5C677D]">/ 100</span>
          </div>

          {/* Mini Circular Gauge SVG */}
          <div className="relative w-10 h-10 flex items-center justify-center">
            <svg className="w-10 h-10 -rotate-90">
              <circle
                cx="20"
                cy="20"
                r="16"
                stroke="#FAF7F2"
                strokeWidth="3.5"
                fill="none"
              />
              <circle
                cx="20"
                cy="20"
                r="16"
                stroke={governance_score >= 80 ? '#0B2545' : '#C5A059'}
                strokeWidth="3.5"
                strokeDasharray={100}
                strokeDashoffset={100 - governance_score}
                strokeLinecap="round"
                fill="none"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <span className="absolute text-[9px] font-bold text-[#0B2545]">
              {governance_score}%
            </span>
          </div>
        </div>
        <div className="mt-2.5 flex items-center justify-between text-[11px]">
          <span className="text-[#134074] font-semibold">
            {governance_score >= 80 ? "Audit Passed" : "Action Required"}
          </span>
          <span className="text-[#5C677D] text-[10px]">{privacy.total_records} Logs Checked</span>
        </div>
      </div>
    </div>
  );
};
