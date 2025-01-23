#! /usr/bin/env python3
import os
import json
import time

import lark_oapi
from lark_oapi.api.drive.v1 import UploadAllFileRequest, UploadAllFileRequestBody
from lark_oapi.api.drive.v1 import CreateImportTaskRequest, ImportTask, ImportTaskMountPoint, GetImportTaskRequest
from lark_oapi.api.wiki.v2 import MoveDocsToWikiSpaceNodeRequest, MoveDocsToWikiSpaceNodeRequestBody

from app import config, log

# 创建client
fs_client = lark_oapi.Client.builder() \
    .app_id(config.fs_app_id) \
    .app_secret(config.fs_app_secret) \
    .build()

class SaveToFeishuError(Exception):
    pass

# 上传文件
def upload_file(file_path: str) -> str:
    # 从文件路径获取文件名和大小
    file_name = os.path.basename(file_path)
    size = os.path.getsize(file_path)

    # 构造请求对象
    file = open(file_path, "rb")
    request: UploadAllFileRequest = UploadAllFileRequest.builder() \
        .request_body(UploadAllFileRequestBody.builder()
            .file_name(file_name)
            .parent_type("explorer") 
            .parent_node(config.fs_file_exchange_folder_token)
            .size(size)
            .file(file)
            .build()) \
        .build()

    # 发起请求
    response = fs_client.drive.v1.file.upload_all(request)
    if not response.success():
        raise SaveToFeishuError(f"upload file failed, code: {response}")
    file_token = response.data.file_token
    return file_token


# 将上传的文件导入到云空间
def create_import_task(file_token: str) -> str:
    # 构造请求对象
    request = CreateImportTaskRequest.builder() \
        .request_body(ImportTask.builder()
            .file_extension("md")
            .file_token(file_token)
            .type("docx")
            .point(ImportTaskMountPoint.builder()
                .mount_type(1)
                .mount_key(config.fs_file_exchange_folder_token)
                .build())
            .build()) \
        .build()

    # 发起请求
    response = fs_client.drive.v1.import_task.create(request)

    # 处理失败返回
    if not response.success():
        raise SaveToFeishuError(f"import file failed, code: {response}")
    task_id = response.data.ticket  # 返回任务ID
    return task_id


def _check_import_task(task_id: str) -> str:
    # 构造请求对象
    request = GetImportTaskRequest.builder() \
        .ticket(task_id) \
        .build()

    # 发起请求
    response = fs_client.drive.v1.import_task.get(request)

    # 处理失败返回
    if not response.success():
        raise SaveToFeishuError(f"get import task failed, code: {response}")
    status = response.data.result.job_status
    if status == 0:
        new_file_token = response.data.result.token
        return new_file_token
    else:
        raise SaveToFeishuError(f"import task failed, status: {status}")


def check_import_task(task_id: str, max_retry: int = 20, retry_interval: int = 1) -> str:
    for i in range(max_retry):
        try:
            return _check_import_task(task_id)
        except SaveToFeishuError:
            if i < max_retry - 1:
                time.sleep(retry_interval)
                continue
            raise

def import_file(file_token: str) -> str:
    task_id = create_import_task(file_token)
    new_file_token = check_import_task(task_id)
    return new_file_token


def move_file_to_wiki(file_token: str) -> str:
    # 构造请求对象
    request = MoveDocsToWikiSpaceNodeRequest.builder() \
        .space_id(config.fs_wiki_id) \
        .request_body(MoveDocsToWikiSpaceNodeRequestBody.builder()
            .parent_wiki_token(config.fs_wiki_parent_token)
            .obj_type("docx")
            .obj_token(file_token)
            .build()) \
        .build()

    # 发起请求
    response = fs_client.wiki.v2.space_node.move_docs_to_wiki(request)

    # 处理失败返回
    if not response.success():
        raise SaveToFeishuError(f"move file to wiki failed, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
    wiki_token = response.data.wiki_token
    return wiki_token


def save_result_to_fs(file_path: str) -> str:
    """
    飞书没办法直接保存本地 MD 文件到一个知识库的文档中，所以需要:
    1. 上传本地 MD 文件到飞书 https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/upload_all
    2. 导入到云空间（Drive/Folder） 
        什么是云空间？ https://open.feishu.cn/document/server-docs/docs/drive-v1/introduction
        如何导入文件到云空间？ https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create
        如何获取导入任务状态？ https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/get
    3. 再将这个云空间的文档，移动到知识空间（Wiki/Space） 
        什么是知识空间？ https://open.feishu.cn/document/server-docs/docs/wiki-v2/introduction
        如何移动文档到知识空间？ https://open.feishu.cn/document/server-docs/docs/wiki-v2/task/move_docs_to_wiki
    """
    # 1. 上传文件到飞书
    file_token = upload_file(file_path)
    log.debug(f"upload file to feishu success, file_token: {file_token}")
    # 2. 导入到云空间
    new_file_token = import_file(file_token)
    log.debug(f"import file to cloud space success, new_file_token: {new_file_token}")
    # 3. 移动到知识空间
    wiki_token = move_file_to_wiki(new_file_token)
    wiki_url = f"{config.fs_wiki_url_prefix}{wiki_token}"
    log.info(f"save result to Feishu success: {wiki_url}")
    return wiki_url

