import os
import logging
import datetime
from threading import Thread

DATABASE_NAME = os.environ.get("DATABASE_NAME")
MAX_TURN = int(os.environ.get("MAX_CONVERSATION_TURN"))


def read_prompts(file_path):
    import json

    with open(file_path, "r") as f:
        prompts = json.load(f)
    return prompts


def perform_red_teaming(prompt):
    from pyrit.memory import DuckDBMemory

    # MEMORY
    duckdb_memory = DuckDBMemory(db_path=f"results/{DATABASE_NAME}.db")

    from pyrit.common import default_values
    from textwrap import dedent
    from pyrit.orchestrator import EndTokenRedTeamingOrchestrator
    from pyrit.prompt_target import AzureOpenAIChatTarget

    # from pyrit.prompt_target import AzureMLChatTarget

    default_values.load_default_env()

    attack_strategy = dedent(prompt)

    # red_teaming_llm could be any LLM endpoint. Here it is Azure Open AI for illustrative purposes.
    red_teaming_llm = AzureOpenAIChatTarget(
        deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY"),
    )

    target_llm = AzureOpenAIChatTarget(
        deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT"),
        api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY"),
    )

    start = datetime.datetime.now()

    # Create an orchestrator to manage the red teaming conversation.
    # The initial prompt is intended to keep the red teaming LLM on topic.
    with EndTokenRedTeamingOrchestrator(
        attack_strategy=attack_strategy,
        red_teaming_chat=red_teaming_llm,
        prompt_target=target_llm,
        initial_red_teaming_prompt="Begin conversation",
        verbose=True,
        end_token="<|pwned|>",
        memory=duckdb_memory,
    ) as red_teaming_orchestrator:
        # Apply the attack strategy until the conversation objective is reached
        # or the maximum number of turns is reached.
        red_teaming_orchestrator.apply_attack_strategy_until_completion(max_turns=MAX_TURN)

    end = datetime.datetime.now()
    print(f"Time taken: {end - start}")


# LOGGING
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{log_dir}/debug.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)

prompts = read_prompts(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./scenarios/prompts.json"))
for prompt in prompts:
    Thread(target=perform_red_teaming, args=(prompt["content"],)).start()
