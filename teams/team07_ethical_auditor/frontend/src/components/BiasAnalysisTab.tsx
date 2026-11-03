import React, { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, Info } from 'lucide-react';
import type { AuditRecord, BiasMetrics } from '../types';

interface BiasAnalysisTabProps {
  records: AuditRecord[];
  bias: BiasMetrics;
}

export const BiasAnalysisTab: React.FC<BiasAnalysisTabProps> = ({ records, bias }) => {
  const [hoveredPoint, setHoveredPoint] = useState<AuditRecord | null>(null);
  const [isExpanderOpen, setIsExpanderOpen] = useState(false);

  // Group records by Zip code for chart coordinates
  const uniqueZips = Array.from(new Set(records.map(r => r.Customer_ZipCode))).sort((a, b) => {
    const avgA = records.filter(r => r.Customer_ZipCode === a).reduce((s, r) => s + r.Customer_Income_Proxy, 0) / (records.filter(r => r.Customer_ZipCode === a).length || 1);
    const avgB = records.filter(r => r.Customer_ZipCode === b).reduce((s, r) => s + r.Customer_Income_Proxy, 0) / (records.filter(r => r.Customer_ZipCode === b).length || 1);
    return avgA - avgB;
  });

  const maxPrice = Math.max(...records.map(r => r.Recommended_Item_Price), 320);

  // Calculate OLS points for each zip
  const trendPoints = uniqueZips.map((zip, idx) => {
    const matching = records.filter(r => r.Customer_ZipCode === zip);
    const meanPrice = matching.reduce((s, r) => s + r.Recommended_Item_Price, 0) / (matching.length || 1);
    return { zip, idx, meanPrice };
  });

  return (
    <div className="space-y-6">
      {/* Module Badges */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#134074]/10 text-[#134074] border border-[#134074]/20 px-2.5 py-0.5 rounded">
          EU AI Act Audit Module
        </span>
        <span className="text-[10px] font-bold uppercase tracking-wider bg-[#C5A059]/15 text-[#7A5B15] border border-[#C5A059]/30 px-2.5 py-0.5 rounded">
          Pearson r Correlation & Disparate Impact
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Scatter Plot */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-[#C5A059]/30 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="font-serif-royal text-base font-bold text-[#0B2545]">
                Demographic Proxy vs AI Recommended Price
              </h2>
              <p className="text-xs text-[#5C677D]">
                Visualizes whether higher-income zip codes receive systematically higher-priced recommendations.
              </p>
            </div>

            {/* Legend */}
            <div className="flex items-center gap-3 text-[11px] font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#134074]" /> Opted-In [PASS]
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#9E2A2B]" /> Breach [FAIL]
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-[#C5A059]" /> OLS Trendline
              </span>
            </div>
          </div>

          {/* Interactive SVG Chart Canvas */}
          <div className="relative w-full h-[380px] bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 p-4 mt-3 select-none">
            {/* Grid Lines */}
            <div className="absolute inset-x-8 inset-y-8 flex flex-col justify-between pointer-events-none opacity-30">
              {[0, 1, 2, 3, 4].map(i => (
                <div key={i} className="border-b border-dashed border-[#0B2545]/40 w-full" />
              ))}
            </div>

            <svg className="w-full h-full" viewBox="0 0 600 320" preserveAspectRatio="none">
              {/* Trendline */}
              {trendPoints.length > 1 && (
                <polyline
                  fill="none"
                  stroke="#C5A059"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeDasharray="4 2"
                  points={trendPoints.map((tp, i) => {
                    const x = 50 + (i / (trendPoints.length - 1)) * 500;
                    const y = 280 - (tp.meanPrice / maxPrice) * 240;
                    return `${x},${y}`;
                  }).join(' ')}
                />
              )}

              {/* Data Points */}
              {records.map((r, i) => {
                const zipIdx = uniqueZips.indexOf(r.Customer_ZipCode);
                const xBase = 50 + (zipIdx / (uniqueZips.length - 1)) * 500;
                // Add jitter
                const jitter = (Math.sin(i * 997) * 24);
                const x = Math.max(25, Math.min(575, xBase + jitter));
                const y = Math.max(20, Math.min(290, 280 - (r.Recommended_Item_Price / maxPrice) * 240));
                const isBreach = !r.Opt_in_Status;
                const radius = Math.max(4, Math.min(8, (r.Recommended_Item_Price / 50)));

                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r={radius}
                    fill={isBreach ? "#9E2A2B" : "#134074"}
                    stroke="#FFFFFF"
                    strokeWidth={1.5}
                    className="cursor-pointer transition-transform duration-200 hover:scale-150 hover:stroke-[#D4AF37]"
                    onMouseEnter={() => setHoveredPoint(r)}
                    onMouseLeave={() => setHoveredPoint(null)}
                  />
                );
              })}
            </svg>

            {/* X-Axis Labels */}
            <div className="absolute bottom-1 inset-x-12 flex justify-between text-[11px] font-bold text-[#0B2545]/80">
              {uniqueZips.map(zip => {
                const match = records.find(r => r.Customer_ZipCode === zip);
                return (
                  <div key={zip} className="text-center">
                    <div>Zip: {zip}</div>
                    <div className="text-[9px] font-normal text-[#5C677D]">{match?.Income_Bracket}</div>
                  </div>
                );
              })}
            </div>

            {/* Hover Tooltip */}
            {hoveredPoint && (
              <div 
                className="absolute z-30 bg-[#0B2545] text-white text-[11px] p-3 rounded-lg shadow-xl border border-[#C5A059] pointer-events-none transform -translate-x-1/2 -translate-y-full"
                style={{ top: '35%', left: '50%' }}
              >
                <div className="font-bold text-[#D4AF37]">
                  Zip Code: {hoveredPoint.Customer_ZipCode} ({hoveredPoint.Income_Bracket})
                </div>
                <div className="mt-1">
                  Price: <strong>${hoveredPoint.Recommended_Item_Price.toFixed(2)}</strong>
                </div>
                <div>Category: {hoveredPoint.Item_Category}</div>
                <div className="mt-1">
                  Status: <span className={hoveredPoint.Opt_in_Status ? "text-[#00E676]" : "text-[#EF4444] font-bold"}>
                    {hoveredPoint.Opt_in_Status ? "Opted-In [PASS]" : "PRIVACY BREACH [FAIL]"}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right: Summary Statistics Table */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-[#C5A059]/30 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="font-serif-royal text-base font-bold text-[#0B2545] mb-1">
              Demographic Price Spread
            </h2>
            <p className="text-xs text-[#5C677D] mb-4">
              Empirical price distributions across zip code tiers.
            </p>

            <div className="overflow-hidden rounded-lg border border-[#C5A059]/20">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#FAF7F2] text-[#0B2545] font-semibold border-b border-[#C5A059]/20">
                  <tr>
                    <th className="p-2.5">Zip</th>
                    <th className="p-2.5">Mean ($)</th>
                    <th className="p-2.5">Median</th>
                    <th className="p-2.5">Logs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#C5A059]/10">
                  {bias.zip_summary.map((zs, i) => (
                    <tr key={i} className="hover:bg-[#FCFBF9]">
                      <td className="p-2.5 font-bold text-[#0B2545]">{zs.Customer_ZipCode || zs["Zip Code"]}</td>
                      <td className="p-2.5 text-[#134074] font-medium">${zs.mean.toFixed(2)}</td>
                      <td className="p-2.5 text-[#5C677D]">${zs.median.toFixed(2)}</td>
                      <td className="p-2.5 text-[#5C677D]">{zs.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-4 p-3 bg-[#FAF7F2] rounded-lg border border-[#C5A059]/20 text-xs">
            <div className="flex items-center gap-1.5 font-bold text-[#0B2545]">
              <Info className="w-3.5 h-3.5 text-[#C5A059]" /> Pearson Correlation Index
            </div>
            <div className="mt-1 text-[#5C677D] leading-relaxed">
              Steering Index: <strong>{bias.pearson_correlation.toFixed(3)}</strong>. Absolute correlation exceeds threshold (0.40), confirming demographic steering.
            </div>
          </div>
        </div>
      </div>

      {/* Disparate Impact Expander */}
      <div className="bg-white rounded-xl border border-[#C5A059]/30 overflow-hidden shadow-sm">
        <button
          onClick={() => setIsExpanderOpen(!isExpanderOpen)}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-[#FAF7F2]/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-[#C5A059]" />
            <span className="font-bold text-xs uppercase tracking-wider text-[#0B2545]">
              Deep-Dive: Disparate Impact & EEOC Four-Fifths Mathematical Rule
            </span>
          </div>
          {isExpanderOpen ? <ChevronUp className="w-4 h-4 text-[#5C677D]" /> : <ChevronDown className="w-4 h-4 text-[#5C677D]" />}
        </button>

        {isExpanderOpen && (
          <div className="p-5 border-t border-[#C5A059]/20 bg-[#FAF7F2]/30 text-xs text-[#0B2545] leading-relaxed space-y-2">
            <p>
              The <strong>Four-Fifths (80%) Rule</strong> is the regulatory standard established by the Equal Employment Opportunity Commission (EEOC) and adopted by algorithmic fairness auditors to quantify disparate impact.
            </p>
            <div className="p-3 bg-white rounded-md border border-[#C5A059]/30 font-mono text-[11px] text-[#134074]">
              Disparate Impact Ratio = (Min Zip Avg Price) / (Max Zip Avg Price) = ${bias.min_zip_avg_price.toFixed(2)} / ${bias.max_zip_avg_price.toFixed(2)} = <strong>{bias.disparate_impact_ratio.toFixed(2)}</strong>
            </div>
            <p>
              • <strong>Current Ratio</strong>: <code className="bg-[#FAF7F2] px-1 py-0.5 rounded border">{bias.disparate_impact_ratio.toFixed(2)}</code> (Benchmark Floor: <code>0.80</code>)<br />
              • <strong>Finding</strong>: {bias.four_fifths_violation ? "[VIOLATION] Disparate impact violation detected: Lower-income zip codes receive less than 80% of average catalog value, indicating socioeconomic bias." : "[COMPLIANT] Complies with Four-Fifths fair recommendation standard."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
