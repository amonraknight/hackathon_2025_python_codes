from django.apps import AppConfig
from agent.bot import get_a_customized_agent
from utils.QueueDict import QueueDict
from django.conf import settings


agent_orchestra = {}
chat_history = None


def _initiate_agent_orchestra():
    global agent_orchestra
    # If agent_orchestra is empty, start to create agents.
    if len(agent_orchestra) == 0:
        # Create agent messanger.
        agent_orchestra['messanger'] = get_a_customized_agent(tools=settings.AGENT_TOOLS_MESSANGER,
                                                              system_message=settings.AGENT_SYSTEM_MESSAGE_MESSANGER,
                                                              model=settings.AGENT_MODEL_MESSANGER)
        # Create agent auditor.

        agent_orchestra['auditor'] = get_a_customized_agent(tools=settings.AGENT_TOOLS_AUDITOR,
                                                            system_message=settings.AGENT_SYSTEM_MESSAGE_AUDITOR,
                                                            model=settings.AGENT_MODEL_AUDITOR)

        # Create reviewer agent.
        agent_orchestra['reviewer'] = get_a_customized_agent(tools=settings.AGENT_TOOLS_REVIEWER,
                                                             system_message=settings.AGENT_SYSTEM_MESSAGE_REVIEWER,
                                                             model=settings.AGENT_MODEL_REVIEWER)

        agent_orchestra['assistant_chat'] = get_a_customized_agent(tools=settings.AGENT_TOOLS_ASSISTANT_CHAT,
                                                                   system_message=settings.AGENT_SYSTEM_MESSAGE_ASSISTANT_CHAT,
                                                                   model=settings.AGENT_MODEL_ASSISTANT_CHAT)


class FuncappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcapp'

    def ready(self):
        _initiate_agent_orchestra()

        global chat_history
        if chat_history is None:
            chat_history = QueueDict()
