import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { analyzeResume } from "./api";

vi.mock("./api", () => ({ analyzeResume: vi.fn() }));

const mockResult = {
  final_score: 74.67,
  semantic_score: 80,
  skill_score: 66.67,
  resume_skills: ["python", "sql"],
  job_skills: ["docker", "python", "sql"],
  matched_skills: ["python", "sql"],
  missing_skills: ["docker"],
  resume_entities: { TITLE: ["Data Analyst"] },
  job_entities: { TITLE: ["Data Engineer"] },
  feedback: ["Consider highlighting relevant experience with Docker."],
};

describe("resume matcher frontend", () => {
  beforeEach(() => vi.clearAllMocks());

  it("validates required resume and job description", async () => {
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));
    expect(screen.getByRole("alert")).toHaveTextContent("Upload your resume");

    const invalidFile = new File(["notes"], "notes.txt", { type: "text/plain" });
    fireEvent.change(screen.getByLabelText(/resume file/i), { target: { files: [invalidFile] } });
    expect(screen.getByRole("alert")).toHaveTextContent("Choose a PDF or DOCX");

    const file = new File(["resume"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText(/resume file/i), { target: { files: [file] } });
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));
    expect(screen.getByRole("alert")).toHaveTextContent("Add the job description");
  });

  it("shows an in-progress state while the API is running", async () => {
    let finish: ((value: typeof mockResult) => void) | undefined;
    vi.mocked(analyzeResume).mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
    render(<App />);
    fireEvent.change(screen.getByLabelText(/resume file/i), {
      target: { files: [new File(["resume"], "resume.pdf", { type: "application/pdf" })] },
    });
    await userEvent.type(screen.getByLabelText("Job description"), "A role description");
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));
    expect(screen.getByRole("status")).toHaveTextContent("Comparing your resume with the role");
    expect(screen.getByRole("button", { name: /analyzing your documents/i })).toBeDisabled();
    finish?.(mockResult);
    expect(await screen.findByRole("heading", { name: "Your resume, in context." })).toBeInTheDocument();
  });

  it("shows score, skills, feedback, and entities after analysis", async () => {
    vi.mocked(analyzeResume).mockResolvedValue(mockResult);
    render(<App />);
    const file = new File(["resume"], "resume.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText(/resume file/i), { target: { files: [file] } });
    await userEvent.type(screen.getByLabelText("Job description"), "Python SQL Docker role");
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));

    expect(await screen.findByRole("heading", { name: "Your resume, in context." })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "75 percent overall match" })).toBeInTheDocument();
    expect(screen.getAllByText("python").length).toBeGreaterThan(0);
    expect(screen.getAllByText("docker").length).toBeGreaterThan(0);
    expect(screen.getByText("Additional")).toBeInTheDocument();
    expect(screen.getByText("Data Analyst")).toBeInTheDocument();
    expect(screen.getByText(/highlighting relevant experience with Docker/i)).toBeInTheDocument();
  });

  it("shows a readable API error", async () => {
    vi.mocked(analyzeResume).mockRejectedValue(new Error("Analysis service is unavailable."));
    render(<App />);
    fireEvent.change(screen.getByLabelText(/resume file/i), {
      target: { files: [new File(["resume"], "resume.docx")] },
    });
    await userEvent.type(screen.getByLabelText("Job description"), "A role description");
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Analysis service is unavailable."));
  });

  it("renders empty skill and entity states without inventing results", async () => {
    vi.mocked(analyzeResume).mockResolvedValue({
      ...mockResult,
      final_score: 28,
      semantic_score: 40,
      skill_score: 0,
      resume_skills: [],
      job_skills: [],
      matched_skills: [],
      missing_skills: [],
      resume_entities: {},
      job_entities: {},
      feedback: ["No matching skills were detected."],
    });
    render(<App />);
    fireEvent.change(screen.getByLabelText(/resume file/i), {
      target: { files: [new File(["resume"], "resume.pdf", { type: "application/pdf" })] },
    });
    await userEvent.type(screen.getByLabelText("Job description"), "Role description");
    await userEvent.click(screen.getByRole("button", { name: /analyze match/i }));

    expect(await screen.findByText("No job skills detected by the current skill dictionary")).toBeInTheDocument();
    expect(screen.getAllByText("No skills in this group were detected.")).toHaveLength(3);
    expect(screen.getAllByText("No additional details detected.")).toHaveLength(2);
  });
});
