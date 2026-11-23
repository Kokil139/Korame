/** Name of the backend agent that handles business requirement conversations. */
export const RTE_AGENT_NAME = "rte";

/** Korame REST API routes (see app/api/chat.py). */
export const CHAT_ENDPOINT = "/api/v1/chat";
export const CONVERSATIONS_ENDPOINT = "/api/v1/conversations";
export const HEALTH_ENDPOINT = "/api/v1/health";
export const KNOWLEDGE_ASK_ENDPOINT = "/api/v1/knowledge/ask";
/** sessionStorage key used to resume the current RTE conversation across page reloads. */
export const CONVERSATION_STORAGE_KEY = "korame.rte.conversationId";

/** localStorage key used to persist the list of past conversations across browser sessions. */
export const CONVERSATIONS_INDEX_STORAGE_KEY = "korame.rte.conversations";
export const KNOWLEDGE_CONVERSATION_STORAGE_KEY = "korame.knowledge.conversationId";