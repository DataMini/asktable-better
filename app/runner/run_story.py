from concurrent.futures import ThreadPoolExecutor
import time
from asktable import Asktable
import asktable

from app import log
from app.models import TestStatus



def run_case(at: Asktable, bot_id: str, case: dict):
    chat = at.chats.create(bot_id=bot_id)
    try_count = 0
    while True:
        try_count += 1
        if try_count > 3:
            log.error(f"Run case {case['name']} failed! try_count > 3")
            return {
                "chat_id": chat.id,
                "trace_id": None,
            }
        try:
            _begin_time = time.time()
            question = case['params']['question']
            if isinstance(question, list):
                question = question[0]

            response = at.chats.messages.create(
                chat_id=chat.id,
                question=question
            )
            answer = response.content
            log.info(f"Run case {case['name']} completed!")

            # 在这里直接将 ContentAttachment 转换为可序列化的字典
            serializable_attachments = []
            for att in answer.attachments:
                attachment = {
                    'type': att.type,
                }
                # 根据类型添加 content 字段
                if att.type == 'excel':
                    attachment['content'] = att.info.get('url', None)
                elif att.type == 'chart':
                    attachment['content'] = att.info.get('category', None)
                else:
                    attachment['content'] = None 
                serializable_attachments.append(attachment)
                
            return {
                "chat_id": chat.id,
                "trace_id": response.trace_id,
                "case_name": case['name'],
                "case_type": case['type'],
                "question": question,
                "actual_answer": answer.text,
                "attachments": serializable_attachments,
                "status": TestStatus.SUCCESS.value,
                "error": None,
                "time_taken": f"{time.time() - _begin_time:.1f}"
            }
        except asktable.APIError as e:
            error_data = e.response.json()
            # if error_data['code'] == 20000:
            if error_data['message'] == '数据准备中，请稍后重试':
                log.info(f'数据准备中，等待10s准备重试')
                time.sleep(10)
                continue

            log.error(f"Run case {case['name']} failed! {e}")

            return {
                "chat_id": chat.id,
                "trace_id": None,
                "case_name": case['name'],
                "case_type": case['type'],
                "question": question,
                "actual_answer": None,
                "attachments": None,
                "status": TestStatus.CRASH.value,
                "error": str(e),
                "time_taken": f"{time.time() - _begin_time:.1f}"
            }
        except Exception as e:
            log.error(f"Run case {case['name']} failed! {e}", exc_info=True)
            return {
                "chat_id": chat.id,
                "trace_id": None,
                "case_name": case['name'],
                "case_type": case['type'],
                "question": question,
                "actual_answer": None,
                "attachments": None,
                "status": 'ATBETTER_CRASH',
                "error": str(e),
                "time_taken": f"{time.time() - _begin_time:.1f}"
            }


def main(
        at: Asktable, 
        bot_name: str,
        datasource_id: str, 
        cases: list,
        works_num: int = 2
    ) -> dict[TestStatus, list]:
    bots = at.bots.list(name=bot_name)
    if bots.items:
        bot = bots.items[0]
        if datasource_id not in bot.datasource_ids:
            at.bots.delete(bot.id)
            bot = at.bots.create(
                name=bot_name, 
                datasource_ids=[datasource_id],
                welcome_message="你好呀～"
            )
            log.info(f"Created new bot '{bot_name}'")
        else:
            log.info(f"Using existing bot '{bot_name}'")
    else:
        bot = at.bots.create(
            name=bot_name, 
            datasource_ids=[datasource_id],
            welcome_message="你好呀～"
        )
        log.info(f"Created new bot '{bot_name}'")

    results = {status.value: [] for status in TestStatus}
    with ThreadPoolExecutor(max_workers=works_num) as executor:
        futures = [executor.submit(run_case, at, bot.id, case) for case in cases]
        for future in futures:
            result = future.result()
            results[result["status"]].append(result)
    return results
