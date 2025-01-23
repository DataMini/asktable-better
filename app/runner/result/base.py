from app.services import save_result_to_db
from app.runner.result.markdown import save_result_to_md
from app.runner.result.feishu import save_result_to_fs, SaveToFeishuError
from app import log, config


def save_result(
        results: dict, 
        story_name: str,
        story_name_cn: str,
        at_api_base_url: str, 
        at_cloud_url: str,
        at_project_id: str,
        at_trace_url_prefix: str,
        curr_model_group: str,
        time_taken: float,
        task_id: str
    ) -> dict:
    # 生成Markdown报告
    md_file = save_result_to_md(
        results, 
        story_name, 
        story_name_cn, 
        at_api_base_url, 
        at_cloud_url,
        at_project_id,
        at_trace_url_prefix,
        curr_model_group,
        time_taken,
    )

    # 保存到Feishu
    if config.fs_app_id and config.fs_app_secret:
        try:
            fs_doc_url = save_result_to_fs(md_file)
        except SaveToFeishuError as e:
            log.error(f"Save result to Feishu failed: {e}", exc_info=True)
            fs_doc_url = None
    else:
        log.info("Feishu is not configured, skip saving to Feishu")
        fs_doc_url = None

    # 保存到数据库
    return save_result_to_db(
        at_api_base_url, 
        at_project_id,
        at_cloud_url,
        story_name, 
        story_name_cn,
        curr_model_group, 
        results,
        fs_doc_url,
        time_taken,
        task_id
    )

