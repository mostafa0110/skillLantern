// Original SkillLantern practice composition. Reuse and adapt freely.
import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame} from 'remotion';

export const HeroLoop: React.FC = () => {
  const frame = useCurrentFrame();
  // Exactly one cycle in 90 frames. Frame 90 would match frame 0.
  const phase = (frame / 90) * Math.PI * 2;
  const glow = 0.32 + Math.sin(phase) * 0.07;
  return (
    <AbsoluteFill style={{background: '#17291f', overflow: 'hidden', fontFamily: 'Arial, sans-serif', color: '#fff9e9'}}>
      <div style={{position: 'absolute', width: 650, height: 650, right: -120, top: -160, borderRadius: '50%', background: '#d4a24b', opacity: glow, filter: 'blur(85px)'}} />
      <div style={{position: 'absolute', left: 84, top: 79, fontSize: 18, letterSpacing: 5, color: '#d9b978'}}>A SMALL CREATIVE PRACTICE</div>
      <div style={{position: 'absolute', left: 80, top: 202, fontSize: 88, fontWeight: 600, lineHeight: 1.08, letterSpacing: -4}}>Make room for<br /><span style={{color: '#e6bd73'}}>a clearer idea.</span></div>
      <div style={{position: 'absolute', left: 86, bottom: 115, fontSize: 22, color: '#c1cdbd'}}>One brief. A little structure. Your next move.</div>
      {[0, 1, 2].map((i) => {
        const a = phase + i * Math.PI * 2 / 3;
        return <div key={i} style={{position: 'absolute', right: 144 + Math.cos(a) * 46, top: 258 + i * 94 + Math.sin(a) * 14, width: 184, padding: '20px 24px', borderRadius: 16, border: '1px solid #7f9273', background: '#294432', transform: `rotate(${Math.sin(a) * 3}deg)`, fontSize: 24, boxShadow: '0 12px 32px #0b191b33'}}><span style={{color: '#e6bd73', marginRight: 18}}>0{i + 1}</span>{['Plan', 'Draft', 'Refine'][i]}</div>;
      })}
      <div style={{position: 'absolute', left: 84, right: 84, bottom: 56, height: 1, background: '#6b7e62'}} />
    </AbsoluteFill>
  );
};

const Root: React.FC = () => <Composition id="HeroLoop" component={HeroLoop} width={1280} height={720} fps={30} durationInFrames={90} />;
registerRoot(Root);
