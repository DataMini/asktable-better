# run_test.py
from os.path import join
import yaml
import time
from app import log, config
from app.runner.run_story import main as run_story
from app.runner import init_db
from app.runner import init_at
from app.runner.result.base import save_result
from app.utils.task_logger import DatabaseAndWebSocketHandler


############## main ##############

def run_test(
        at_api_base_url, 
        at_api_key, 
        at_cloud_url,
        at_trace_url_prefix,
        story_name, 
        model_group=None,
        case_name=None, 
        force_recreate_db=False,
        works_num=2,
        task_id=None
    ):

    if task_id:
        log_handler = DatabaseAndWebSocketHandler(task_id)
        log.addHandler(log_handler)
    else:
        log_handler = None

    _begin_time = time.time()

    with open(join(config.atb_stories_dir, story_name, "main.yaml"), 'r') as f:
        story = yaml.safe_load(f)

    if case_name:
        story['cases'] = [case for case in story['cases'] if case['name'] == case_name] 

    try:
        story_name_cn = story['data']['name_cn']
    except KeyError:
        story_name_cn = story_name

    try:
        bot_name_cn = story['data']['bot_name_cn']
    except KeyError:
        log.warning(f"Bot name not found in story '{story_name}'")

    # Step 1: Initialize DB
    if 'access_config' in story['data']:
        init_db.init_db(story['data']['access_config'], story['data']['init_sqls'], story_name, force_recreate_db)
        log.info("Step 1: Database ready!")
    else:
        log.info("Step 1: No database initialization required")
   
    # Step 2: Configure AskTable
    at, curr_model_group = init_at.configure_model(at_api_base_url, at_api_key, model_group)

    # Step 2.1: Create datasource
    local_file = story['data']['local_file'] if 'local_file' in story['data'] else None
    if local_file:
        local_file = join(config.atb_stories_dir, story_name, local_file)

    datasource = init_at.create_or_get_datasource(
        at, 
        story_name_cn, 
        access_config=story['data']['access_config'] if 'access_config' in story['data'] else None,
        local_file=local_file,
        force_recreate_db=force_recreate_db
    )
    if 'business_knowledge' in story:
        init_at.create_knowledge(at, story['business_knowledge'])
    log.info("Step 2: AskTable ready!")

    # Step 3: Run Tests
    results = run_story(
        at=at,
        bot_name=bot_name_cn,
        datasource_id=datasource.id,
        cases=story['cases'],
        works_num=works_num
    )
    
    time_taken = time.time() - _begin_time

    result_stat = save_result(
        results, 
        story_name,
        story_name_cn,
        at_api_base_url,
        at_cloud_url,
        at.auth.me().get('project_id'),
        at_trace_url_prefix,
        curr_model_group,
        time_taken,
        task_id
    )
    at_project_url = f"{at_cloud_url}/p/{at.auth.me().get('project_id')}/data/data-source"
    log.info(f"Step 3: Tests completed! Total time taken: {time_taken:.1f}s, {result_stat} in {at_project_url}")

    if log_handler:
        log.removeHandler(log_handler)
