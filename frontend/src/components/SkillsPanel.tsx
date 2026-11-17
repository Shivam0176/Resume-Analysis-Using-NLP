import { CSSProperties } from "react";
import { MatchResult } from "../api";

type SkillGroupProps = { title: string; subtitle: string; skills: string[]; tone: "matched" | "missing" | "additional" };

function SkillGroup({ title, subtitle, skills, tone }: SkillGroupProps) {
  return <div className="skill-group">
    <div className="skill-group-heading"><span className={`legend-dot ${tone}`}/><div><h4>{title}</h4><p>{subtitle}</p></div><span className="skill-count">{skills.length}</span></div>
    {skills.length ? <div className="skill-list">{skills.map((skill) => <span className={`skill-chip ${tone}`} key={skill}><span className="skill-category">Technical</span><span className="skill-name">{skill}</span></span>)}</div> : <p className="empty-note">No skills in this group were detected.</p>}
  </div>;
}

export function SkillsPanel({ result }: { result: MatchResult }) {
  const additional = result.resume_skills.filter((skill) => !result.job_skills.includes(skill));
  const total = result.job_skills.length;
  const covered = result.matched_skills.length;
  const coverage = total ? Math.min(100, covered / total * 100) : 0;

  return <section className="surface-card skills-panel" aria-labelledby="skills-title">
    <div className="section-heading"><div><span className="eyebrow-label">ROLE REQUIREMENTS</span><h2 id="skills-title">Skills alignment</h2><p>Skills found in the resume compared with the job description.</p></div><span className="quiet-count">{total} role skills</span></div>
    <div className="skills-layout">
      <div className="skill-groups">
        <SkillGroup title="Matched" subtitle="In both resume and role" skills={result.matched_skills} tone="matched" />
        <SkillGroup title="Missing" subtitle="Listed in the role, not detected in resume" skills={result.missing_skills} tone="missing" />
        <SkillGroup title="Additional" subtitle="In resume, not listed in this role" skills={additional} tone="additional" />
      </div>
      <aside className="coverage-card">
        <span className="eyebrow-label">SKILL COVERAGE</span>
        <div className="coverage-visual"><div className="coverage-ring" style={{ "--coverage": `${coverage * 3.6}deg` } as CSSProperties}><div><strong>{total ? `${Math.round(coverage)}%` : "—"}</strong><span>covered</span></div></div></div>
        <p>{total ? `${covered} of ${total} role skills detected in your resume.` : "No job description skills were detected by the current skill dictionary."}</p>
        <div className="coverage-legend"><span><i className="legend-dot matched"/>Matched</span><span><i className="legend-dot missing"/>Not detected</span></div>
      </aside>
    </div>
  </section>;
}
