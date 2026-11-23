"""Tests for Korame registry."""

import pytest
from app.kernel.registry import Registry
from app.kernel.agent import Agent
from app.kernel.provider import Provider
from app.kernel.models import Task, Response


class MockAgent(Agent):
    """Mock agent for testing."""
    async def execute(self, task: Task) -> Response:
        return Response(
            task_id=task.id,
            agent_name=self.name,
            status="success",
            data={"result": "mock"}
        )


class MockProvider(Provider):
    """Mock provider for testing."""
    async def call(self, prompt: str, **kwargs) -> str:
        return "mock response"


def test_register_agent():
    """Test registering an agent."""
    registry = Registry()
    agent = MockAgent("test-agent")
    registry.register_agent(agent)

    assert registry.has_agent("test-agent")
    assert registry.get_agent("test-agent") == agent


def test_register_provider():
    """Test registering a provider."""
    registry = Registry()
    provider = MockProvider("test-provider")
    registry.register_provider(provider)

    assert registry.has_provider("test-provider")
    assert registry.get_provider("test-provider") == provider


def test_duplicate_agent_registration():
    """Test that duplicate agent registration raises error."""
    registry = Registry()
    agent1 = MockAgent("test-agent")
    agent2 = MockAgent("test-agent")

    registry.register_agent(agent1)
    with pytest.raises(ValueError):
        registry.register_agent(agent2)


def test_list_agents():
    """Test listing agents."""
    registry = Registry()
    agent1 = MockAgent("agent1")
    agent2 = MockAgent("agent2")

    registry.register_agent(agent1)
    registry.register_agent(agent2)

    agents = registry.list_agents()
    assert len(agents) == 2
    assert "agent1" in agents
    assert "agent2" in agents

