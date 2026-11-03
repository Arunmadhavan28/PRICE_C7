import type { AuditRecord, PrivacyMetrics } from '../types';
import React, { useState } from 'react';
import { Trash2, RotateCcw, CheckCircle2, Search } from 'lucide-react';

interface PrivacyVaultTabProps {
  breaches: AuditRecord[];
  privacy: PrivacyMetrics;
  onScrub: () => void;
  onReset: () => void;
  isScrubbed: boolean;
}

export const PrivacyVaultTab: React.FC<PrivacyVaultTabProps> = ({
  breaches,
  privacy,
  onScrub,
  onReset,
  isScrubbed
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isScrubbing, setIsScrubbing] = useState(false);
  const [scrubProgress, setScrubProgress] = useState(0);

  const filteredBreaches = breaches.filter(b => 
    b.Customer_ZipCode.toString().includes(searchTerm) ||
    b.Item_Category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleScrubClick = () => {
    setIsScrubbing(true);
    setScrubProgress(20);

    setTimeout(() => setScrubProgress(60), 300);
    setTimeout(() => setScrubProgress(95), 600);
    setTimeout(() => {
      setIsScrubbing(false);
      setScrubProgress(100);
      onScrub();
    }, 850);
  };

  return (
    <div className="space-y-6">
      {/* Module Badges */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#134074]/10 text-[#134074] border border-[#134074]/20 px-2.5 py-0.5 rounded">
          GDPR Article 6 & 17 Vault
        </span>
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#C5A059]/15 text-[#7A5B15] border border-[#C5A059]/30 px-2.5 py-0.5 rounded">
          Right to Erasure & Consent Enforcement
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Quarantined Records Table */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-[#C5A059]/30 p-5 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <h2 className="font-serif-royal text-base font-bold text-[#0B2545]">
                Quarantined Non-Consented User Records
              </h2>
              <p className="text-xs text-[#5C677D]">
                Users who did not provide affirmative consent or who opted out, yet were inadvertently processed.
              </p>
            </div>

            {/* Search */}
            <div className="relative w-full sm:w-56">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-[#5C677D]" />
              <input
                type="text"
                placeholder="Search zip or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#FAF7F2] text-xs pl-8 pr-3 py-1.5 rounded-lg border border-[#C5A059]/30 focus:outline-none focus:border-[#0B2545] text-[#0B2545]"
              />
            </div>
          </div>

          {/* Scrub Progress Bar */}
          {isScrubbing && (
            <div className="mb-4 p-3 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/40">
              <div className="flex justify-between text-xs font-semibold text-[#0B2545] mb-1">
                <span>Executing Cryptographic GDPR Purge...</span>
                <span>{scrubProgress}%</span>
              </div>
              <div className="w-full bg-white h-2 rounded-full overflow-hidden border">
                <div 
                  className="bg-[#C5A059] h-full transition-all duration-300"
                  style={{ width: `${scrubProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Table Container */}
          {breaches.length > 0 ? (
            <div className="overflow-x-auto rounded-lg border border-[#C5A059]/20 max-h-[340px]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#FAF7F2] text-[#0B2545] font-semibold sticky top-0 border-b border-[#C5A059]/20">
                  <tr>
                    <th className="p-3">Customer Zip</th>
                    <th className="p-3">Price ($)</th>
                    <th className="p-3">Consent Status</th>
                    <th className="p-3">Category</th>
                    <th className="p-3">Engine</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#C5A059]/10">
                  {filteredBreaches.map((row, idx) => (
                    <tr key={idx} className="hover:bg-[#FCFBF9]">
                      <td className="p-3 font-semibold text-[#0B2545]">{row.Customer_ZipCode}</td>
                      <td className="p-3 font-medium text-[#134074]">${row.Recommended_Item_Price.toFixed(2)}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#9E2A2B]/10 text-[#9E2A2B]">
                          BREACH [FAIL]
                        </span>
                      </td>
                      <td className="p-3 text-[#5C677D]">{row.Item_Category}</td>
                      <td className="p-3 font-mono text-[10px] text-[#5C677D]">{row.Recommendation_Algorithm}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 bg-[#FAF7F2]/40 rounded-lg border border-dashed border-[#C5A059]/40">
              <CheckCircle2 className="w-10 h-10 text-[#00E676] mx-auto mb-2" />
              <h3 className="font-bold text-[#0B2545] text-sm">Full Privacy Compliance Verified</h3>
              <p className="text-xs text-[#5C677D] mt-1">
                Zero unconsented user records exist in the active recommendation pipeline.
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 mt-4">
            {breaches.length > 0 ? (
              <button
                onClick={handleScrubClick}
                disabled={isScrubbing}
                className="flex items-center gap-2 bg-[#0B2545] hover:bg-[#134074] text-white text-xs font-semibold px-4 py-2.5 rounded-lg border border-[#C5A059] shadow-sm transition-all hover:shadow"
              >
                <Trash2 className="w-3.5 h-3.5 text-[#D4AF37]" />
                Simulate Automated GDPR Data Scrub / Quarantine
              </button>
            ) : (
              <button
                onClick={onReset}
                className="flex items-center gap-2 bg-white hover:bg-[#FAF7F2] text-[#0B2545] text-xs font-semibold px-4 py-2.5 rounded-lg border border-[#C5A059]/40 transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5 text-[#C5A059]" />
                Restore Original Raw Inferences
              </button>
            )}

            {isScrubbed && (
              <span className="text-xs text-[#1B4931] font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Active Dataset Encrypted & Quarantined
              </span>
            )}
          </div>
        </div>

        {/* Right: Consent Doughnut & Risk Status */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-[#C5A059]/30 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="font-serif-royal text-base font-bold text-[#0B2545] mb-1">
              Consent Distribution
            </h2>
            <p className="text-xs text-[#5C677D] mb-4">
              Opted-in vs unconsented processing ratio.
            </p>

            {/* SVG Doughnut Chart */}
            <div className="relative w-40 h-40 mx-auto my-2 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="62"
                  stroke="#FAF7F2"
                  strokeWidth="16"
                  fill="none"
                />
                {/* Consented Arc */}
                <circle
                  cx="80"
                  cy="80"
                  r="62"
                  stroke="#134074"
                  strokeWidth="16"
                  strokeDasharray={390}
                  strokeDashoffset={390 * (1 - (privacy.consented_count / privacy.total_records))}
                  strokeLinecap="round"
                  fill="none"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute text-center">
                <div className="font-serif-royal text-lg font-bold text-[#0B2545]">
                  {Math.round((privacy.consented_count / privacy.total_records) * 100)}%
                </div>
                <div className="text-[9px] uppercase tracking-wider text-[#5C677D]">Consented</div>
              </div>
            </div>

            <div className="flex justify-center gap-6 mt-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-[#134074]" />
                <span className="text-[#5C677D]">Consented ({privacy.consented_count})</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-[#9E2A2B]" />
                <span className="text-[#5C677D]">Breach ({privacy.breach_count})</span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-4 rounded-xl bg-[#FAF7F2] border border-[#C5A059]/30">
            <div className="text-[10px] uppercase font-bold tracking-wider text-[#5C677D]">
              Consent Integrity Status
            </div>
            <div className={`text-sm font-bold mt-1 ${privacy.privacy_compliant ? 'text-[#1B4931]' : 'text-[#9E2A2B]'}`}>
              {privacy.regulatory_risk}
            </div>
            <div className="text-[11px] text-[#5C677D] mt-1">
              Total Processed Records: {privacy.total_records}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
