from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from potassium.dependencies import get_scheduler

router = APIRouter()


class JobUpdate(BaseModel):
    frequency_seconds: int = Field(..., gt=0, description="The new frequency for the job in seconds.")


class JobStatus(BaseModel):
    job_id: str
    is_running: bool
    next_run_time: str | None


@router.put("/jobs/connector_status_check", response_model=JobStatus)
def update_job_frequency(job_update: JobUpdate, scheduler: AsyncIOScheduler = Depends(get_scheduler)) -> JobStatus:
    job_id = "connector_status_check"

    if not scheduler.running:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Scheduler is not running. The job cannot be modified."
        )

    job: Job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with ID '{job_id}' not found.")

    try:
        scheduler.modify_job(job_id, trigger=IntervalTrigger(seconds=job_update.frequency_seconds))

        # After modification, get the job again to reflect the new state
        updated_job = scheduler.get_job(job_id)

        return JobStatus(
            job_id=updated_job.id,
            is_running=scheduler.running,
            next_run_time=updated_job.next_run_time.isoformat() if updated_job.next_run_time else None,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to reschedule job: {e}")


@router.get("/jobs/connector_status_check", response_model=JobStatus)
def get_job_status(scheduler: AsyncIOScheduler = Depends(get_scheduler)) -> JobStatus:
    job_id = "connector_status_check"
    if not scheduler.running:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Scheduler is not running.")

    job: Job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job with ID '{job_id}' not found.")

    return JobStatus(
        job_id=job.id,
        is_running=scheduler.running,
        next_run_time=job.next_run_time.isoformat() if job.next_run_time else None,
    )
