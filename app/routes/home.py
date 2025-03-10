from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.runner.test import sleep_test
from app.services import get_test_report, get_test_results
from app.schemas import RunTestRequest
from app.runner.main import run_test
import os
import yaml
import uuid
from app import config, log
from app.utils.task_logger import LogReader

router = APIRouter()


@router.get("/stories")
def get_stories():
    """Get all stories and their main.yaml content"""
    stories = []
    for story_name in os.listdir(config.atb_stories_dir):
        story_path = os.path.join(config.atb_stories_dir, story_name, "main.yaml")
        if os.path.isfile(story_path):
            with open(story_path, "r", encoding="utf-8") as f:
                yaml_content = yaml.safe_load(f)
                # Remove sensitive information
                if yaml_content and 'data' in yaml_content and 'access_config' in yaml_content['data']:
                    del yaml_content['data']['access_config']
            stories.append({"name": story_name, "content": yaml_content})
    return {"stories": stories}


@router.get("/test-report")
def get_report():
    """Get test report"""
    return {"report": get_test_report()}


@router.get("/test-history")
def get_history(limit: int = 20):
    """Get recent test history"""
    results = get_test_results()
    return {"history": [r.__dict__ for r in results[:limit]]}


@router.post("/run-test")
async def run_test_endpoint(
    request: RunTestRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    API to start a test
    """
    log.info(f"Run test request, force_recreate_db: {request.force_recreate_db}")
    log.debug(f"Run test request, request: {request}")
    try:
        # add test task to background
        task_id = str(uuid.uuid4())
        background_tasks.add_task(
            run_test,
            request.at_api_base_url,
            request.at_api_key,
            request.at_cloud_url,
            request.at_trace_url_prefix,
            request.story_name,
            request.model_group,
            request.case_name,
            request.force_recreate_db,
            request.works,
            task_id
        )
        return {"status": "Running", "message": f"Test for {request.story_name} has started.", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start test: {str(e)}")
    


@router.get("/logs/{task_id}")
async def get_logs(task_id: str, last_read_id: int = 0):
    """
    Get new logs for a specified task ID.
    """
    try:
        log_reader = LogReader(task_id)
        log_reader.last_read_id = last_read_id
        new_logs = log_reader.get_new_logs()
        return {"logs": new_logs, "last_read_id": log_reader.last_read_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")