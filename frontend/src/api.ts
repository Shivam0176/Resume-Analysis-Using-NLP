export interface MatchResult {
  final_score: number;
  semantic_score: number;
  skill_score: number;
  resume_skills: string[];
  job_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  resume_entities: Record<string, string[]>;
  job_entities: Record<string, string[]>;
  feedback: string[];
}

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function analyzeResume(file: File, jobDescription: string): Promise<MatchResult> {
  const body = new FormData();
  body.append("resume", file);
  body.append("job_description", jobDescription);

  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/analyze`, { method: "POST", body });
  } catch {
    throw new Error("Could not reach the analysis service. Check that the backend is running.");
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail ?? "Analysis failed. Please try again.");
  }
  return payload as MatchResult;
}
