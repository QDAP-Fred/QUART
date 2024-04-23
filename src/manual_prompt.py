print("-------------------------MANUAL PROMPT-------------------------")

import os

from pyrit.common import default_values
from pyrit.models import PromptRequestPiece
from pyrit.prompt_target import AzureOpenAIChatTarget

default_values.load_default_env()

with AzureOpenAIChatTarget(
    deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY"),
) as target_llm:

    request = PromptRequestPiece(
        role="user",
        original_prompt_text="this is a test prompt",
    ).to_prompt_request_response()
    print(request.__str__())

    response = target_llm.send_prompt(prompt_request=request)
    print(response.__str__())
