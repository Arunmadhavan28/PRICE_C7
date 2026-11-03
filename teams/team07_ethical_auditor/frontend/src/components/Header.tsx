import React, { useEffect, useRef } from 'react';
import { ShieldCheck, Scale, Cpu, Activity } from 'lucide-react';
import { gsap } from 'gsap';
import { RadarScanner } from './RadarScanner';
import { ThreeShieldRadar } from './ThreeShieldRadar';

interface HeaderProps {
  isScrubbed: boolean;
  totalRecords: number;
}

export const Header: React.FC<HeaderProps> = ({ isScrubbed, totalRecords }) => {
  const headerRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (headerRef.current && titleRef.current) {
      gsap.fromTo(
        headerRef.current,
        { opacity: 0, y: -15 },
        { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }
      );
      gsap.fromTo(
        titleRef.current,
        { letterSpacing: "2px" },
        { letterSpacing: "0.2px", duration: 1.2, ease: "expo.out" }
      );
    }
  }, []);

  return (
    <header 
      ref={headerRef}
      className="relative w-full rounded-2xl bg-gradient-to-r from-[#0B2545] via-[#134074] to-[#0B2545] border border-[#C5A059]/40 border-t-2 border-t-[#D4AF37] p-6 mb-6 shadow-xl shadow-[#0B2545]/15 overflow-hidden"
    >
      {/* Subtle Metallic Gold Top Line */}
      <div className="absolute top-0 left-0 right-0 h-[1.5px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent" />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#FCFBF9]/10 border border-[#C5A059]/40 backdrop-blur-sm text-[#D4AF37]">
              <Scale className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] uppercase font-bold tracking-widest text-[#C5A059] bg-[#C5A059]/15 border border-[#C5A059]/30 px-2 py-0.5 rounded">
                  Retail AI Lab • Track 07
                </span>
                <span className="text-[10px] uppercase tracking-wider text-white/60">
                  Autonomous Governance Engine
                </span>
              </div>
              <h1 
                ref={titleRef}
                className="font-serif-royal text-2xl lg:text-3xl font-bold tracking-tight text-[#FCFBF9] mt-0.5"
              >
                Ethical AI Auditor for Retail
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-3 text-[11px] text-[#F4EBD9]/80 font-medium">
            <span className="flex items-center gap-1.5 bg-black/20 px-2.5 py-1 rounded-md border border-white/10">
              <Cpu className="w-3.5 h-3.5 text-[#C5A059]" />
              Model: <strong className="text-white">PricingEngine_v2.1</strong>
            </span>
            <span className="flex items-center gap-1.5 bg-black/20 px-2.5 py-1 rounded-md border border-white/10">
              <ShieldCheck className="w-3.5 h-3.5 text-[#00E676]" />
              Policy: <strong className="text-white">EU AI Act High-Risk Annex III & GDPR Art. 22</strong>
            </span>
            <span className="flex items-center gap-1.5 bg-black/20 px-2.5 py-1 rounded-md border border-white/10">
              <Activity className="w-3.5 h-3.5 text-[#D4AF37]" />
              Active Telemetry: <strong className="text-white">{totalRecords} Inferences</strong>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Three.js 3D Holographic Wireframe */}
          <ThreeShieldRadar isCompliant={isScrubbed} />

          {/* Interactive Motion Radar Scanner */}
          <RadarScanner 
            label={isScrubbed ? "QUARANTINED & SCRUBBED" : "ACTIVE STREAM SCAN"} 
            isCompliant={isScrubbed} 
          />
        </div>
      </div>
    </header>
  );
};
