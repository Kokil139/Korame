import { apiClient } from "./client";
import type {
  StartDevelopmentResponse,
  WorkflowStatus,
  StartStoryRunResponse,
  StoryRunStatus,
} from "../types/workflow";

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

/** Start automatic, sequential development across multiple stories. Returns immediately with a pollable ID. */
export async function startStoryRun(params: {
  stories: string[];
  storyTitles: string[];
  conversationId?: string;
  maxAttemptsPerItem?: number;
}): Promise<StartStoryRunResponse> {
  const response = await apiClient.post<StartStoryRunResponse>("/api/v1/develop-stories", {
    stories: params.stories,
    story_titles: params.storyTitles,
    conversation_id: params.conversationId,
    max_attempts_per_item: params.maxAttemptsPerItem ?? 5,
  });
  return response.data;
}

/** Poll the live status of a multi-story development run. */
export async function getStoryRunStatus(storyRunId: string): Promise<StoryRunStatus> {
  const response = await apiClient.get<StoryRunStatus>(`/api/v1/story-runs/${storyRunId}`);
  return response.data;
}
