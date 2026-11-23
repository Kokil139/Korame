export type MessageRole = "user" | "assistant" | "system";

/** A single message rendered in the RTE chat window. */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  /** True when this assistant message is asking clarifying questions rather than a final story. */
  needsClarification?: boolean;
  /** Clarifying questions parsed out of the assistant's response, if any. */
  questions?: string[];
  /** Suggestions the agent surfaced from similar past requirements in the knowledge base. */
  suggestions?: string[];
  /** Individual story blocks when RTE split a requirement into multiple independent stories (usually just one, or absent). */
  stories?: string[];
  /** True when this message represents a client/server error rather than agent output. */
  isError?: boolean;
}

/** Shape of the response returned by POST /api/v1/chat. */
export interface ChatApiResponse {
  task_id: string;
  conversation_id: string;
  agent_name: string;
  status: "success" | "error";
  user_story?: string;
  needs_clarification?: boolean;
  questions?: string[];
  suggestions?: string[];
  stories?: string[];
  error?: string;
}

/** Shape of a single stored message returned by GET /api/v1/conversations/{id}. */
export interface ConversationHistoryMessage {
  role: string;
  content: string;
  agent_name?: string;
  timestamp: string;
}

/** Shape of the response returned by GET /api/v1/conversations/{id}. */
export interface ConversationHistoryResponse {
  conversation_id: string;
  messages: ConversationHistoryMessage[];
}

/** A past-conversation entry as tracked locally by the frontend. */
export interface ConversationSummary {
  id: string;
  preview: string;
  updatedAt: string;
  messageCount?: number;
  /** True once this conversation has produced a finalized (STATUS: READY) user story. */
  hasFinalStory?: boolean;
  /** Title of the finalized user story, extracted from the agent's response, if any. */
  storyTitle?: string;
}

/** A single conversation summary as returned by GET /api/v1/conversations. */
export interface BackendConversationSummary {
  conversation_id: string;
  preview: string;
  message_count: number;
  updated_at: string;
}

/** Shape of the response returned by GET /api/v1/conversations. */
export interface ConversationListResponse {
  conversations: BackendConversationSummary[];
}
