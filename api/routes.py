import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from groq import RateLimitError

from models.schemas import ApplicantInput
from workflow.graph import screen_applicant
from utils.audit import init_db, log_screening, save_feedback, get_screenings, get_all_screenings, get_summary

init_db()

app = FastAPI(title="dLoan Screening API")

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=2)


def _run_screening(job_id: str, applicant_dict: dict):
    def progress(name: str):
        with JOBS_LOCK:
            JOBS[job_id]["progress"].append(name)

    with JOBS_LOCK:
        JOBS[job_id]["status"] = "running"

    try:
        result, agent_states = screen_applicant(applicant_dict, progress_callback=progress)
        screening_id = log_screening(
            applicant_dict["applicant_id"],
            applicant_dict,
            result.model_dump(),
            agent_states,
        )
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "done"
            JOBS[job_id]["result"] = result.model_copy(
                update={"screening_id": screening_id}
            ).model_dump()
            JOBS[job_id]["agent_states"] = {
                k: v for k, v in agent_states.items()
                if k not in ("should_stop", "stop_reason")
            }
    except RateLimitError:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = "Groq API rate limit exceeded. Please wait a moment and try again."
    except Exception as e:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = f"Screening failed: {str(e)}"


@app.post("/screen")
def screen(applicant: ApplicantInput):
    job_id = str(uuid.uuid4())[:8]
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "queued",
            "progress": [],
            "result": None,
            "error": None,
        }
    _executor.submit(_run_screening, job_id, applicant.model_dump())
    return {"job_id": job_id}


@app.get("/screen/{job_id}/status")
def screen_status(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


class FeedbackInput(BaseModel):
    screening_id: int
    correct: bool
    override_recommendation: str | None = None
    comment: str | None = None


@app.post("/feedback")
def feedback(data: FeedbackInput):
    try:
        save_feedback(data.screening_id, data.correct, data.override_recommendation, data.comment)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")


@app.get("/audit/summary")
def audit_summary():
    return get_summary()


@app.get("/audit")
def audit_all(limit: int = 50, offset: int = 0):
    return get_all_screenings(limit, offset)


@app.get("/audit/{applicant_id}")
def audit(applicant_id: str):
    return get_screenings(applicant_id)


@app.get("/health")
def health():
    return {"status": "ok"}
