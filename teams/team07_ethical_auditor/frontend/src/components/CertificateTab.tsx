import React from 'react';
import { Download, Award, Shield, FileText, CheckCircle2 } from 'lucide-react';
import type { CertificateMetadata, ComplianceReport, AuditRecord } from '../types';

interface CertificateTabProps {
  certificate: CertificateMetadata;
  report: ComplianceReport;
  records: AuditRecord[];
}

export const CertificateTab: React.FC<CertificateTabProps> = ({
  certificate,
  report,
  records
}) => {
  const downloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
      certificate,
      report,
      auditTimestamp: new Date().toISOString()
    }, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `audit_report_team07_${certificate.certificate_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const downloadCsv = () => {
    if (!records.length) return;
    const headers = Object.keys(records[0]).join(",");
    const rows = records.map(r => Object.values(r).join(",")).join("\n");
    const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(`${headers}\n${rows}`);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", csvContent);
    downloadAnchor.setAttribute("download", `audited_retail_records_team07.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const isCompliant = report.risk_level === "COMPLIANT & AUDITED";

  return (
    <div className="space-y-6">
      {/* Module Badges */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#134074]/10 text-[#134074] border border-[#134074]/20 px-2.5 py-0.5 rounded">
          Official Governance Artifact
        </span>
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#C5A059]/15 text-[#7A5B15] border border-[#C5A059]/30 px-2.5 py-0.5 rounded">
          Audit Trail & Remediation Playbook
        </span>
      </div>

      {/* Certificate Box */}
      <div className="relative bg-white rounded-2xl border-2 border-[#C5A059] p-8 shadow-xl shadow-[#0B2545]/5 overflow-hidden">
        {/* Certificate Seal Badge */}
        <div className="absolute top-6 right-6 w-20 h-20 rounded-full border-2 border-dashed border-[#C5A059] bg-[#FAF7F2] flex flex-col items-center justify-center text-center shadow-inner">
          <Award className="w-5 h-5 text-[#C5A059] mb-0.5" />
          <span className="text-[8px] font-bold tracking-tight text-[#7A5B15] uppercase leading-tight">
            RETAIL AI<br />AUDIT
          </span>
        </div>

        <div className="max-w-xl">
          <div className="text-[10px] uppercase font-bold tracking-widest text-[#C5A059] mb-1">
            Verification Specification v2.1
          </div>
          <h2 className="font-serif-royal text-xl sm:text-2xl font-bold text-[#0B2545]">
            Certificate of Ethical AI Compliance
          </h2>
          <div className="font-mono text-xs font-semibold text-[#134074] mt-1">
            ID: {certificate.certificate_id}
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6 text-xs text-[#0B2545] border-t border-b border-[#C5A059]/20 py-4">
            <div>
              <span className="text-[#5C677D]">Target Model:</span><br />
              <strong>PricingEngine_v2.1</strong>
            </div>
            <div>
              <span className="text-[#5C677D]">Audited Records:</span><br />
              <strong>{certificate.records_audited} Transactions</strong>
            </div>
            <div>
              <span className="text-[#5C677D]">Steering Pearson r:</span><br />
              <strong>{report.bias.pearson_correlation > 0 ? '+' : ''}{report.bias.pearson_correlation.toFixed(3)}</strong>
            </div>
            <div>
              <span className="text-[#5C677D]">Disparate Impact:</span><br />
              <strong>{report.bias.disparate_impact_ratio.toFixed(2)} (EEOC)</strong>
            </div>
            <div>
              <span className="text-[#5C677D]">Privacy Breaches:</span><br />
              <strong>{report.privacy.breach_count} Unconsented Logs</strong>
            </div>
            <div>
              <span className="text-[#5C677D]">Final Verdict:</span><br />
              <strong className={isCompliant ? "text-[#1B4931]" : "text-[#9E2A2B]"}>
                {certificate.final_status}
              </strong>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {certificate.standard_alignment.map((std, i) => (
              <span key={i} className="text-[10px] bg-[#FAF7F2] border border-[#C5A059]/30 text-[#7A5B15] px-2 py-0.5 rounded font-mono">
                {std}
              </span>
            ))}
          </div>

          <div className="mt-6 text-[10px] text-[#5C677D] italic">
            Certified under the Retail AI Lab Evaluation Framework • Aligned with EU AI Act High-Risk Annex III & GDPR Article 22.
          </div>
        </div>
      </div>

      {/* Download Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          onClick={downloadJson}
          className="flex items-center justify-center gap-2 bg-[#0B2545] hover:bg-[#134074] text-white text-xs font-semibold py-3 px-4 rounded-xl border border-[#C5A059] shadow-sm transition-all"
        >
          <FileText className="w-4 h-4 text-[#D4AF37]" />
          Download Official Compliance Report (JSON)
        </button>

        <button
          onClick={downloadCsv}
          className="flex items-center justify-center gap-2 bg-white hover:bg-[#FAF7F2] text-[#0B2545] text-xs font-semibold py-3 px-4 rounded-xl border border-[#C5A059]/40 shadow-sm transition-all"
        >
          <Download className="w-4 h-4 text-[#C5A059]" />
          Download Audited Dataset (CSV)
        </button>
      </div>

      {/* Executive Remediation Playbook */}
      <div className="bg-white rounded-xl border border-[#C5A059]/30 p-6 shadow-sm">
        <h3 className="font-serif-royal text-base font-bold text-[#0B2545] mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-[#C5A059]" />
          Executive Remediation Playbook for Data Governance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-[#0B2545]">
          <div className="p-3.5 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 space-y-1">
            <div className="font-bold text-[#0B2545] flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#134074]" /> 1. Demographic Decoupling
            </div>
            <p className="text-[#5C677D] leading-relaxed">
              Introduce adversarial debiasing layers during model loss computation to penalize loss gradients correlated with customer zip codes or income proxies.
            </p>
          </div>

          <div className="p-3.5 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 space-y-1">
            <div className="font-bold text-[#0B2545] flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#134074]" /> 2. Strict Consent Gating
            </div>
            <p className="text-[#5C677D] leading-relaxed">
              Enforce cryptographic token verification at the inference gateway before piping raw customer context into active pricing inference routines.
            </p>
          </div>

          <div className="p-3.5 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 space-y-1">
            <div className="font-bold text-[#0B2545] flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#134074]" /> 3. Automated Right-to-Erasure
            </div>
            <p className="text-[#5C677D] leading-relaxed">
              Implement zero-latency quarantine queues purging non-consented logs within 60 seconds of user opt-out events under GDPR Article 17.
            </p>
          </div>

          <div className="p-3.5 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 space-y-1">
            <div className="font-bold text-[#0B2545] flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#134074]" /> 4. Continuous Four-Fifths Auditing
            </div>
            <p className="text-[#5C677D] leading-relaxed">
              Maintain automated telemetry alerting anytime the rolling 7-day disparate impact ratio drops below the EEOC 0.80 benchmark.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
