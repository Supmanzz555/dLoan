import uuid
import threading
import atexit
from concurrent.futures import ThreadPoolExecutor

from workflow.graph import screen_applicant
from .models import Screening

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=2)

atexit.register(_executor.shutdown, wait=False)


def _cleanup_old_jobs():
    with JOBS_LOCK:
        done_ids = [
            jid for jid, j in JOBS.items()
            if j["status"] in ("done", "error")
        ]
        for jid in done_ids:
            del JOBS[jid]


def _run_screening(job_id: str, applicant_dict: dict):
    def progress(name: str):
        with JOBS_LOCK:
            if job_id in JOBS:
                JOBS[job_id]["progress"].append(name)

    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id]["status"] = "running"

    try:
        result, agent_states = screen_applicant(applicant_dict, progress_callback=progress)

        Screening.objects.filter(job_id=job_id).update(
            status="done",
            result_data=result.model_dump(),
            agent_states={
                k: v for k, v in agent_states.items()
                if k not in ("should_stop", "stop_reason")
            },
            progress=JOBS.get(job_id, {}).get("progress", []),
        )

        with JOBS_LOCK:
            if job_id in JOBS:
                JOBS[job_id].update(
                    status="done",
                    result=result.model_dump(),
                    agent_states={
                        k: v for k, v in agent_states.items()
                        if k not in ("should_stop", "stop_reason")
                    },
                )
    except Exception as e:
        error_msg = str(e)
        Screening.objects.filter(job_id=job_id).update(
            status="error", error_message=error_msg
        )
        with JOBS_LOCK:
            if job_id in JOBS:
                JOBS[job_id].update(status="error", error=error_msg)


def start_screening(applicant_dict: dict, user=None) -> str:
    job_id = str(uuid.uuid4())[:8]

    Screening.objects.create(
        job_id=job_id,
        status="queued",
        input_data=applicant_dict,
        initiated_by=user,
    )

    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "queued",
            "progress": [],
            "result": None,
            "error": None,
        }

    _cleanup_old_jobs()
    _executor.submit(_run_screening, job_id, applicant_dict)
    return job_id


def get_job_status(job_id: str) -> dict:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if job:
        return job

    screening = Screening.objects.filter(job_id=job_id).first()
    if screening is None:
        return {"status": "not_found"}
    return {
        "status": screening.status,
        "progress": screening.progress,
        "result": screening.result_data,
        "agent_states": screening.agent_states,
        "error": screening.error_message,
    }
