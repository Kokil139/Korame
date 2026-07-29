import { apiClient } from "./client";
import type { StartDevelopmentResponse, WorkflowStatus } from "../types/workflow";

/** Start the Developer/Testing workflow for a finalized story. Returns immediately with a pollable ID. */
export async function startDevelopment(params: {
  storyTitle: string;
  story?: string;
  conversationId?: string;
  maxAttemptsPerItem?: number;
}): Promise<StartDevelopmentResponse> {
  const response = await apiClient.post<StartDevelopmentResponse>("/api/v1/develop", {
    story_title: params.storyTitle,
    story: params.story,
    conversation_id: params.conversationId,
    max_attempts_per_item: params.maxAttemptsPerItem ?? 3,
  });
  return response.data;
}

/** Poll the live status of a development workflow run. */
export async function getWorkflowStatus(todoListId: string): Promise<WorkflowStatus> {
  const response = await apiClient.get<WorkflowStatus>(`/api/v1/todos/${todoListId}`);
  return response.data;
}
