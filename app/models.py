from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.utils.db_manager import Base


class TestStatus(Enum):
    SUCCESS = "SUCCESS"
    MISTAKE = "MISTAKE" 
    INVALID = "INVALID"
    CRASH = "CRASH"

    @classmethod
    def get_status_by_severity(cls) -> list[str]:
        """获取有序的状态列表"""
        return ["MISTAKE", "INVALID", "CRASH", "SUCCESS"]

class TestResult(Base):
    __tablename__ = "atb_test_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    at_api_base_url = Column(String(255), nullable=False)
    at_project_id = Column(String(255), nullable=False)
    at_cloud_url = Column(String(255), nullable=False)
    story_name = Column(String(255), nullable=False)
    story_name_cn = Column(String(255), nullable=False)
    model_group_name = Column(String(255), nullable=False)
    total_cases = Column(Integer, nullable=False)
    success_cases = Column(Integer, nullable=False)
    crash_cases = Column(Integer, nullable=False)
    invalid_cases = Column(Integer, nullable=False)
    mistake_cases = Column(Integer, nullable=False)
    feishu_doc_url = Column(String(255), nullable=True)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    modified_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    time_taken = Column(Float, nullable=True)
    task_id = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<TestResult story_name={self.story_name}, model_group={self.model_group_name}, id={self.id}>"
    



class TestLog(Base):
    __tablename__ = "atb_test_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(255), nullable=False)  # 任务ID
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    level = Column(String(50), nullable=False)  # 日志级别，例如 INFO, ERROR
    message = Column(Text, nullable=False)  # 日志内容
