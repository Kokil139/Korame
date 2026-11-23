"""Tests for workflow engine."""

import pytest
from app.kernel.models import Context, Task
from app.kernel.agent import Agent
from app.kernel.provider import Provider


class SimpleAgent(Agent):
    """Simple test agent."""
    async def execute(self, task: Task):
        return {
            "task_id": task.id,
            "agent_name": self.name,
            "status": "success",
            "data": {"result": f"Processed by {self.name}"}
        }


@pytest.mark.asyncio
async def test_workflow_engine_execute(workflow_engine, registry):
    """Test workflow engine execution."""
    agent = SimpleAgent("test-agent")
    registry.register_agent(agent)

    response = await workflow_engine.execute(
        agent_name="test-agent",
        input_data={"test": "data"}
    )

    assert response.agent_name == "test-agent"
    assert response.status == "success"


@pytest.mark.asyncio
async def test_workflow_engine_missing_agent(workflow_engine):
    """Test workflow engine with missing agent."""
    response = await workflow_engine.execute(
        agent_name="nonexistent-agent",
        input_data={"test": "data"}
    )

    assert response.status == "error"
    assert "not found" in response.error.lower()


@pytest.mark.asyncio
async def test_workflow_engine_with_context(workflow_engine, registry):
    """Test workflow engine with context."""
    agent = SimpleAgent("test-agent")
    registry.register_agent(agent)

    context = Context(user_id="user1", session_id="session1")

    response = await workflow_engine.execute(
        agent_name="test-agent",
        input_data={"test": "data"},
        context=context
    )

    assert response.agent_name == "test-agent"
    assert response.status == "success"

