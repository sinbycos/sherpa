import pytest
from langchain.llms import OpenAI
from langchain.llms.base import LLM

import sherpa_ai.config as cfg
from sherpa_ai.actions.planning import TaskPlanning
from tests.fixtures.llms import get_llm


@pytest.mark.external_api
def test_planning(get_llm):
    llm = get_llm(__file__, test_planning.__name__)

    task_planning = TaskPlanning(llm)

    task = """We need to render a highly complex 3D image on the solar system. We can use any publicly avaliable
    resources to achieve this task."""  # noqa: E501

    agent_pool_description = """Agent: physicist
    Info: the physicist can answer question on any physics questions. 

    Agent: programmer
    Info: the programmer can write scripts to automate some tasks.
    """

    plan = task_planning.execute(task, agent_pool_description)

    print(str(plan))

    assert len(plan.steps) > 0
