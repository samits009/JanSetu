import React from 'react';

interface CinematicBackgroundProps {
  showBridgePath?: boolean;
  intensity?: 'high' | 'medium' | 'subtle';
}

export function CinematicBackground({ showBridgePath = true, intensity = 'high' }: CinematicBackgroundProps) {
  const opacityMap = {
    high: 0.92,
    medium: 0.72,
    subtle: 0.45,
  };

  return (
    <div className="cinematic-bg-container" aria-hidden="true">
      {/* 1. Deep Atmospheric Sky Base with Sunset/Dawn Horizon Glow */}
      <div className="cinematic-sky-gradient" />

      {/* 2. Vector Silhouetted Heritage Landscape & Bridge */}
      <svg
        className="cinematic-scene-svg"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
        style={{ opacity: opacityMap[intensity] }}
      >
        <defs>
          {/* Luminous Warm Golden Setu Path Gradient */}
          <linearGradient id="setuGoldGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FDE68A" stopOpacity="0.85" />
            <stop offset="35%" stopColor="#F5C77C" stopOpacity="0.9" />
            <stop offset="70%" stopColor="#D97706" stopOpacity="0.65" />
            <stop offset="100%" stopColor="#B45309" stopOpacity="0.3" />
          </linearGradient>

          {/* River Water Reflection Gradient */}
          <linearGradient id="riverReflection" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#D97706" stopOpacity="0.18" />
            <stop offset="50%" stopColor="#0B132B" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#050811" stopOpacity="0.98" />
          </linearGradient>

          {/* Mist / Fog Overlay Gradient */}
          <linearGradient id="mistOverlay" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#070B16" stopOpacity="0" />
            <stop offset="50%" stopColor="#F59E0B" stopOpacity="0.06" />
            <stop offset="100%" stopColor="#070B16" stopOpacity="0.85" />
          </linearGradient>

          {/* Radial Warm Golden Sun Glow */}
          <radialGradient id="sunHorizonGlow" cx="65%" cy="38%" r="48%">
            <stop offset="0%" stopColor="#FDE047" stopOpacity="0.28" />
            <stop offset="30%" stopColor="#F59E0B" stopOpacity="0.18" />
            <stop offset="65%" stopColor="#92400E" stopOpacity="0.07" />
            <stop offset="100%" stopColor="#070B16" stopOpacity="0" />
          </radialGradient>

          {/* Soft Golden Path Glow Filter */}
          <filter id="luminousGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur1" />
            <feGaussianBlur stdDeviation="12" result="blur2" />
            <feMerge>
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Atmospheric Radial Sun/Horizon Flare */}
        <rect x="0" y="0" width="1440" height="900" fill="url(#sunHorizonGlow)" />

        {/* Distant Architecture Silhouettes (Stately domes, minarets, temples in golden mist) */}
        <g className="distant-monuments" opacity="0.45" fill="#1C1824">
          {/* Main Central High Dome */}
          <path d="M 850,330 C 850,290 875,270 890,250 C 905,270 930,290 930,330 Z" />
          <path d="M 888,250 L 892,250 L 890,230 Z" /> {/* Finial tip */}
          <rect x="840" y="330" width="100" height="70" />
          {/* Side Pavilion Towers */}
          <path d="M 800,320 C 800,300 812,290 820,280 C 828,290 840,300 840,320 Z" />
          <rect x="806" y="320" width="28" height="80" />
          <path d="M 940,320 C 940,300 952,290 960,280 C 968,290 980,300 980,320 Z" />
          <rect x="946" y="320" width="28" height="80" />

          {/* Distant skyline towers on far right */}
          <path d="M 1120,340 C 1120,310 1135,295 1145,280 C 1155,295 1170,310 1170,340 Z" />
          <rect x="1132" y="340" width="26" height="60" />
          <rect x="1050" y="360" width="200" height="50" opacity="0.5" />
        </g>

        {/* Midground Grand Arched Indian Stone Bridge (JanSetu Sovereign Bridge Metaphor) */}
        <g className="heritage-bridge" fill="#111625">
          {/* Bridge Roadway Deck */}
          <path d="M -50,390 L 1500,380 L 1500,410 L -50,418 Z" opacity="0.9" />
          <line x1="-50" y1="388" x2="1500" y2="378" stroke="#F5C77C" strokeOpacity="0.35" strokeWidth="1.5" />

          {/* Repeating Symmetrical Bridge Arches across River */}
          <path d="M 120,414 Q 180,360 240,413 L 260,413 L 260,520 L 100,520 L 100,414 Z" />
          <path d="M 280,413 Q 345,355 410,412 L 430,412 L 430,520 L 260,520 L 260,413 Z" />
          <path d="M 450,412 Q 520,350 590,411 L 610,411 L 610,520 L 430,520 L 430,412 Z" />
          <path d="M 630,411 Q 705,348 780,410 L 800,410 L 800,520 L 610,520 L 610,411 Z" />
          <path d="M 820,410 Q 900,345 980,409 L 1000,409 L 1000,520 L 800,520 L 800,410 Z" />
          <path d="M 1020,409 Q 1100,344 1180,408 L 1200,408 L 1200,520 L 1000,520 L 1000,409 Z" />
          <path d="M 1220,408 Q 1300,342 1380,407 L 1490,407 L 1490,520 L 1200,520 L 1200,408 Z" />

          {/* Pier Foundations & Lamps */}
          <circle cx="260" cy="385" r="2.5" fill="#FDE68A" opacity="0.75" />
          <circle cx="430" cy="384" r="2.5" fill="#FDE68A" opacity="0.75" />
          <circle cx="610" cy="383" r="2.5" fill="#FDE68A" opacity="0.75" />
          <circle cx="800" cy="382" r="2.5" fill="#FDE68A" opacity="0.75" />
          <circle cx="1000" cy="381" r="2.5" fill="#FDE68A" opacity="0.75" />
          <circle cx="1200" cy="380" r="2.5" fill="#FDE68A" opacity="0.75" />
        </g>

        {/* River Water Surface with Golden Reflection */}
        <rect x="0" y="470" width="1440" height="430" fill="url(#riverReflection)" />

        {/* Misty Atmosphere overlay across water */}
        <rect x="0" y="380" width="1440" height="240" fill="url(#mistOverlay)" />

        {/* Foreground Silhouetted Foliage (Soft riverbank trees framing edges) */}
        <g className="foreground-silhouettes" fill="#060A14" opacity="0.88">
          <path d="M -30,900 L -30,620 C 10,610 30,590 50,620 C 70,580 110,590 120,630 C 140,610 170,620 180,660 C 200,640 230,670 230,720 L 250,900 Z" />
          <path d="M 1240,900 L 1250,710 C 1270,660 1300,650 1320,680 C 1340,630 1390,640 1410,690 C 1430,660 1460,670 1480,900 Z" />
        </g>

        {/* 3. The Signature Setu Bridge Path Motif (Starting Point → Bridge Connection → Welfare Destination) */}
        {showBridgePath && (
          <g className="jansetu-bridge-path-group">
            {/* Luminous Glow Ribbon Underneath */}
            <path
              d="M -60,320 C 260,280 480,480 820,380 C 1120,290 1320,540 1520,440"
              fill="none"
              stroke="#F5C77C"
              strokeWidth="6"
              strokeOpacity="0.18"
              filter="url(#luminousGlow)"
            />

            {/* Core Delicate Luminous Bridge Path */}
            <path
              d="M -60,320 C 260,280 480,480 820,380 C 1120,290 1320,540 1520,440"
              fill="none"
              stroke="url(#setuGoldGlow)"
              strokeWidth="1.8"
              strokeLinecap="round"
              className="jansetu-bridge-path-draw"
            />

            {/* Subtle Secondary Guide Echo Path */}
            <path
              d="M -80,480 C 240,560 620,340 1020,490 C 1240,580 1420,400 1540,430"
              fill="none"
              stroke="#F59E0B"
              strokeWidth="1.2"
              strokeOpacity="0.25"
              strokeDasharray="4 8"
            />

            {/* Warm Constellation Nodes (Citizen -> Evidence -> Scheme -> Action) */}
            <g className="path-nodes">
              <circle cx="280" cy="340" r="4" fill="#FDE68A" filter="url(#luminousGlow)" />
              <circle cx="280" cy="340" r="2" fill="#FFFFFF" />

              <circle cx="620" cy="440" r="4.5" fill="#F59E0B" filter="url(#luminousGlow)" />
              <circle cx="620" cy="440" r="2" fill="#FFFFFF" />

              <circle cx="980" cy="350" r="4" fill="#FDE68A" filter="url(#luminousGlow)" />
              <circle cx="980" cy="350" r="2" fill="#FFFFFF" />

              <circle cx="1280" cy="470" r="5" fill="#F5C77C" filter="url(#luminousGlow)" />
              <circle cx="1280" cy="470" r="2.5" fill="#FFFFFF" />
            </g>
          </g>
        )}
      </svg>

      {/* 4. Ambient Floating Bokeh / Stardust Particles */}
      <div className="cinematic-bokeh-layer">
        <span className="bokeh-particle bp-1" />
        <span className="bokeh-particle bp-2" />
        <span className="bokeh-particle bp-3" />
        <span className="bokeh-particle bp-4" />
        <span className="bokeh-particle bp-5" />
      </div>

      {/* 5. Cinematic Vignette (Soft dark border framing) */}
      <div className="cinematic-vignette" />
    </div>
  );
}
