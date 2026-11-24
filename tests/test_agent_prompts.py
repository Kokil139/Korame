from pathlib import Path

from app.agents import DeveloperAgent, KnowledgeAgent, RTEAgent, TestingAgent
from app.knowledge.todos import TodoStore
from app.router.model_router import ModelRouter

def test_agents_load_prompts_from_app_prompts() -> None:
    model_router = ModelRouter()
    agents = [
        RTEAgent(model_router=model_router),
        DeveloperAgent(model_router=model_router, todo_store=TodoStore()),
        TestingAgent(model_router=model_router),
        KnowledgeAgent(model_router=model_router, knowledge_fabric=object()),
    ]
    prompts_dir = Path(__file__).resolve().parents[1] / "app" / "prompts"

    for agent in agents:
        expected = (prompts_dir / f"{agent.name}.md").read_text(encoding="utf-8")
        assert agent.prompt_template == expected