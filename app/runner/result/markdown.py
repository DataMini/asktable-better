import os
from datetime import datetime

from app.models import TestStatus
from app import config


MARKDOWN_DIR = config.atb_data_home_dir + "/results_md"


def save_result_to_md(
        results: dict,
        story_name: str,
        story_name_cn: str,
        at_api_base_url: str,
        at_cloud_url: str,
        at_project_id: str,
        at_trace_url_prefix: str,
        model_group_name: str,
        time_taken: float,
    ) -> str:
    """
    Save the test results in Markdown format.

    :param results: Dictionary of test results from run_story_tests.
    :param story_name: Name of the story being tested.
    :param at_api_base_url: Base URL of the AskTable instance.
    :param at_project_id: Project ID of the AskTable instance.
    :return: Path to the generated Markdown file.
    """
    # Ensure output directory exists
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    # Prepare Markdown content
    md_content = []

    # 1. 基本信息
    md_content.append("# AskTable Better 测试报告\n")
    md_content.append("## 一、基本信息\n")
    md_content.append(f"- **报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append(f"- **测试总耗时**: {time_taken:.1f}s")
    md_content.append(f"- **AskTable API**: {at_api_base_url}")
    at_project_url = f"{at_cloud_url}/p/{at_project_id}/data/data-source"
    md_content.append(f"- **AskTable**: [进入项目]({at_project_url})")
    md_content.append(f"- **模型组**: `{model_group_name}`")

    # 2. Result 结果汇总

    md_content.append("## 二、结果汇总\n")
    md_content.append("| 名称 | 问题 | 状态 | 耗时（秒） | AskTable | Trace |")
    md_content.append("|-----------|----------|--------|----------|----------|----------|")
    for status in TestStatus.get_status_by_severity():
        for case in results.get(status, []):
            trace_url = f"{at_trace_url_prefix}{case['trace_id']}"
            trace_url_md = f"[查看Trace]({trace_url})"
            if case['case_type'] == 'chat':
                at_url = f"{at_cloud_url}/p/{at_project_id}/talk/chat/{case['chat_id']}"
                at_url_md = f"[进入聊天]({at_url})"
            else:
                at_url_md = "-"
            md_content.append(
                f"| {case['case_name']} | {case['question']} | {status} | "
                f"{case.get('time_taken', '-')} | {at_url_md} | {trace_url_md} |"
            )

    # 3. Result 详情
    md_content.append("\n## 三、测试详情\n")
    for status in TestStatus.get_status_by_severity():
        for case in results.get(status, []):
            # Add a table for this case
            md_content.append(f"### {case['case_name']}\n")
            md_content.append("| 名称 | 问题 | 状态 | 耗时（秒） | AskTable | Trace |")
            md_content.append("|-----------|----------|--------|----------|----------|----------|")

            trace_url = f"{at_trace_url_prefix}{case['trace_id']}"
            trace_url_md = f"[查看Trace]({trace_url})"
            if case['case_type'] == 'chat':
                at_url = f"{at_cloud_url}/p/{at_project_id}/talk/chat/{case['chat_id']}"
                at_url_md = f"[进入聊天]({at_url})"
            else:
                at_url_md = "-"

            md_content.append(
                f"| {case['case_name']} | {case['question']} | {status} | "
                f"{case.get('time_taken', '-')} | {at_url_md} | {trace_url_md} |"
            )

            # Add details below the table
            md_content.append("\n**实际回答:**")
            md_content.append(f"```\n{case.get('actual_answer', '无回答')}\n```")
            if case.get('attachments'):
                md_content.append("**附件:**")
                for attachment in case['attachments']:
                    md_content.append(f"- 类型: {attachment['type']}, 内容: {attachment['content']}")
            else:
                md_content.append("**附件:** 无")
            md_content.append("")

    # Save Markdown file
    file_name = f"{datetime.now().strftime('%Y%m%d-%H:%M')}-{story_name_cn}({story_name}).md"
    output_file = os.path.join(MARKDOWN_DIR, file_name)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))

    return output_file