from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI


def get_basic_bot():
    llm_cfg = {
        # 使用 DashScope 提供的模型服务：
        'model': 'qwen-max-latest',
        'model_type': 'qwen_dashscope'
        # Read DASHSCOPE_API_KEY from .env file as the API key.

    }

    system_instruction = '''
    You are an agent help the user to interpreate codes.
    '''
    tools = ['code_interpreter']  # `code_interpreter` 是框架自带的工具，用于执行代码。

    return Assistant(llm=llm_cfg,
                     system_message=system_instruction,
                     function_list=tools)



def get_a_customized_agent(tools: list = [], system_message: str = None, model: str=None):
    llm_cfg = {
        # 使用 DashScope 提供的模型服务：
        # If model is not given, use qwen-max-latest.
        'model': model if model is not None else 'qwen-max-latest',
        'model_type': 'qwen_dashscope'
    }

    if system_message is None:
        system_message = "You are a resourceful agent."
    return Assistant(llm=llm_cfg, system_message=system_message, function_list=tools)

def run_bot_with_ui(bot: Assistant):
    WebUI(bot).run()



