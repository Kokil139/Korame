export type KnowledgeMessageRole = "user" | "assistant" | "system";

/** A single cited excerpt a Knowledge Assistant answer was grounded in. */
export interface KnowledgeSource {
    source: string;
    start_line?: number | null;
    end_line?: number | null;
    score: number;
}

/** A single message rendered in the Knowledge Assistant widget. */
export interface KnowledgeMessage {
    id: string;
    role: KnowledgeMessageRole;
    content: string;
    timestamp: string;
    sources?: KnowledgeSource[];
    /** True when the agent found no matching content in the knowledge base. */
    foundContext?: boolean;
    /** True when this message represents a client/server error rather than agent output. */
    isError?: boolean;
}

/** Shape of the response returned by POST /api/v1/knowledge/ask. */
export interface KnowledgeAskResponse {
    task_id: string;
    conversation_id: string;
    status: "success" | "error";
    answer?: string;
    sources?: KnowledgeSource[];
    found_context?: boolean;
    error?: string;
}