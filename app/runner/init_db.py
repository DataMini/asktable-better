import os
import requests
import subprocess
from os.path import join

from app import log, config

class DBAlreadyExists(Exception):
    pass


def init_db(access_config, init_sqls, story_name, force_recreate_db=False):
    """
    Initialize the database based on the provided configuration.

    :param access_config: Dictionary containing DB connection details (host, port, user, password, db).
    :param init_sqls: Dictionary specifying the type of initialization and its source.
    :param story_name: Name of the story (used for logging and DB identification).
    """
    db_name = access_config["db"]
    if init_sqls["type"] == "skip":
        log.info(f"Skipping DB initialization for story '{story_name}'")
        return

    # Ensure the database exists
    try:
        create_database(access_config, force_recreate_db)
        if force_recreate_db:
            log.info(f"Recreated database '{db_name}'")
        else:
            log.info(f"Created database '{db_name}'")
    except DBAlreadyExists:
        log.info(f"Using existing database '{db_name}'")
        return

    # Perform initialization based on type
    if init_sqls["type"] == "http":
        sql_dir = download_and_extract_sql(init_sqls["location"], story_name)
        execute_sql_files(sql_dir, access_config)
        log.info(f"Executed SQL files from {init_sqls['location']}")
    elif init_sqls["type"] == "local":
        sql_dir = join(config.atb_stories_dir, story_name, init_sqls["location"])
        execute_sql_files(sql_dir, access_config)
        log.info(f"Executed SQL files from {init_sqls['location']}")
    else:
        raise ValueError(f"Unsupported init_sqls type: {init_sqls['type']}")

def create_database(access_config, force_recreate_db=False):
    """
    Ensure the database exists by creating it if necessary.

    :param access_config: Dictionary containing DB connection details.
    :param db_name: Name of the database to create.
    """
    host = access_config["host"]
    port = access_config.get("port", 3306)
    user = access_config["user"]
    password = access_config["password"]
    db_name = access_config["db"]

    if force_recreate_db:
        create_db_command = (
            f"mysql -h {host} -P {port} -u {user} -p{password} "
            f"-e 'DROP DATABASE IF EXISTS {db_name}; CREATE DATABASE {db_name};' 2>/dev/null"
        )
    else:
        create_db_command = (
            f"mysql -h {host} -P {port} -u {user} -p{password} "
            f"-e 'CREATE DATABASE {db_name};' 2>/dev/null"
        )
    try:
        subprocess.run(create_db_command, shell=True, check=True)
    except Exception:
        raise DBAlreadyExists(f"Database '{db_name}' already exists")

def download_and_extract_sql(url, story_name):
    """
    Download and extract SQL files from a remote HTTP location.

    :param url: URL of the tar.gz file containing SQL files.
    :param story_name: Name of the story (used for temporary directory naming).
    :return: Path to the directory containing extracted SQL files.
    """
    init_sql_dir = "init_sqls"
    sql_dir = f"/tmp/{story_name}_sqls"
    os.makedirs(sql_dir, exist_ok=True)
    tar_file = os.path.join(sql_dir, f"{init_sql_dir}.tar.gz")

    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to download SQL files from {url} (status: {response.status_code})")
    with open(tar_file, "wb") as f:
        f.write(response.content)
    log.info(f"Downloaded SQL files to {tar_file}")
    subprocess.run(["tar", "-xzf", tar_file, "-C", sql_dir], check=True)
    full_dir = join(sql_dir, init_sql_dir)
    log.info(f"Extracted SQL files to {full_dir}")
    return full_dir

def execute_sql_files(directory, access_config):
    """
    Execute all SQL files in the given directory, in alphabetical order.

    :param directory: Directory containing SQL files.
    :param uri: MySQL connection URI.
    """
    sql_files = sorted([f for f in os.listdir(directory) if f.endswith(".sql")])
    if not sql_files:
        log.error(f"No SQL files found in {directory}")
        exit(1)

    for sql_file in sql_files:
        sql_file_path = os.path.join(directory, sql_file)
        execute_sql_file(sql_file_path, access_config)

def execute_sql_file(sql_file, access_config):
    """
    Execute a single SQL file using MySQL CLI.

    :param sql_file: Path to the SQL file.
    :param uri: MySQL connection URI.
    """
    host = access_config['host']
    user = access_config['user']
    password = access_config['password']
    port = access_config.get('port', 3306)
    db_name = access_config['db']

    command = f"""mysql -u {user} -p{password} -h {host} -P {port} {db_name} < {sql_file} 2>/dev/null"""
    log.info(f"Executing SQL file: {sql_file}")
    subprocess.run(command, shell=True, check=True)
