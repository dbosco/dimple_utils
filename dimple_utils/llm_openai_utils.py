from openai import OpenAI
from dimple_utils import config_utils
from privacera_shield import client as privacera_shield_client
from privacera_shield.model import ConversationType
import os
import time
import logging
import uuid

# These are the global variables that are updated during initialization. Any method using these variables should
# declare them as global in the method.
openai_client = None
openai_model = "gpt-4o"
retry_delay = 60
max_retries = 5
max_response_tokens = 4096

# These are static variables that are not updated during initialization
rate_limit_error_list = ["Rate limit reached for", "Read timed out", "Connection reset by peer",
                         "The server is overloaded or not ready yet"]


def initialize():
    global openai_client, openai_model, retry_delay, max_retries, max_response_tokens
    openai_key_file = config_utils.get_property("openai.key.file", section="OPENAI", fallback="openai_key_dont_commit.txt")
    logging.info(f"Initializing OpenAI with key file: {openai_key_file}")
    # Load the OpenAI key from its file
    # Let's check if the file exists
    if not os.path.exists(openai_key_file):
        # log the current folder
        logging.error(f"Current folder: {os.getcwd()}, openai_key_file={openai_key_file} not found")
        raise Exception(f"OpenAI key file not found: Current folder: {os.getcwd()}, openai_key_file={openai_key_file}")
    with open(openai_key_file, 'r') as f:
        openai_key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = openai_key
    openai_client = OpenAI(api_key=openai_key)
    openai_model = config_utils.get_property("openai.model", section="OPENAI", fallback=openai_model)
    retry_delay = config_utils.get_int_property("openai.retry.delay", section="OPENAI", fallback=retry_delay)
    max_retries = config_utils.get_int_property("openai.max.retries", section="OPENAI", fallback=max_retries)
    max_response_tokens = config_utils.get_int_property("openai.max.response_tokens", section="OPENAI", fallback=max_response_tokens)

    logging.info(f"openai_model={openai_model}, retry_delay={retry_delay}, max_retries={max_retries}, max_response_tokens={max_response_tokens}")
    logging.info(f"OpenAI Initialized. openai_model will be {openai_model}!!!")


def infer_query(prompt, paig_service_user, log_msg=""):

    with privacera_shield_client.create_shield_context(username=paig_service_user):
        thread_id = str(uuid.uuid4())
        updated_prompt_text = privacera_shield_client.check_access(
            text=prompt,
            conversation_type=ConversationType.PROMPT,
            thread_id=thread_id
        )
        updated_prompt_text = updated_prompt_text[0].response_text

        for attempt in range(max_retries):
            try:
                response = openai_client.chat.completions.create(model=openai_model,
                                                                 messages=[{"role": "user", "content": updated_prompt_text}],
                                                                 temperature=0,
                                                                 max_tokens=max_response_tokens)
                break
            except Exception as e:
                if any(msg in str(e) for msg in rate_limit_error_list):
                    if attempt < max_retries - 1:
                        logging.warning(f"Failed to execute. Attempt= {attempt + 1}/{max_retries}. "
                                       f"We will retry after {retry_delay} seconds. exception={e} {log_msg}")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise Exception(f"Failed to execute {func.__name__} after {max_retries} attempts. {log_msg}") from e
                raise

        try:
            llm_response = response.choices[0].message.content
            updated_reply_text = privacera_shield_client.check_access(
                text=llm_response,
                conversation_type=ConversationType.REPLY,
                thread_id=thread_id
            )
            updated_reply_text = updated_reply_text[0].response_text
        except Exception as e:
            logging.error(f"Error while processing LLM response. Won't alter prompt and also will continue: PROMPT={prompt}, exception={e}", exc_info=True)

        return updated_reply_text
