"""
Workflow Engine for Korame.

Orchestrates the flow of tasks through agents and providers.
"""

import time
import uuid
from typing import Optional, Any
from app.kernel.models import Task, Response, Context
from app.kernel.registry import Registry
from app.router.model_router import ModelRouter


class WorkflowEngine:
    """
    Main workflow orchestration engine.

    For V1:
    1. Takes a task
    2. Routes to appropriate agent
    3. Agent calls model via router
    4. Returns result

    Later it will handle:
    - Multi-agent workflows
    - Agent chaining
    - Error recovery
    - Result caching
    """

    def __init__(self, registry: Registry, model_router: ModelRouter):
        """
        Initialize the workflow engine.

        Args:
            registry: Registry of agents and providers
            model_router: Router for selecting providers
        """
        self.registry = registry
        self.model_router = model_router

    async def execute(
        self,
        agent_name: str,
        input_data: dict[str, Any],
        context: Optional[Context] = None,
        task_id: Optional[str] = None
    ) -> Response:
        """
        Execute a workflow task.

        Args:
            agent_name: Name of the agent to invoke
            input_data: Input data for the agent
            context: Execution context
            task_id: Optional task ID (generated if not provided)

        Returns:
            Response from the agent
        """
        # Generate task ID if not provided
        if not task_id:
            task_id = str(uuid.uuid4())

        # Get or create context
        if not context:
            context = Context()

        # Create the task
        task = Task(
            id=task_id,
            agent_name=agent_name,
            input_data=input_data,
            context=context
        )

        # Get the agent
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return Response(
                task_id=task_id,
                agent_name=agent_name,
                status="error",
                data={},
                error=f"Agent '{agent_name}' not found in registry"
            )

        # Execute the agent
        start_time = time.time()
        try:
            response = await agent.execute(task)
            response.duration_ms = (time.time() - start_time) * 1000
            return response
        except Exception as e:
            return Response(
                task_id=task_id,
                agent_name=agent_name,
                status="error",
                data={},
                error=f"Workflow execution failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    async def execute_chain(
        self,
        agent_sequence: list[str],
        initial_input: dict[str, Any],
        context: Optional[Context] = None
    ) -> list[Response]:
        """
        Execute a chain of agents.

        Each agent's output becomes the next agent's input.

        Args:
            agent_sequence: List of agent names to execute in order
            initial_input: Initial input data
            context: Execution context

        Returns:
            List of responses from each agent
        """
        responses = []
        current_input = initial_input

        for agent_name in agent_sequence:
            response = await self.execute(
                agent_name=agent_name,
                input_data=current_input,
                context=context
            )
            responses.append(response)

            # If any agent fails, stop the chain
            if response.status == "error":
                break

            # Use this agent's output as input for the next agent
            current_input = response.data

        return responses

