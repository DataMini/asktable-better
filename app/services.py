from app.models import TestResult, TestStatus
from app.utils.db_manager import SessionManager
from sqlalchemy import func
from app import log

def save_result_to_db(
        at_api_base_url: str,
        at_project_id: str,
        at_cloud_url: str,
        story_name: str, 
        story_name_cn: str,
        model_group_name: str, 
        results: dict,
        fs_doc_url: str = None,
        time_taken: float = None,
        task_id: str = None
        ):
    

    success_cases = len(results[TestStatus.SUCCESS.value])
    crash_cases = len(results[TestStatus.CRASH.value])
    invalid_cases = len(results[TestStatus.INVALID.value])
    mistake_cases = len(results[TestStatus.MISTAKE.value])

    # 保存测试结果
    with SessionManager() as db:
        test_result = TestResult(
            at_api_base_url=at_api_base_url,
            at_project_id=at_project_id,
            at_cloud_url=at_cloud_url,
            story_name=story_name,
            story_name_cn=story_name_cn,
            model_group_name=model_group_name,
            total_cases=success_cases + crash_cases + invalid_cases + mistake_cases,
            success_cases=success_cases,
            crash_cases=crash_cases,
            invalid_cases=invalid_cases,
            mistake_cases=mistake_cases,
            feishu_doc_url=fs_doc_url,
            result_json=results,
            time_taken=time_taken,
            task_id=task_id
        )
        db.add(test_result)
        db.commit()
    return {'success': success_cases, 'crash': crash_cases, 'invalid': invalid_cases, 'mistake': mistake_cases}

def get_test_results() -> list[TestResult]:
    # 获取测试结果
    with SessionManager() as db:
        return db.query(TestResult).all()


def get_test_report() -> dict:
    # 获取测试报告，包括得分和时间
    with SessionManager() as db:
        # 查询所有 story-model 的最新测试结果
        subquery = db.query(
            TestResult.story_name,
            TestResult.story_name_cn,
            TestResult.model_group_name,
            func.max(TestResult.created_at).label("latest_date")
        ).group_by(
            TestResult.story_name, 
            TestResult.story_name_cn, 
            TestResult.model_group_name
        ).subquery()

        results = db.query(
            TestResult.story_name,
            TestResult.story_name_cn,
            TestResult.model_group_name,
            TestResult.total_cases,
            TestResult.success_cases,
            TestResult.created_at
        ).join(
            subquery,
            (TestResult.story_name == subquery.c.story_name) &
            (TestResult.model_group_name == subquery.c.model_group_name) &
            (TestResult.created_at == subquery.c.latest_date)
        ).all()

        # 构建报告
        report = {}
        for story_name, story_name_cn, model_name, total_cases, success_cases, created_at in results:
            score = success_cases / total_cases if total_cases else 0
            report.setdefault(f"{story_name} ({story_name_cn})", {})[model_name] = {
                "score": f"{score:.0%}",
                "timestamp": created_at.strftime("%m-%d %H:%M"),
            }
        return report

