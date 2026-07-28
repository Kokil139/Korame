import { useChatStore } from "../store/chatStore";

/**
 * Hook exposing the RTE conversation state and actions to page/components.
 */
export function useChat() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const error = useChatStore((s) => s.error);
  const conversationId = useChatStore((s) => s.conversationId);
  const sendRequirement = useChatStore((s) => s.sendRequirement);
  const startNewConversation = useChatStore((s) => s.startNewConversation);

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendRequirement,
    startNewConversation,
  };
}
