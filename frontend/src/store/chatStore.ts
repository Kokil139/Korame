import { create } from "zustand";
import axios from "axios";
import { submitBusinessRequirement, fetchConversationHistory, listConversations } from "../api/chatApi";
import type { ChatMessage, ConversationSummary } from "../types/chat";
import { CONVERSATION_STORAGE_KEY, CONVERSATIONS_INDEX_STORAGE_KEY } from "../utils/constants";

interface ChatState {
  conversationId: string | null;
  messages: ChatMessage[];
  conversations: ConversationSummary[];
  isLoading: boolean;
  isLoadingHistory: boolean;
  error: string | null;
  sendRequirement: (text: string) => Promise<void>;
  startNewConversation: () => void;
  loadConversation: (id: string) => Promise<void>;
  refreshConversationList: () => Promise<void>;
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

function loadConversationsIndex(): ConversationSummary[] {
  try {
    const raw = localStorage.getItem(CONVERSATIONS_INDEX_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ConversationSummary[]) : [];
  } catch {
    return [];
  }
}

function persistConversationsIndex(conversations: ConversationSummary[]): void {
  try {
    localStorage.setItem(CONVERSATIONS_INDEX_STORAGE_KEY, JSON.stringify(conversations));
  } catch {
    // Ignore storage failures (e.g., private browsing quota) - this is not critical.
  }
}

/** Insert/replace a conversation summary and keep the list sorted by most recently updated. */
function upsertConversation(list: ConversationSummary[], entry: ConversationSummary): ConversationSummary[] {
  const next = list.filter((c) => c.id !== entry.id);
  next.push(entry);
  next.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  return next;
}

/** Extract the story title ("**User Story Title**: ...") out of a finalized agent response, if present. */
export function extractStoryTitle(content: string): string | undefined {
  // Look for any line mentioning "user story title" rather than requiring one
  // exact markdown pattern - small local models don't always format it
  // exactly as "**User Story Title**:" (the colon sometimes ends up inside
  // the bold markers instead, e.g. "**User Story Title:**"). Take everything
  // after the first colon on that line and strip emphasis characters.
  for (const line of content.split("\n")) {
    if (/user story title/i.test(line)) {
      const colonIndex = line.indexOf(":");
      if (colonIndex === -1) continue;
      const cleaned = line.slice(colonIndex + 1).replace(/\*/g, "").trim();
      if (cleaned) return cleaned;
    }
  }
  return undefined;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversationId: sessionStorage.getItem(CONVERSATION_STORAGE_KEY),
  messages: [],
  conversations: loadConversationsIndex(),
  isLoading: false,
  isLoadingHistory: false,
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
        suggestions: data.suggestions,
        stories: data.stories,
      };

      set((state) => {
        const messages = [...state.messages, assistantMessage];
        const existing = state.conversations.find((c) => c.id === data.conversation_id);
        const firstUserMessage = messages.find((m) => m.role === "user");

        const conversations = upsertConversation(state.conversations, {
          id: data.conversation_id,
          preview: existing?.preview || firstUserMessage?.content.slice(0, 120) || trimmed.slice(0, 120),
          updatedAt: new Date().toISOString(),
          messageCount: messages.length,
          hasFinalStory: Boolean(existing?.hasFinalStory) || !data.needs_clarification,
          storyTitle: (!data.needs_clarification && extractStoryTitle(assistantMessage.content)) || existing?.storyTitle,
        });
        persistConversationsIndex(conversations);

        return {
          conversationId: data.conversation_id,
          messages,
          conversations,
          isLoading: false,
        };
      });
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

  loadConversation: async (id: string) => {
    if (!id) return;
    // Skip only if this conversation is already the active one AND already has
    // content loaded - this keeps the call idempotent-safe for re-hydrating on
    // page reload (conversationId restored from sessionStorage, messages empty).
    if (get().conversationId === id && get().messages.length > 0) return;

    set({ isLoadingHistory: true, error: null });
    try {
      const history = await fetchConversationHistory(id);
      const messages: ChatMessage[] = history.messages.map((m, idx) => ({
        id: `${id}-${idx}`,
        role: m.role === "user" ? "user" : "assistant",
        content: m.content,
        timestamp: m.timestamp,
      }));

      // Backend-stored messages don't retain the needsClarification/suggestions
      // flags, so infer "finalized" from the presence of the story heading.
      const finalizedMessage = [...messages].reverse().find((m) => m.content.includes("Acceptance Criteria"));
      const hasFinalStory = Boolean(finalizedMessage);

      sessionStorage.setItem(CONVERSATION_STORAGE_KEY, id);

      set((state) => {
        const existing = state.conversations.find((c) => c.id === id);
        const firstUserMessage = messages.find((m) => m.role === "user");

        const conversations = upsertConversation(state.conversations, {
          id,
          preview: existing?.preview || firstUserMessage?.content.slice(0, 120) || "",
          updatedAt: new Date().toISOString(),
          messageCount: messages.length,
          hasFinalStory,
          storyTitle: existing?.storyTitle || (finalizedMessage && extractStoryTitle(finalizedMessage.content)),
        });
        persistConversationsIndex(conversations);

        return {
          conversationId: id,
          messages,
          conversations,
          isLoadingHistory: false,
        };
      });
    } catch (err) {
      set({ isLoadingHistory: false, error: extractErrorMessage(err) });
    }
  },

  refreshConversationList: async () => {
    try {
      const { conversations: backendConversations } = await listConversations();

      set((state) => {
        let conversations = state.conversations;
        for (const backendConversation of backendConversations) {
          const existing = conversations.find((c) => c.id === backendConversation.conversation_id);
          conversations = upsertConversation(conversations, {
            id: backendConversation.conversation_id,
            preview: existing?.preview || backendConversation.preview,
            updatedAt: backendConversation.updated_at,
            messageCount: backendConversation.message_count,
            hasFinalStory: existing?.hasFinalStory,
            storyTitle: existing?.storyTitle,
          });
        }
        persistConversationsIndex(conversations);
        return { conversations };
      });
    } catch {
      // Non-critical: keep using the local index if the backend call fails.
    }
  },
}));

