import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Code, ChevronDown, ChevronUp, AlertCircle,
  ArrowRight, CheckCircle2, XCircle, MinusCircle, Building2, Info } from 'lucide-react';
import { AspectScoreChart, ViabilityProgressChart, AspectRadarChart, DistributionScatterChart } from './CustomCharts';
import MarketGapsPanel from './MarketGapsPanel';

const LOW_CONF = 0.4;   // below this, the estimate is unreliable (warn)
const NO_PREDICT = 0.2; // below this, don't show a prediction at all

/* Collapsible drill-in section: keeps the deep analysis off the first screen but
   one click away, so the page reads clean while nothing is removed. */
function Section({ title, subtitle, defaultOpen = false, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={styles.section}>
      <button style={styles.sectionHeader} onClick={() => setOpen(o => !o)}>
        <div style={styles.sectionHeaderText}>
          <span style={styles.sectionTitle}>{title}</span>
          {subtitle && <span style={styles.sectionSub}>{subtitle}</span>}
        </div>
        {open ? <ChevronUp size={18} color="var(--text-muted)" />
              : <ChevronDown size={18} color="var(--text-muted)" />}
      </button>
      {open && <div style={styles.sectionBody}>{children}</div>}
    </div>
  );
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  const color = value >= LOW_CONF ? 'var(--success)' : 'var(--warning)';
  return (
    <div style={styles.confBarWrap}>
      <div style={styles.confBarTrack}>
        <div style={{ ...styles.confBarFill, width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span style={{ ...styles.confBarPct, color }}>{pct}%</span>
    </div>
  );
}

export default function PredictorResults({ result, categoryProfile, hoveredAspect, setHoveredAspect, previewImpact, setPreviewImpact }) {
  const [showRawJson, setShowRawJson] = useState(false);
  if (!result) return null;

  // ---- Requirement 3: input was refused before any prediction ----
  if (result.refused) {
    return (
      <div style={styles.refusalPanel} className="animate-fade-in">
        <AlertCircle size={46} color="var(--warning)" />
        <h3 style={styles.refusalTitle}>Need more product detail</h3>
        <p style={styles.refusalReason}>{result.reason}</p>
        {result.suggestions?.length > 0 && (
          <ul style={styles.refusalList}>
            {result.suggestions.map((s, i) => <li key={i} style={styles.refusalItem}>{s}</li>)}
          </ul>
        )}
        <div style={styles.refusalMeta}>
          {result.signals ?? 0} of {result.required} meaningful details provided
        </div>
      </div>
    );
  }

  const viability = result.viability_pct;
  const percentile = result.retro_percentile;
  const confidence = result.confidence;
  const isLowConfidence = confidence < LOW_CONF;
  const suppressPrediction = confidence < NO_PREDICT;
  const groundedCount = Math.round((result.grounded_frac ?? 1) * 9);
  const successThreshold = result.success_threshold_p75;
  const maturity = result.maturity || {};

  // ---- post-bridging suppression (second, independent gate) ----
  if (suppressPrediction) {
    return (
      <div style={styles.refusalPanel}>
        <AlertCircle size={46} color="var(--warning)" />
        <h3 style={styles.refusalTitle}>Not enough detail to predict</h3>
        <p style={styles.refusalReason}>
          Your specification described only <strong>{groundedCount} of 9</strong> product
          aspects with concrete evidence — too little for a meaningful estimate. Rather than
          show a score that would just reflect <strong>category averages</strong>, we're
          holding the prediction.
        </p>
        <p style={styles.refusalReason}>
          Describe the product properly — build materials, key features, battery/performance,
          reliability, warranty — then use <strong>Review my spec</strong> and run again.
        </p>
        <div style={styles.refusalMeta}>
          Bridging confidence {confidence.toFixed(2)} · below the {NO_PREDICT.toFixed(2)} minimum
        </div>
      </div>
    );
  }

  // ---- verdict ----
  const isViable = viability >= successThreshold;
  const isBorderline = !isViable && viability >= successThreshold * 0.85;
  const verdict = isViable ? 'Viable' : (isBorderline ? 'Borderline' : 'Not Viable');
  const verdictColor = isViable ? 'var(--success)' : (isBorderline ? 'var(--warning)' : 'var(--danger)');
  const verdictMuted = isViable ? 'var(--success-muted)' : (isBorderline ? 'var(--warning-muted)' : 'var(--danger-muted)');
  const VerdictIcon = isViable ? CheckCircle2 : (isBorderline ? MinusCircle : XCircle);

  const getTrustBadgeColor = (trust) => {
    if (trust === 'STRONG') return { backgroundColor: 'var(--success-muted)', color: 'var(--success)' };
    if (trust === 'MODERATE') return { backgroundColor: 'var(--warning-muted)', color: 'var(--warning)' };
    if (trust === 'WEAK' || (trust || '').startsWith('LOW')) return { backgroundColor: 'var(--danger-muted)', color: 'var(--danger)' };
    return { backgroundColor: 'var(--border)', color: 'var(--text-secondary)' };
  };

  return (
    <div style={styles.container} className="animate-fade-in">

      {/* ===== HEADLINE VERDICT ===== */}
      <div style={{ ...styles.verdictCard, borderColor: verdictColor, background: verdictMuted }}>
        <div style={styles.verdictLeft}>
          <div style={styles.verdictBadgeRow}>
            <VerdictIcon size={22} color={verdictColor} />
            <span style={{ ...styles.verdictLabel, color: verdictColor }}>{verdict}</span>
          </div>
          <div style={styles.verdictScoreRow}>
            <span style={styles.verdictScore}>{viability.toFixed(0)}</span>
            <span style={styles.verdictScoreUnit}>/ 100 viability</span>
          </div>
          <p style={styles.verdictHint}>
            Category success threshold is {successThreshold?.toFixed(0)}.
            {percentile != null && ` Beats ${Math.round(percentile)}% of real launched products.`}
          </p>
        </div>
        <div style={styles.verdictRight}>
          <span style={styles.verdictConfLabel}>Confidence</span>
          <ConfidenceBar value={confidence} />
          <span style={styles.verdictConfSub}>
            {isLowConfidence ? `Low — only ${groundedCount}/9 aspects grounded` : `${groundedCount}/9 aspects grounded`}
          </span>
        </div>
      </div>

      {/* ===== MATURITY NOTE (Requirement 2) ===== */}
      {maturity.applied && maturity.notes?.length > 0 && (
        <div style={styles.maturityBanner}>
          <Building2 size={18} color="var(--info)" />
          <div style={styles.bannerTextContainer}>
            <h4 style={styles.maturityTitle}>Maturity adjustment applied</h4>
            {maturity.notes.map((n, i) => <p key={i} style={styles.bannerDesc}>{n}</p>)}
            {Object.keys(maturity.adjusted_aspects || {}).length > 0 && (
              <div style={styles.chipRow}>
                {Object.entries(maturity.adjusted_aspects).map(([a, v]) => (
                  <span key={a} style={styles.maturityChip}>
                    {a.replace(/_/g, ' ')} {v.before}→{v.after}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ===== LOW-CONFIDENCE WARNING ===== */}
      {isLowConfidence && (
        <div style={styles.warningBanner}>
          <AlertCircle size={18} color="var(--warning)" />
          <div style={styles.bannerTextContainer}>
            <h4 style={styles.bannerTitle}>Low-confidence estimate — indicative only</h4>
            <p style={styles.bannerDesc}>
              Only {groundedCount} of 9 aspects were backed by concrete evidence, so this
              leans on <strong>category averages</strong> rather than your actual product.
              Add detail via the <strong>Spec Coach</strong> and re-run.
            </p>
          </div>
        </div>
      )}

      {/* ===== KEY FACTORS (always visible, scannable chips) ===== */}
      <div style={styles.factorsGrid}>
        <div style={styles.factorCol}>
          <div style={styles.factorHead}>
            <ShieldCheck size={15} color="var(--success)" />
            <span style={styles.factorTitle}>Raises viability</span>
          </div>
          <div style={styles.chipRow}>
            {result.top_strengths?.length ? result.top_strengths.map((s, i) => (
              <span key={i} style={{ ...styles.factorChip, ...styles.factorChipPos }}
                title={s.reasoning}>
                {s.feature.replace(/_mention_rate/g, ' freq').replace(/_/g, ' ')}
                <b style={styles.chipVal}>+{s.impact.toFixed(1)}</b>
              </span>
            )) : <span style={styles.noneText}>None identified</span>}
          </div>
        </div>
        <div style={styles.factorCol}>
          <div style={styles.factorHead}>
            <ShieldAlert size={15} color="var(--danger)" />
            <span style={styles.factorTitle}>Lowers viability</span>
          </div>
          <div style={styles.chipRow}>
            {result.top_risks?.length ? result.top_risks.map((r, i) => (
              <span key={i} style={{ ...styles.factorChip, ...styles.factorChipNeg }}
                title={r.reasoning}>
                {r.feature.replace(/_mention_rate/g, ' freq').replace(/_/g, ' ')}
                <b style={styles.chipVal}>{r.impact.toFixed(1)}</b>
              </span>
            )) : <span style={styles.noneText}>None identified</span>}
          </div>
        </div>
      </div>

      {/* ===== DRILL-IN SECTIONS (collapsed by default) ===== */}
      <Section title="Viability & aspect scores"
        subtitle="How the estimate compares to the category threshold and averages"
        defaultOpen>
        <div style={styles.vizGrid}>
          <ViabilityProgressChart viability={viability} threshold={successThreshold} previewImpact={previewImpact} />
          <AspectScoreChart data={result.bridged_scores}
            categoryAvg={categoryProfile?.avg_aspect_scores || {}}
            hoveredAspect={hoveredAspect} setHoveredAspect={setHoveredAspect} />
        </div>
      </Section>

      <Section title="Aspect radar & market positioning"
        subtitle="Your design profile vs the category, and its price/viability position">
        <div style={styles.vizGrid}>
          <AspectRadarChart data={result.bridged_scores}
            categoryAvg={categoryProfile?.avg_aspect_scores || {}}
            hoveredAspect={hoveredAspect} setHoveredAspect={setHoveredAspect} />
          <DistributionScatterChart
            currentProduct={{ price: result.price || 49.99, viability }}
            categoryProducts={result.category_products} />
        </div>
      </Section>

      <Section title="Explainability path map"
        subtitle="Trace how a spec detail propagates to the score">
        <div style={styles.flowMapNodes}>
          {[
            ['Specification Text', hoveredAspect ? `"${hoveredAspect.replace(/_/g, ' ')}"` : 'Select an aspect'],
            ['LLM Aspect Bridging', hoveredAspect && result.bridged_scores[hoveredAspect] ? `${result.bridged_scores[hoveredAspect].score.toFixed(1)} / 10` : 'Bridged score'],
            ['XGBoost Weight', (() => {
              if (!hoveredAspect) return 'SHAP contribution';
              const risk = result.top_risks?.find(r => r.feature === hoveredAspect || r.feature === `${hoveredAspect}_mention_rate`);
              const strength = result.top_strengths?.find(s => s.feature === hoveredAspect || s.feature === `${hoveredAspect}_mention_rate`);
              if (risk) return `${risk.impact.toFixed(2)} risk`;
              if (strength) return `+${strength.impact.toFixed(2)} strength`;
              return 'Neutral';
            })()],
            ['Viability', `${viability.toFixed(1)}%`],
          ].map(([label, val], i, arr) => (
            <React.Fragment key={label}>
              <div style={{ ...styles.flowNode, borderColor: hoveredAspect ? 'var(--accent)' : 'var(--border)' }}>
                <span style={styles.flowNodeLabel}>{label}</span>
                <span style={styles.flowNodeVal}>{val}</span>
              </div>
              {i < arr.length - 1 && <ArrowRight size={16} color={hoveredAspect ? 'var(--accent)' : 'var(--text-muted)'} />}
            </React.Fragment>
          ))}
        </div>
      </Section>

      <Section title="What moves the score (SHAP)"
        subtitle="Aspects the model weighs for and against your predicted score">
        <div style={styles.shapGrid}>
          <div style={styles.shapPanel}>
            <div style={styles.shapHeader}>
              <ShieldAlert size={16} color="var(--danger)" />
              <h3 style={styles.shapTitle}>Lowering viability ↓</h3>
            </div>
            <div style={styles.shapList}>
              {result.top_risks?.map((risk, idx) => (
                <div key={idx} style={styles.shapItem}
                  onMouseEnter={() => setHoveredAspect?.(risk.feature.replace(/_mention_rate/g, ''))}
                  onMouseLeave={() => setHoveredAspect?.(null)}>
                  <div style={styles.shapMeta}>
                    <span style={styles.shapName}>{risk.feature.replace(/_mention_rate/g, ' frequency').replace(/_/g, ' ')}</span>
                    <span style={styles.shapImpactNeg}>{risk.impact.toFixed(2)}</span>
                  </div>
                  {risk.reasoning && <p style={styles.shapReason}>{risk.reasoning}</p>}
                </div>
              ))}
            </div>
          </div>
          <div style={styles.shapPanel}>
            <div style={styles.shapHeader}>
              <ShieldCheck size={16} color="var(--success)" />
              <h3 style={styles.shapTitle}>Raising viability ↑</h3>
            </div>
            <div style={styles.shapList}>
              {result.top_strengths?.map((strength, idx) => (
                <div key={idx} style={styles.shapItem}
                  onMouseEnter={() => setHoveredAspect?.(strength.feature.replace(/_mention_rate/g, ''))}
                  onMouseLeave={() => setHoveredAspect?.(null)}>
                  <div style={styles.shapMeta}>
                    <span style={styles.shapName}>{strength.feature.replace(/_mention_rate/g, ' frequency').replace(/_/g, ' ')}</span>
                    <span style={styles.shapImpactPos}>+{strength.impact.toFixed(2)}</span>
                  </div>
                  {strength.reasoning && <p style={styles.shapReason}>{strength.reasoning}</p>}
                </div>
              ))}
            </div>
          </div>
        </div>
      </Section>

      <Section title="Bridged aspect score sheet"
        subtitle="Every aspect, its evidence basis, and validation trust">
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr style={styles.tr}>
                <th style={styles.th}>Aspect</th>
                <th style={styles.th}>Score</th>
                <th style={styles.th}>Evidence</th>
                <th style={styles.th}>Trust</th>
                <th style={styles.th}>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result.bridged_scores || {}).map(([aspect, val]) => {
                const catAvg = categoryProfile?.avg_aspect_scores?.[aspect];
                const belowAvg = catAvg != null && val.score < catAvg;
                return (
                <tr key={aspect} style={styles.trHover}
                  onMouseEnter={() => setHoveredAspect?.(aspect)}
                  onMouseLeave={() => setHoveredAspect?.(null)}>
                  <td style={{ ...styles.td, fontWeight: 600 }}>
                    {aspect.replace(/_/g, ' ')}
                    {val.maturity_adjusted && <span style={styles.adjTag}>adjusted</span>}
                  </td>
                  <td style={styles.td}>
                    <span style={{ ...styles.scorePill,
                      backgroundColor: catAvg == null ? 'var(--border)' : (belowAvg ? 'var(--danger-muted)' : 'var(--success-muted)'),
                      color: catAvg == null ? 'var(--text-secondary)' : (belowAvg ? 'var(--danger)' : 'var(--success)') }}>
                      {val.score.toFixed(1)}
                      {catAvg != null && <span style={styles.scorePillAvg}>{belowAvg ? '▼' : '▲'} avg {catAvg.toFixed(1)}</span>}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <span style={val.grounded ? styles.evidenceSpec : styles.evidenceNone}>
                      {val.grounded ? '📄 spec' : '⚪ none'}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <span style={{ ...styles.trustBadge, ...getTrustBadgeColor(val.trust) }}>{val.trust}</span>
                  </td>
                  <td style={{ ...styles.td, color: 'var(--text-secondary)', fontSize: '13px' }}>{val.reasoning}</td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Section>

      {result.market_gaps?.length > 0 && (
        <Section title="Unaddressed market gaps"
          subtitle={`${result.market_gaps.length} category pain point(s) your design doesn't clearly solve`}>
          <MarketGapsPanel gaps={result.market_gaps} hoveredAspect={hoveredAspect} setHoveredAspect={setHoveredAspect} />
        </Section>
      )}

      {/* ===== SCOPE CAVEAT ===== */}
      <div style={styles.honestyBanner}>
        <Info size={18} color="var(--text-muted)" style={{ flexShrink: 0, marginTop: 2 }} />
        <p style={styles.honestyDesc}>
          This scores product-design viability against historical consumer sentiment. It does
          <strong> not</strong> forecast sales or revenue — it has no visibility into marketing
          spend, manufacturing, distribution, or support quality.
        </p>
      </div>

      {/* ===== RAW JSON ===== */}
      <div style={styles.rawJsonSection}>
        <div onClick={() => setShowRawJson(!showRawJson)} style={styles.rawJsonTrigger}>
          <Code size={14} />
          <span>Raw prediction output (JSON)</span>
          {showRawJson ? <ChevronUp size={14} style={{ marginLeft: 'auto' }} /> : <ChevronDown size={14} style={{ marginLeft: 'auto' }} />}
        </div>
        {showRawJson && (
          <pre style={styles.rawJsonCode}><code>{JSON.stringify(result, null, 2)}</code></pre>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '28px',
    width: '100%',
  },

  /* refusal / suppression */
  refusalPanel: {
    display: 'flex', flexDirection: 'column', alignItems: 'center',
    justifyContent: 'center', textAlign: 'center', padding: '64px 24px',
    gap: '16px', minHeight: '420px',
  },
  refusalTitle: { fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 },
  refusalReason: { fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '480px', lineHeight: 1.6, margin: 0 },
  refusalList: { textAlign: 'left', maxWidth: '480px', margin: 0, paddingLeft: '20px',
    display: 'flex', flexDirection: 'column', gap: '8px', color: 'var(--text-secondary)', fontSize: '13.5px', lineHeight: 1.5 },
  refusalItem: { paddingLeft: '4px' },
  refusalMeta: { marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)' },

  /* verdict hero */
  verdictCard: {
    display: 'flex', justifyContent: 'space-between', gap: '32px',
    border: '1px solid', borderRadius: 'var(--radius-lg)', padding: '28px 32px',
    boxShadow: 'var(--shadow-sm)', flexWrap: 'wrap',
  },
  verdictLeft: { display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '220px' },
  verdictBadgeRow: { display: 'flex', alignItems: 'center', gap: '8px' },
  verdictLabel: { fontSize: '15px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' },
  verdictScoreRow: { display: 'flex', alignItems: 'baseline', gap: '8px' },
  verdictScore: { fontSize: '52px', fontWeight: 800, fontFamily: 'var(--font-heading)', lineHeight: 1, color: 'var(--text-primary)' },
  verdictScoreUnit: { fontSize: '14px', color: 'var(--text-muted)', fontWeight: 500 },
  verdictHint: { fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0, maxWidth: '360px' },
  verdictRight: { display: 'flex', flexDirection: 'column', gap: '8px', justifyContent: 'center', minWidth: '200px' },
  verdictConfLabel: { fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' },
  verdictConfSub: { fontSize: '12px', color: 'var(--text-secondary)' },

  confBarWrap: { display: 'flex', alignItems: 'center', gap: '10px' },
  confBarTrack: { flex: 1, height: '8px', borderRadius: '4px', backgroundColor: 'var(--bg-input)', overflow: 'hidden' },
  confBarFill: { height: '100%', borderRadius: '4px', transition: 'width 400ms ease-out' },
  confBarPct: { fontSize: '15px', fontWeight: 700, fontFamily: 'var(--font-heading)', minWidth: '42px', textAlign: 'right' },

  /* banners */
  maturityBanner: {
    display: 'flex', gap: '14px', backgroundColor: 'var(--info-muted)',
    border: '1px solid var(--info)', borderRadius: 'var(--radius-sm)', padding: '16px 20px', alignItems: 'flex-start',
  },
  maturityTitle: { fontSize: '14px', fontWeight: 600, color: 'var(--info)' },
  warningBanner: {
    display: 'flex', gap: '14px', backgroundColor: 'var(--warning-muted)',
    border: '1px solid var(--warning)', borderRadius: 'var(--radius-sm)', padding: '16px 20px', alignItems: 'flex-start',
  },
  bannerTextContainer: { display: 'flex', flexDirection: 'column', gap: '6px' },
  bannerTitle: { fontSize: '14px', fontWeight: 600, color: 'var(--warning)' },
  bannerDesc: { fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5, margin: 0 },

  /* key factors */
  factorsGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px',
    '@media (max-width: 768px)': { gridTemplateColumns: '1fr' },
  },
  factorCol: { display: 'flex', flexDirection: 'column', gap: '10px' },
  factorHead: { display: 'flex', alignItems: 'center', gap: '6px' },
  factorTitle: { fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' },
  chipRow: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  factorChip: {
    display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500,
    padding: '5px 10px', borderRadius: '14px', textTransform: 'capitalize', border: '1px solid transparent',
  },
  factorChipPos: { backgroundColor: 'var(--success-muted)', color: 'var(--success)' },
  factorChipNeg: { backgroundColor: 'var(--danger-muted)', color: 'var(--danger)' },
  chipVal: { fontWeight: 700 },
  noneText: { fontSize: '12.5px', color: 'var(--text-muted)' },
  maturityChip: {
    display: 'inline-flex', alignItems: 'center', fontSize: '11px', fontWeight: 600,
    padding: '3px 8px', borderRadius: '12px', textTransform: 'capitalize',
    backgroundColor: 'var(--bg-input)', border: '1px solid var(--border)', color: 'var(--text-secondary)',
  },

  /* collapsible sections */
  section: {
    border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
    backgroundColor: 'var(--bg-panel)', boxShadow: 'var(--shadow-sm)', overflow: 'hidden',
  },
  sectionHeader: {
    width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    background: 'none', border: 'none', borderRadius: 0, padding: '18px 24px', cursor: 'pointer', textAlign: 'left',
  },
  sectionHeaderText: { display: 'flex', flexDirection: 'column', gap: '3px' },
  sectionTitle: { fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)' },
  sectionSub: { fontSize: '12px', color: 'var(--text-muted)' },
  sectionBody: { padding: '4px 24px 24px', display: 'flex', flexDirection: 'column', gap: '24px' },

  vizGrid: {
    display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px',
    '@media (max-width: 1024px)': { gridTemplateColumns: '1fr' },
  },

  /* flow map */
  flowMapNodes: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px',
    '@media (max-width: 768px)': { flexDirection: 'column', gap: '16px' },
  },
  flowNode: {
    backgroundColor: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
    padding: '12px', flex: 1, display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center',
    textAlign: 'center', transition: 'all 250ms ease-out', minWidth: '120px',
  },
  flowNodeLabel: { fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 },
  flowNodeVal: { fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' },

  /* shap */
  shapGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px',
    '@media (max-width: 768px)': { gridTemplateColumns: '1fr' },
  },
  shapPanel: { display: 'flex', flexDirection: 'column', gap: '12px' },
  shapHeader: { display: 'flex', alignItems: 'center', gap: '8px' },
  shapTitle: { fontSize: '15px', fontWeight: 600 },
  shapList: { display: 'flex', flexDirection: 'column', gap: '12px' },
  shapItem: {
    backgroundColor: 'var(--bg-input)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
    padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '6px',
  },
  shapMeta: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  shapName: { fontSize: '13px', fontWeight: 600, textTransform: 'capitalize' },
  shapImpactNeg: { color: 'var(--danger)', fontWeight: 600, fontSize: '12px' },
  shapImpactPos: { color: 'var(--success)', fontWeight: 600, fontSize: '12px' },
  shapReason: { fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4, margin: 0 },

  /* table */
  tableWrapper: { overflowX: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse', textAlign: 'left' },
  tr: { borderBottom: '1px solid var(--border)' },
  trHover: { borderBottom: '1px solid var(--border)' },
  th: { fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '10px 14px' },
  td: { padding: '12px 14px', fontSize: '13px', color: 'var(--text-primary)', verticalAlign: 'top' },
  adjTag: {
    marginLeft: '6px', fontSize: '9px', fontWeight: 700, textTransform: 'uppercase',
    color: 'var(--info)', backgroundColor: 'var(--info-muted)', padding: '1px 5px', borderRadius: '6px',
  },
  evidenceSpec: { backgroundColor: 'var(--accent-muted)', color: 'var(--accent)', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 500 },
  evidenceNone: { backgroundColor: 'var(--border)', color: 'var(--text-muted)', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 500 },
  trustBadge: { padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600, whiteSpace: 'nowrap' },
  scorePill: { display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '2px 8px', borderRadius: '12px', fontSize: '12px', fontWeight: 700, whiteSpace: 'nowrap' },
  scorePillAvg: { fontSize: '10px', fontWeight: 600, opacity: 0.85 },

  /* caveat + raw json */
  honestyBanner: {
    backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
    padding: '16px 20px', display: 'flex', gap: '12px', alignItems: 'flex-start',
  },
  honestyDesc: { fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 },
  rawJsonSection: { border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' },
  rawJsonTrigger: {
    backgroundColor: 'var(--bg-panel)', padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '8px',
    cursor: 'pointer', fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', userSelect: 'none',
  },
  rawJsonCode: {
    backgroundColor: 'var(--bg-input)', borderTop: '1px solid var(--border)', padding: '20px',
    fontFamily: 'monospace', fontSize: '12px', overflowX: 'auto', maxHeight: '300px', color: 'var(--text-primary)',
  },
};
