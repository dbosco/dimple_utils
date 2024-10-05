import tiktoken

def num_tokens_from_string(string: str, model_name) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
