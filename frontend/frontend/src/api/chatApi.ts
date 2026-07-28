import { apiClient } from "./client";
import { CHAT_ENDPOINT, CONVERSATIONS_ENDPOINT, RTE_AGENT_NAME } from "../utils/constants";
import type { ChatApiResponse, ConversationHistoryResponse } from "../types/chat";

/**
 * Submit a business requirement (or a follow-up answer) to the RTE agent.
 *
 * Passing the same `conversationId` on subsequent calls lets the backend include
 * prior turns as context, so the RTE agent can ask clarifying questions and
 * remember previous answers.
 */
export async function submitBusinessRequirement(
  requirement: string,
  conversationId?: string
): Promise<ChatApiResponse> {
  const response = await apiClient.post<ChatApiResponse>(CHAT_ENDPOINT, {
    agent_name: RTE_AGENT_NAME,
    requirement,
    conversation_id: conversationId,
  });
  return response.data;
}

/** Fetch the full stored message history for a conversation. */
export async function fetchConversationHistory(
  conversationId: string
): Promise<ConversationHistoryResponse> {
  const response = await apiClient.get<ConversationHistoryResponse>(
    `${CONVERSATIONS_ENDPOINT}/${conversationId}`
  );
  return response.data;
}


