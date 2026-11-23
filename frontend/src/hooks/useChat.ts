import { useChatStore } from "../store/chatStore";

/**
 * Hook exposing the RTE conversation state and actions to page/components.
 */
export function useChat() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const isLoadingHistory = useChatStore((s) => s.isLoadingHistory);
  const error = useChatStore((s) => s.error);
  const conversationId = useChatStore((s) => s.conversationId);
  const conversations = useChatStore((s) => s.conversations);
  const sendRequirement = useChatStore((s) => s.sendRequirement);
  const startNewConversation = useChatStore((s) => s.startNewConversation);
  const loadConversation = useChatStore((s) => s.loadConversation);
  const refreshConversationList = useChatStore((s) => s.refreshConversationList);

  return {
    messages,
    isLoading,
    isLoadingHistory,
    error,
    conversationId,
    conversations,
    sendRequirement,
    startNewConversation,
    loadConversation,
    refreshConversationList,
  };
}

