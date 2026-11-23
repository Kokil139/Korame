import { create } from "zustand";
import axios from "axios";
import { askKnowledgeBase } from "../api/knowledgeApi";
import type { KnowledgeMessage } from "../types/knowledge";
import { KNOWLEDGE_CONVERSATION_STORAGE_KEY } from "../utils/constants";

interface KnowledgeState {
    isOpen: boolean;
    conversationId: string | null;
    messages: KnowledgeMessage[];
    isLoading: boolean;
    error: string | null;
    toggleOpen: () => void;
    askQuestion: (text: string) => Promise<void>;
    reset: () => void;
}

function createId(prefix: string): string {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function extractErrorMessage(err: unknown): string {
    if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === "string") return detail;
        if (err.code === "ECONNABORTED") {
            return "The Knowledge agent took too long to respond. Please try again.";
        }
        if (!err.response) {
            return "Could not reach the Korame API. Is the backend running?";
        }
    }
    if (err instanceof Error) return err.message;
    return "Failed to reach the Knowledge agent. Please try again.";
}

export const useKnowledgeStore = create<KnowledgeState>((set, get) => ({
    isOpen: false,
    conversationId: sessionStorage.getItem(KNOWLEDGE_CONVERSATION_STORAGE_KEY),
    messages: [],
    isLoading: false,
    error: null,

    toggleOpen: () => set((state) => ({ isOpen: !state.isOpen })),

    askQuestion: async (text: string) => {
        const trimmed = text.trim();
        if (!trimmed || get().isLoading) return;

        const userMessage: KnowledgeMessage = {
            id: createId("user"),
            role: "user",
            content: trimmed,
            timestamp: new Date().toISOString(),
        };

        set((state) => ({
            messages: [...state.messages, userMessage],
            isLoading: true,
            error: null,
        }));

        try {
            const { conversationId } = get();
            const data = await askKnowledgeBase(trimmed, conversationId ?? undefined);

            if (data.status !== "success") {
                throw new Error(data.error || "Knowledge agent returned an error");
            }

            if (data.conversation_id) {
                sessionStorage.setItem(KNOWLEDGE_CONVERSATION_STORAGE_KEY, data.conversation_id);
            }

            const assistantMessage: KnowledgeMessage = {
                id: createId("assistant"),
                role: "assistant",
                content: data.answer ?? "",
                timestamp: new Date().toISOString(),
                sources: data.sources,
                foundContext: data.found_context,
            };

            set((state) => ({
                conversationId: data.conversation_id,
                messages: [...state.messages, assistantMessage],
                isLoading: false,
            }));
        } catch (err) {
            const message = extractErrorMessage(err);
            set((state) => ({
                isLoading: false,
                error: message,
                messages: [
                    ...state.messages,
                    {
                        id: createId("error"),
                        role: "system",
                        content: message,
                        timestamp: new Date().toISOString(),
                        isError: true,
                    },
                ],
            }));
        }
    },

    reset: () => {
        sessionStorage.removeItem(KNOWLEDGE_CONVERSATION_STORAGE_KEY);
        set({ conversationId: null, messages: [], error: null, isLoading: false });
    },
}));
