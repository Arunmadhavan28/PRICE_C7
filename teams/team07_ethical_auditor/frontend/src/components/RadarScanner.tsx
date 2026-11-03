import React from 'react';

interface RadarScannerProps {
  label?: string;
  isCompliant?: boolean;
}

export const RadarScanner: React.FC<RadarScannerProps> = ({
  label = "ACTIVE STREAM SCAN",
  isCompliant = false
}) => {
  return (
    <div className="flex items-center gap-3.5 bg-white/10 backdrop-blur-md border border-[#C5A059]/30 px-4 py-2 rounded-full shadow-inner">
      <div className="relative w-8 h-8 rounded-full border border-[#D4AF37] flex items-center justify-center overflow-hidden">
        {/* Radar Concentric Rings */}
        <div className="absolute inset-1 rounded-full border border-[#D4AF37]/40" />
        <div className="absolute inset-2.5 rounded-full border border-[#D4AF37]/25" />
        
        {/* Rotating Radar Sweep */}
        <div 
          className="absolute inset-0 rounded-full animate-radar-sweep"
          style={{
            background: 'conic-gradient(from 0deg, transparent 65%, rgba(212, 175, 55, 0.75) 100%)'
          }}
        />

        {/* Center Pulsing Dot */}
        <div 
          className={`w-2 h-2 rounded-full shadow-sm z-10 animate-radar-pulse ${
            isCompliant ? 'bg-[#00E676] shadow-[#00E676]' : 'bg-[#D4AF37] shadow-[#D4AF37]'
          }`} 
        />
      </div>

      <div className="flex flex-col">
        <span className="text-[10px] tracking-wider uppercase font-semibold text-[#FCFBF9]">
          {label}
        </span>
        <span className="text-[9px] text-[#C5A059] font-mono tracking-tight">
          FREQUENCY: 120 HZ
        </span>
      </div>
    </div>
  );
};
