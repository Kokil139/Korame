import { create } from "zustand";
import axios from "axios";
import { submitBusinessRequirement } from "../api/chatApi";
import type { ChatMessage } from "../types/chat";
import { CONVERSATION_STORAGE_KEY } from "../utils/constants";

interface ChatState {
  conversationId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendRequirement: (text: string) => Promise<void>;
  startNewConversation: () => void;
}

function createId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (err.code === "ECONNABORTED") {
      return "The RTE agent took too long to respond. Please try again.";
    }
    if (!err.response) {
      return "Could not reach the Korame API. Is the backend running?";
    }
  }
  if (err instanceof Error) return err.message;
  return "Failed to reach the RTE agent. Please try again.";
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversationId: sessionStorage.getItem(CONVERSATION_STORAGE_KEY),
  messages: [],
  isLoading: false,
  error: null,

  sendRequirement: async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || get().isLoading) return;

    const userMessage: ChatMessage = {
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
      const data = await submitBusinessRequirement(trimmed, conversationId ?? undefined);

      if (data.status !== "success") {
        throw new Error(data.error || "RTE agent returned an error");
      }

      if (data.conversation_id) {
        sessionStorage.setItem(CONVERSATION_STORAGE_KEY, data.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: createId("assistant"),
        role: "assistant",
        content: data.user_story ?? "",
        timestamp: new Date().toISOString(),
        needsClarification: data.needs_clarification,
        questions: data.questions,
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

  startNewConversation: () => {
    sessionStorage.removeItem(CONVERSATION_STORAGE_KEY);
    set({ conversationId: null, messages: [], error: null, isLoading: false });
  },
}));
