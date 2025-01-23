import logging
from app.utils.db_manager import SessionManager
from app.models import TestLog



class DatabaseAndWebSocketHandler(logging.Handler):
    def __init__(self, task_id):
        super().__init__()
        self.task_id = task_id

    def emit(self, record):
        """处理日志的存储和推送"""
        log_entry = self.format(record)
        level = record.levelname

        # 保存日志到数据库
        with SessionManager() as db:
            db.add(TestLog(task_id=self.task_id, level=level, message=log_entry))
            db.commit()


class LogReader:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.last_read_id = 0  # 初始为 0，表示从最早开始读取

    def get_new_logs(self):
        """
        获取 task_id 对应的新增日志。
        仅查询 `id > last_read_id` 的日志。
        """
        with SessionManager() as db:
            query = db.query(TestLog).filter(
                TestLog.task_id == self.task_id,
                TestLog.id > self.last_read_id  # 只查询新增日志
            ).order_by(TestLog.id.asc())

            logs = query.all()

            if logs:
                # 更新 last_read_id 为最新日志的 ID
                self.last_read_id = logs[-1].id

            return [{"level": log.level, "message": log.message, "created_at": log.created_at} for log in logs]