from jobs.manager import JobManager
from jobs.models import JobStatus


def test_job_manager_completes_background_job() -> None:
    manager = JobManager(max_workers=1)

    record = manager.submit(lambda job: "done")
    manager.shutdown(wait=True)

    stored = manager.get(record.job_id)
    assert stored is not None
    assert stored.status == JobStatus.COMPLETED
    assert stored.progress == 100


def test_job_manager_records_failure() -> None:
    manager = JobManager(max_workers=1)

    def fail(job):
        raise RuntimeError("boom")

    record = manager.submit(fail)
    manager.shutdown(wait=True)

    stored = manager.get(record.job_id)
    assert stored is not None
    assert stored.status == JobStatus.FAILED
    assert stored.error == "boom"
