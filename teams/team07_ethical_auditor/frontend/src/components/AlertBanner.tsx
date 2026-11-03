import React from 'react';
import { AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-react';
import type { ComplianceReport } from '../types';

interface AlertBannerProps {
  report: ComplianceReport;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({ report }) => {
  const isCritical = report.risk_level === "CRITICAL NON-COMPLIANCE";
  const isWarning = report.risk_level.includes("WARNING");
  const isCompliant = report.risk_level === "COMPLIANT & AUDITED";

  return (
    <div 
      className={`relative w-full rounded-xl p-4 mb-6 border transition-all duration-300 shadow-sm ${
        isCritical 
          ? 'bg-[#9E2A2B]/10 border-[#9E2A2B]/40 text-[#9E2A2B]'
          : isWarning
          ? 'bg-[#C5A059]/15 border-[#C5A059]/50 text-[#7A5B15]'
          : 'bg-[#1B4931]/10 border-[#1B4931]/40 text-[#1B4931]'
      }`}
    >
      <div className="flex items-start gap-3.5">
        <div className="mt-0.5 shrink-0">
          {isCritical && <AlertTriangle className="w-5 h-5 text-[#9E2A2B] animate-pulse" />}
          {isWarning && <AlertCircle className="w-5 h-5 text-[#C5A059]" />}
          {isCompliant && <CheckCircle2 className="w-5 h-5 text-[#1B4931]" />}
        </div>

        <div className="flex-1 text-xs leading-relaxed">
          <div className="font-bold tracking-wide uppercase text-[11px] mb-0.5">
            {isCritical && "CRITICAL RED-TEAMING NON-COMPLIANCE ALERT"}
            {isWarning && "REGULATORY COMPLIANCE ADVISORY"}
            {isCompliant && "STATUS: COMPLIANT & AUDITED"}
          </div>
          <div>
            <strong>{report.risk_level}</strong> — {report.recommended_action}
          </div>
        </div>
      </div>
    </div>
  );
};
