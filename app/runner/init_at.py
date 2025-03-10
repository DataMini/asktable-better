from asktable import Asktable
import asktable
from app import log


def configure_model(api_base_url, api_key, model_group=None) -> tuple[Asktable, str]:
    at = Asktable(api_key=api_key, base_url=api_base_url)
    try:
        at.auth.me()
        log.info(f"Connected to Asktable {api_base_url}!")
    except asktable.APIConnectionError:
        log.error(f"Failed to connect to Asktable {api_base_url}. Please check your api key and base url.")
        exit(1)
    except asktable.AuthenticationError:
        log.error(f"Failed to connect to Asktable {api_base_url}. Please check your api key and base url.")
        exit(1)
    if model_group:
        try:
            at.project.update(llm_model_group=model_group)
        except asktable.APIError as e:
            log.error(f"failed to set model group for project {at.project.name}, maybe the model group '{model_group}' is not supported.")
            exit(1)
    else:
        # 获取当前project的model group
        model_group = at.project.retrieve().llm_model_group
        log.info(f"Using model group '{model_group}'")
    return at, model_group

def create_or_get_datasource(at: Asktable, story_name_cn, access_config: dict=None, local_file: str=None, force_recreate_db=False):
    ds_name = f"{story_name_cn}数据"
    datasources = at.datasources.list(name=ds_name)
    if datasources.items:
        log.info(f"Using existing datasource '{ds_name}'")
        ds = datasources.items[0]
        if not force_recreate_db:
            return ds
        else:
            at.datasources.delete(ds.id)
            log.info(f"Deleted existing datasource '{ds_name}'")

    if local_file:
        with open(local_file, 'rb', encoding='utf-8') as f:
            ds = at.datasources.create_from_file(
                name=ds_name,
                engine='excel',
                file=f,
                async_process_meta=False
            )
    elif access_config:
        ds = at.datasources.create(
            name=ds_name,
            engine='mysql',
            access_config=access_config
        )
    else:
        raise ValueError("No datasource configuration provided")    
    log.info(f"Created datasource '{ds_name}'")
    return ds

def create_glossary_item(at: Asktable, item):
    glossary = {
        "term": item['name'],
        "definition": item['definition'],
    }
    if 'aliases' in item:
        glossary['aliases'] = item['aliases']
    at.business_glossary.create(
        body=[
            glossary
        ]
    )

def delete_glossary_item(at: Asktable, item):
    items = at.business_glossary.list(term=item['name'])    
    if items.items:
        at.business_glossary.delete(items.items[0].id)
    else:
        log.warning(f"Glossary '{item['name']}' not found")


def create_knowledge(at: Asktable, knowledge):
    glossary = knowledge.get('glossary', [])
    for item in glossary:
        try:
            create_glossary_item(at, item)
            log.info(f"Created glossary '{item['name']}'")
        except asktable.APIError as e:
            if e.status_code == 409 and "Integrity Error" in str(e):
                delete_glossary_item(at, item)
                create_glossary_item(at, item)
                log.info(f"Recreated glossary '{item['name']}'")
            else:
                raise e