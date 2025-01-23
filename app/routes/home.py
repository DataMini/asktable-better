from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services import get_test_report, get_test_results
from app.schemas import RunTestRequest
from app.runner.main import run_test
import os
import yaml
import uuid
from app import config
from app.utils.task_logger import LogReader

router = APIRouter()


@router.get("/stories")
def get_stories():
    """获取所有故事及其 main.yaml 内容"""
    stories = []
    for story_name in os.listdir(config.atb_stories_dir):
        story_path = os.path.join(config.atb_stories_dir, story_name, "main.yaml")
        if os.path.isfile(story_path):
            with open(story_path, "r", encoding="utf-8") as f:
                yaml_content = yaml.safe_load(f)
            stories.append({"name": story_name, "content": yaml_content})
    return {"stories": stories}


@router.get("/test-report")
def get_report():
    """获取测试报告"""
    return {"report": get_test_report()}


@router.get("/test-history")
def get_history(limit: int = 20):
    """获取最近的测试历史"""
    results = get_test_results()
    sorted_results = sorted(results, key=lambda x: x.created_at, reverse=True)
    return {"history": [r.__dict__ for r in sorted_results[:limit]]}


@router.post("/run-test")
async def run_test_endpoint(
    request: RunTestRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    启动测试的 API
    """
    try:
        # 添加测试任务到后台
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
    获取指定任务 ID 的新增日志。
    """
    try:
        log_reader = LogReader(task_id)
        log_reader.last_read_id = last_read_id
        new_logs = log_reader.get_new_logs()
        return {"logs": new_logs, "last_read_id": log_reader.last_read_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")