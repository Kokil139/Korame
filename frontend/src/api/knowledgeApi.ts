import { apiClient } from "./client";
import { KNOWLEDGE_ASK_ENDPOINT } from "../utils/constants";
import type { KnowledgeAskResponse } from "../types/knowledge";

/**
 * Ask the Knowledge Agent a question about the application's indexed documents.
 *
 * Passing the same `conversationId` on subsequent calls lets the backend include
 * prior turns as context, so follow-up questions ("what about X instead?") work.
 */
export async function askKnowledgeBase(
    question: string,
    conversationId?: string
): Promise<KnowledgeAskResponse> {
    const response = await apiClient.post<KnowledgeAskResponse>(KNOWLEDGE_ASK_ENDPOINT, {
        question,
        conversation_id: conversationId,
    });
    return response.data;
}