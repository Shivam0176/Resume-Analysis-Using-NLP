import { MatchResult } from "../api";

const entityGroups = [
  { title: "Experience signals", keys: ["TITLE", "COMPANY"] },
  { title: "Education & credentials", keys: ["DEGREE", "INSTITUTION", "CERT"] },
  { title: "Languages", keys: ["LANGUAGE"] },
];

function ComparisonColumn({ title, skills, entities }: { title: string; skills: string[]; entities: Record<string, string[]> }) {
  const sections = entityGroups.map((group) => ({ ...group, values: group.keys.flatMap((key) => entities[key] ?? []) })).filter((group) => group.values.length > 0);
  const knownLabels = new Set(["SKILL", ...entityGroups.flatMap((group) => group.keys)]);
  const otherEntities = Object.entries(entities).filter(([key, values]) => !knownLabels.has(key) && values.length > 0);
  return <article className="comparison-column">
    <header className="comparison-column-title"><span className="comparison-avatar">{title === "Your resume" ? "R" : "J"}</span><div><h3>{title}</h3><p>{title === "Your resume" ? "Candidate profile" : "Role requirements"}</p></div></header>
    <div className="comparison-section"><h4>Detected skills <span>{skills.length}</span></h4>{skills.length ? <div className="comparison-skills">{skills.map((skill) => <span key={skill}>{skill}</span>)}</div> : <p className="empty-note">No skills detected.</p>}</div>
    {sections.length ? sections.map((section) => <div className="comparison-section" key={section.title}><h4>{section.title}</h4><ul className="entity-list">{[...new Set(section.values)].map((value) => <li key={value} title={value}>{value}</li>)}</ul></div>) : <div className="comparison-section"><h4>Profile details</h4><p className="empty-note">No additional details detected.</p></div>}
    {otherEntities.map(([label, values]) => <div className="comparison-section" key={label}><h4>{label.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())}</h4><ul className="entity-list">{[...new Set(values)].map((value) => <li key={value} title={value}>{value}</li>)}</ul></div>)}
  </article>;
}

export function ComparisonPanel({ result }: { result: MatchResult }) {
  return <section className="surface-card comparison-panel" aria-labelledby="comparison-title">
    <div className="section-heading"><div><span className="eyebrow-label">SIDE BY SIDE</span><h2 id="comparison-title">Resume vs. role</h2><p>Profile details and skills identified from each document.</p></div></div>
    <div className="comparison-grid"><ComparisonColumn title="Your resume" skills={result.resume_skills} entities={result.resume_entities}/><ComparisonColumn title="Job description" skills={result.job_skills} entities={result.job_entities}/></div>
  </section>;
}
