/** Name of the backend agent that handles business requirement conversations. */
export const RTE_AGENT_NAME = "rte";

/** Korame REST API routes (see app/api/chat.py). */
export const CHAT_ENDPOINT = "/api/v1/chat";
export const CONVERSATIONS_ENDPOINT = "/api/v1/conversations";
export const HEALTH_ENDPOINT = "/api/v1/health";

/** sessionStorage key used to resume the current RTE conversation across page reloads. */
export const CONVERSATION_STORAGE_KEY = "korame.rte.conversationId";
