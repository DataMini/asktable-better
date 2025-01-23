# base/app_config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import cached_property
from os import makedirs
from os.path import expanduser, join
from dotenv import load_dotenv


class AppConfig(BaseSettings):
    # local storage path
    atb_data_home_dir: str = Field(default="/at-better")

    # stories directory
    atb_stories_dir: str = Field(default="/stories")

    # database config
    database_type: str = Field(default="sqlite", description="database type, default is sqlite")
    mysql_host: str = Field(default="", description="MySQL database host address")
    mysql_port: int = Field(default=3306, description="MySQL database port")
    mysql_user: str = Field(default="", description="MySQL database username")
    mysql_password: str = Field(default="", description="MySQL database password")
    mysql_db: str = Field(default="at_better", description="MySQL database name")
    @cached_property
    def sqlite_path(self):
        sqlite_dir = join(expanduser(self.atb_data_home_dir), "sqlite")
        makedirs(sqlite_dir, exist_ok=True)
        sqlite_file = join(sqlite_dir, "at-better.db")
        return sqlite_file
    
    # atb_project_dir: str = Field(default_factory=lambda: dirname(dirname(dirname(dirname(abspath(__file__))))))
    @cached_property
    def database_url(self) -> str:
        """generate database connection URL based on config"""
        if self.database_type == "mysql":
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        return f"sqlite:///{self.sqlite_path}"
    
    
    # feishu config
    fs_app_id: str = Field(default="")
    fs_app_secret: str = Field(default="")
    fs_wiki_parent_token: str = Field(default="")
    fs_wiki_id: str = Field(default="")
    fs_file_exchange_folder_token: str = Field(default="")  # example: EaSffN1MqlXhxldOoR2cJdmAnjf
    fs_wiki_url_prefix: str = Field(default="")  # example: https://datamini.feishu.cn/wiki/
    

    class Config:
        env_file = None
        env_file_encoding = "utf-8"

load_dotenv(override=True)
config = AppConfig()