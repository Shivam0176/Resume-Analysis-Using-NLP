import { MatchResult } from "../api";
import { ComparisonPanel } from "./ComparisonPanel";
import { ScoreRing } from "./ScoreRing";
import { SkillsPanel } from "./SkillsPanel";

function MetricCard({ label, value, description, weight }: { label: string; value: number; description: string; weight?: string }) {
  return <article className="metric-card"><div className="metric-card-header"><span>{label}</span>{weight && <span className="weight-tag">{weight} WEIGHT</span>}</div><div className="metric-card-value">{Math.round(value)}<small>%</small></div><div className="metric-track"><span style={{ width: `${Math.max(0, Math.min(100, value))}%` }}/></div><p>{description}</p></article>;
}

function getStrengthLabel(result: MatchResult) {
  if (result.semantic_score === result.skill_score) return "Semantic similarity and skill coverage contribute equally to this score.";
  const strongest = result.semantic_score > result.skill_score ? "Semantic similarity" : "Skill coverage";
  const score = Math.max(result.semantic_score, result.skill_score);
  return `${strongest} is the strongest component at ${Math.round(score)}%.`;
}

function Recommendations({ result }: { result: MatchResult }) {
  const additional = result.resume_skills.filter((skill) => !result.job_skills.includes(skill));
  const strengths: string[] = [];
  if (result.matched_skills.length) strengths.push(`${result.matched_skills.length} role ${result.matched_skills.length === 1 ? "skill is" : "skills are"} also detected in your resume: ${result.matched_skills.join(", ")}.`);
  if (result.semantic_score > 0) strengths.push(`Semantic similarity is ${Math.round(result.semantic_score)}%, reflecting the model’s text-level comparison.`);
  if (additional.length) strengths.push(`Your resume also includes skills beyond this role’s detected list: ${additional.join(", ")}.`);

  const opportunities: string[] = [];
  if (result.missing_skills.length) opportunities.push(`Review whether your experience supports these role skills, and add relevant evidence where accurate: ${result.missing_skills.join(", ")}.`);
  result.feedback.forEach((message) => {
    if (!opportunities.includes(message) && !message.toLowerCase().startsWith("matched skills:") && !message.toLowerCase().startsWith("consider highlighting relevant experience with:")) opportunities.push(message);
  });

  return <section className="surface-card recommendations-panel" aria-labelledby="recommendations-title">
    <div className="section-heading"><div><span className="eyebrow-label">BASED ON THIS COMPARISON</span><h2 id="recommendations-title">Strengths & next steps</h2><p>Suggestions use detected matches and the matcher’s feedback.</p></div></div>
    <div className="recommendation-grid">
      <article className="recommendation-card strength-card"><div className="recommendation-title"><span className="recommendation-icon strength-icon">↗</span><div><h3>Strengths</h3><p>What already aligns</p></div></div>
        {strengths.length ? <ul>{strengths.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="empty-note">No matching skills were detected. Review your resume and job description for relevant terms.</p>}
      </article>
      <article className="recommendation-card opportunity-card"><div className="recommendation-title"><span className="recommendation-icon opportunity-icon">＋</span><div><h3>Areas to review</h3><p>Potential ways to strengthen your application</p></div></div>
        {opportunities.length ? <ul>{opportunities.map((item) => <li key={item}>{item}</li>)}</ul> : <p className="empty-note">No specific skill gaps were detected in this comparison.</p>}
      </article>
    </div>
  </section>;
}

function ScoreExplanation({ result }: { result: MatchResult }) {
  const coverage = result.job_skills.length ? `${result.matched_skills.length} of ${result.job_skills.length} identified skills` : "No job skills detected";
  return <section className="surface-card score-explanation" aria-labelledby="score-reason-title">
    <div className="section-heading"><div><span className="eyebrow-label">TAILORING INSIGHTS</span><h2 id="score-reason-title">What shaped your score</h2><p>{getStrengthLabel(result)}</p></div></div>
    <div className="formula-bar"><div className="formula-part"><span>Semantic similarity</span><strong>{Math.round(result.semantic_score)}% <small>× 60%</small></strong></div><span className="formula-operator">+</span><div className="formula-part"><span>Skill coverage</span><strong>{Math.round(result.skill_score)}% <small>× 40%</small></strong><small className="formula-detail">{coverage}</small></div><span className="formula-operator">=</span><div className="formula-total"><span>Overall match</span><strong>{Math.round(result.final_score)}%</strong></div></div>
    {result.missing_skills.length > 0 && <div className="gap-callout"><span className="gap-marker"/><p><strong>Most direct gap to review</strong><span>{result.missing_skills.join(", ")}</span></p></div>}
    <p className="score-disclaimer">This score is an estimate based on text similarity and detected skill mentions. It does not measure proficiency, validate claims, or predict hiring outcomes.</p>
  </section>;
}

export function AnalysisDashboard({ result, fileName, fileSize, onReset }: { result: MatchResult; fileName: string; fileSize: number; onReset: () => void }) {
  const sizeText = fileSize >= 1024 * 1024 ? `${(fileSize / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(fileSize / 1024))} KB`;
  const fileType = fileName.split(".").pop()?.toUpperCase() ?? "FILE";
  return <div className="dashboard-wrap">
    <div className="dashboard-topline"><div className="analysis-state" role="status"><span className="state-check">✓</span><span>ANALYSIS COMPLETE</span></div><button className="button button-tertiary" onClick={onReset}>New analysis <span aria-hidden="true">↗</span></button></div>
      <section className="overview-card" aria-labelledby="overview-title">
      <div className="overview-main"><div className="overview-copy"><span className="eyebrow-label">MATCH OVERVIEW</span><h1 id="overview-title">Your resume, in context.</h1><p>A clear view of how your experience compares with this opportunity.</p><div className="analyzed-file"><span className="file-mini">{fileType}</span><span className="filename" title={fileName}>{fileName}</span><span className="file-meta">{sizeText} · Analyzed just now</span></div></div><ScoreRing score={result.final_score}/></div>
      <div className="overview-metrics"><MetricCard label="Semantic similarity" value={result.semantic_score} description="Text and experience themes" weight="60%"/><MetricCard label="Technical skill coverage" value={result.skill_score} description={result.job_skills.length ? `${result.matched_skills.length} of ${result.job_skills.length} job skills found` : "No job skills detected by the current skill dictionary"} weight="40%"/></div>
      <p className="overview-formula"><span className="formula-info">i</span>Overall match = semantic similarity × 60% + skill coverage × 40%</p>
    </section>
    <SkillsPanel result={result}/>
    <ComparisonPanel result={result}/>
    <Recommendations result={result}/>
    <ScoreExplanation result={result}/>
  </div>;
}
