# base/app_config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import cached_property
from os import makedirs
from os.path import expanduser, join
from dotenv import load_dotenv


class AppConfig(BaseSettings):
    # 是否开启 debug 模式
    debug: bool = Field(default=True)

    # 本地存储路径
    atb_data_home_dir: str = Field(default="/at-better-web")

    # 故事目录
    atb_stories_dir: str = Field(default="/stories")

    # 数据库配置
    database_type: str = Field(default="sqlite", description="数据库类型，默认为 sqlite")
    mysql_host: str = Field(default="", description="MySQL 数据库主机地址")
    mysql_port: int = Field(default=3306, description="MySQL 数据库端口号")
    mysql_user: str = Field(default="", description="MySQL 数据库用户名")
    mysql_password: str = Field(default="", description="MySQL 数据库密码")
    mysql_db: str = Field(default="at_better", description="MySQL 数据库名称")
    @cached_property
    def sqlite_path(self):
        sqlite_dir = join(expanduser(self.atb_data_home_dir), "sqlite")
        makedirs(sqlite_dir, exist_ok=True)
        sqlite_file = join(sqlite_dir, "at-better.db")
        return sqlite_file
    
    # atb_project_dir: str = Field(default_factory=lambda: dirname(dirname(dirname(dirname(abspath(__file__))))))
    @cached_property
    def database_url(self) -> str:
        """根据配置生成数据库连接 URL"""
        if self.database_type == "mysql":
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        return f"sqlite:///{self.sqlite_path}"
    
    
    # 飞书配置
    fs_app_id: str = Field(default="")
    fs_app_secret: str = Field(default="")
    fs_wiki_parent_token: str = Field(default="")
    fs_wiki_id: str = Field(default="")
    fs_file_exchange_folder_token: str = Field(default="")  # 示例：EaSffN1MqlXhxldOoR2cJdmAnjf
    fs_wiki_url_prefix: str = Field(default="")  # 示例：https://datamini.feishu.cn/wiki/
    

    class Config:
        env_file = None
        env_file_encoding = "utf-8"

load_dotenv(override=True)
config = AppConfig()