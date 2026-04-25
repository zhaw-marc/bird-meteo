import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.sidebar import render_sidebar

st.set_page_config(page_title="Bird & Weather Explorer", layout="wide")

filters = render_sidebar()

st.markdown("""
<style>
/* ── Hero ────────────────────────────────────────────────── */
.bw-hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(-45deg, #0a1628, #1b3a5c, #0c3d2e, #12334a);
    background-size: 400% 400%;
    animation: bwGrad 15s ease infinite;
    border-radius: 16px;
    padding: 5rem 2rem 4rem;
    text-align: center;
    color: white;
    margin-bottom: 2.5rem;
}
@keyframes bwGrad {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.bw-badge {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 20px;
    padding: 0.28rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
    animation: bwUp 0.6s ease forwards;
    opacity: 0;
}
.bw-hero-title {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800;
    letter-spacing: -0.025em;
    line-height: 1.1;
    animation: bwUp 0.65s ease 0.15s forwards;
    opacity: 0;
}
.bw-hero-sub {
    margin-top: 0.8rem;
    font-size: 1.1rem;
    color: rgba(255,255,255,0.68);
    max-width: 560px;
    margin-left: auto;
    margin-right: auto;
    animation: bwUp 0.65s ease 0.3s forwards;
    opacity: 0;
}
@keyframes bwUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
/* Birds */
.bw-birds { position: absolute; inset: 0; pointer-events: none; }
.bw-bird { position: absolute; animation: bwFly linear infinite; opacity: 0; }
.bw-b1 { width: 48px; top: 18%; animation-duration: 17s; animation-delay:  0s; }
.bw-b2 { width: 30px; top: 40%; animation-duration: 23s; animation-delay:  5s; }
.bw-b3 { width: 56px; top: 12%; animation-duration: 20s; animation-delay: 10s; }
.bw-b4 { width: 26px; top: 65%; animation-duration: 14s; animation-delay:  2s; }
.bw-b5 { width: 42px; top: 78%; animation-duration: 26s; animation-delay:  7s; }
@keyframes bwFly {
    0%   { left: -80px; opacity: 0; }
    6%   { opacity: 1; }
    90%  { opacity: 1; }
    100% { left: calc(100% + 80px); opacity: 0; }
}

/* ── Feature cards ───────────────────────────────────────── */
.bw-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.bw-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-top: 3px solid #1d4ed8;
    border-radius: 10px;
    padding: 1.4rem 1.2rem;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.bw-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 30px rgba(0,0,0,0.09);
}
.bw-card-icon { color: #1d4ed8; margin-bottom: 0.55rem; }
.bw-card-title { font-weight: 700; font-size: 0.98rem; color: #0f172a; margin-bottom: 0.3rem; }
.bw-card-desc  { font-size: 0.81rem; color: #64748b; line-height: 1.55; }
</style>

<div class="bw-hero">
  <div class="bw-birds">
    <svg class="bw-bird bw-b1" viewBox="0 0 40 12">
      <path d="M0,6 Q10,0 20,6 Q30,0 40,6" stroke="rgba(255,255,255,0.55)" stroke-width="1.8" fill="none" stroke-linecap="round"/>
    </svg>
    <svg class="bw-bird bw-b2" viewBox="0 0 30 10">
      <path d="M0,5 Q7,0 15,5 Q23,0 30,5" stroke="rgba(255,255,255,0.38)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    </svg>
    <svg class="bw-bird bw-b3" viewBox="0 0 52 16">
      <path d="M0,8 Q13,0 26,8 Q39,0 52,8" stroke="rgba(255,255,255,0.48)" stroke-width="2" fill="none" stroke-linecap="round"/>
    </svg>
    <svg class="bw-bird bw-b4" viewBox="0 0 25 8">
      <path d="M0,4 Q6,0 12,4 Q18,0 25,4" stroke="rgba(255,255,255,0.30)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
    </svg>
    <svg class="bw-bird bw-b5" viewBox="0 0 44 14">
      <path d="M0,7 Q11,0 22,7 Q33,0 44,7" stroke="rgba(255,255,255,0.42)" stroke-width="1.8" fill="none" stroke-linecap="round"/>
    </svg>
  </div>
  <div>
    <div class="bw-badge">Switzerland &nbsp;·&nbsp; eBird &amp; Open-Meteo</div>
    <div class="bw-hero-title">Bird &amp; Weather Explorer</div>
    <div class="bw-hero-sub">Uncovering how Swiss weather shapes bird activity across cantons</div>
  </div>
</div>

<div class="bw-cards">
  <div class="bw-card">
    <div class="bw-card-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
      </svg>
    </div>
    <div class="bw-card-title">Map</div>
    <div class="bw-card-desc">Interactive heatmap of sighting hotspots across Switzerland.</div>
  </div>
  <div class="bw-card">
    <div class="bw-card-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/>
      </svg>
    </div>
    <div class="bw-card-title">Weather Impact</div>
    <div class="bw-card-desc">Pearson correlation between weather parameters and daily sighting counts.</div>
  </div>
  <div class="bw-card">
    <div class="bw-card-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="3" width="8" height="18" rx="2"/><rect x="14" y="3" width="8" height="18" rx="2"/>
      </svg>
    </div>
    <div class="bw-card-title">Compare Regions</div>
    <div class="bw-card-desc">Independent t-test comparing sighting rates between cantons or bounding boxes.</div>
  </div>
  <div class="bw-card">
    <div class="bw-card-icon">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/>
      </svg>
    </div>
    <div class="bw-card-title">Findings</div>
    <div class="bw-card-desc">AI-generated scientific summary of your results via Google Gemini.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.caption(f"Selected: {filters['species']}  ·  {filters['start_date']} – {filters['end_date']}")
