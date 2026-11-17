import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { analyzeResume, MatchResult } from "./api";
import { AnalysisDashboard } from "./components/AnalysisDashboard";

function Icon({ name }: { name: "spark" | "upload" | "file" | "arrow" | "lock" }) {
  const paths = {
    spark: <><path d="m12 3 1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3Z"/><path d="m19 14 1.1 2.9L23 18l-2.9 1.1L19 22l-1.1-2.9L15 18l2.9-1.1L19 14Z"/></>,
    upload: <><path d="M12 16V4m0 0L7 9m5-5 5 5"/><path d="M4 16v4h16v-4"/></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8m-8 4h8"/></>,
    arrow: <><path d="M5 12h14m-6-6 6 6-6 6"/></>,
    lock: <><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3m-4 5v2"/></>,
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState<MatchResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function acceptFile(next: File | undefined) {
    if (!next) return;
    if (!/\.(pdf|docx)$/i.test(next.name)) { setFile(null); setError("Choose a PDF or DOCX file to continue."); return; }
    if (next.size === 0) { setFile(null); setError("This file is empty. Choose a resume with readable content."); return; }
    if (next.size > 10 * 1024 * 1024) { setFile(null); setError("Your resume must be smaller than 10 MB."); return; }
    setFile(next);
    setError("");
  }

  function onFileChange(event: ChangeEvent<HTMLInputElement>) { acceptFile(event.target.files?.[0]); }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (!file) { setError("Upload your resume before starting the analysis."); return; }
    if (!jobDescription.trim()) { setError("Add the job description so we can compare it with your resume."); return; }
    setLoading(true);
    try { setResult(await analyzeResume(file, jobDescription)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Analysis failed. Please try again."); }
    finally { setLoading(false); }
  }

  function reset() { setResult(null); setError(""); window.scrollTo({ top: 0, behavior: "smooth" }); }
  const fileSize = file ? (file.size >= 1024 * 1024 ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` : `${Math.max(1, Math.round(file.size / 1024))} KB`) : "";

  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="#top" aria-label="Career Lens home"><span className="brand-mark"><Icon name="spark"/></span><span>career<span className="brand-light">lens</span></span></a><div className="topbar-right"><span className="secure-label"><span className="secure-dot"/>Private analysis</span><span className="topbar-divider"/><span className="topbar-product">RESUME MATCH</span></div></header>
    <main id="top" className="main-content">
      {result ? <AnalysisDashboard result={result} fileName={file?.name ?? "Resume"} fileSize={file?.size ?? 0} onReset={reset}/> : <>
        <section className="intro"><div className="eyebrow"><span className="eyebrow-line"/> CAREER TOOLS</div><h1>See your experience<br/><span>from their perspective.</span></h1><p>Understand where your resume aligns with a role, what may be missing, and where to focus your next edits.</p></section>
        <form className="workspace" onSubmit={submit}>
          <div className="workspace-heading"><div><span className="section-kicker">START A NEW REVIEW</span><h2>Bring the opportunity into focus</h2></div><span className="time-estimate">Resume match analysis</span></div>
          <div className="input-grid">
            <section className="input-card"><div className="input-card-heading"><span className="step-index">01</span><div><h3>Your resume</h3><p>Use the version you’re considering for this role.</p></div></div>
              <input ref={inputRef} aria-label="Resume file" className="visually-hidden" type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={onFileChange}/>
              <button type="button" className={`dropzone${dragging ? " dropzone-active" : ""}${file ? " has-file" : ""}`} onClick={() => { if (inputRef.current) { inputRef.current.value = ""; inputRef.current.click(); } }} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(event) => { event.preventDefault(); setDragging(false); acceptFile(event.dataTransfer.files[0]); }}>
                <span className="upload-icon"><Icon name={file ? "file" : "upload"}/></span><span className="dropzone-copy">{file ? <><strong>{file.name}</strong><small>{fileSize} · Ready to analyze</small></> : <><strong>Drop your resume here, or <em>browse files</em></strong><small>PDF or DOCX · Maximum file size 10 MB</small></>}</span>{file && <span className="file-ready" aria-label="File ready">✓</span>}
              </button>
              <div className="input-footnote"><Icon name="lock"/>Your resume is processed for this analysis only.</div>
            </section>
            <section className="input-card job-card"><div className="input-card-heading"><span className="step-index">02</span><div><h3>Job description</h3><p>Paste the full description for a more useful comparison.</p></div></div>
              <label className="visually-hidden" htmlFor="job-description">Job description</label><textarea id="job-description" value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} placeholder="Paste the job title, responsibilities, requirements, and skills…" rows={8}/><div className="textarea-footer"><span>Include requirements and responsibilities</span><span>{jobDescription.length} characters</span></div>
            </section>
          </div>
          {error && <div className="error-banner" role="alert"><span>!</span>{error}</div>}
          <div className="submit-row"><div className="model-note"><span className="model-spark"><Icon name="spark"/></span><span><strong>Resume and role analysis</strong><small>Semantic similarity, skill coverage, and profile signals</small></span></div><button className="button button-primary" type="submit" disabled={loading}>{loading ? <><span className="spinner"/>Analyzing your documents…</> : <>Analyze match <Icon name="arrow"/></>}</button></div>
          {loading && <div className="loading-status" role="status"><span className="loading-indicator"/><div><strong>Comparing your resume with the role</strong><span>The first analysis may take a little longer while models load.</span></div></div>}
        </form>
        <section className="process-row" aria-label="Analysis steps"><div className="process-item"><span className="process-icon"><Icon name="file"/></span><div><strong>Compare experience</strong><small>Identify shared themes</small></div></div><span className="process-connector"/><div className="process-item"><span className="process-icon"><Icon name="spark"/></span><div><strong>Review skill coverage</strong><small>See overlap and gaps</small></div></div><span className="process-connector"/><div className="process-item"><span className="process-icon"><Icon name="arrow"/></span><div><strong>Focus your edits</strong><small>Use grounded insights</small></div></div></section>
      </>}
    </main>
    <footer className="footer"><span>Career Lens <span className="footer-separator">/</span> Resume Match</span><span>For guidance only · Not a hiring decision</span></footer>
  </div>;
}
