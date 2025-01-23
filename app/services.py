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

    # save test result
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
    # get test results, sorted by created_at in descending order
    with SessionManager() as db:
        return db.query(TestResult).order_by(TestResult.created_at.desc()).all()


def get_test_report() -> dict:
    # get test report, including score and time
    with SessionManager() as db:
        # query the latest test result for each story-model
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

        # build report
        report = {}
        for story_name, story_name_cn, model_name, total_cases, success_cases, created_at in results:
            score = success_cases / total_cases if total_cases else 0
            report.setdefault(f"{story_name} ({story_name_cn})", {})[model_name] = {
                "score": f"{score:.0%}",
                "timestamp": created_at.strftime("%m-%d %H:%M"),
            }
        return report

