from backend.app.repositories.logging import get_log_repository


async def job_listener(event):
    async with get_log_repository() as log_repo:        
        status, message = False, str(event.exception) if event.exception \
            else True, "Job executed successfully" 

        await log_repo.create_task_log(
            job_id=event.job_id,
            task_name=event.job_id,
            success=status,
            message=message
        )