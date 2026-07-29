import { useEffect, useRef } from "react";
import type { FC } from "react";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import ChatMessage from "./ChatMessage";
import TypingIndicator from "./TypingIndicator";
import EmptyState from "../common/EmptyState";
import { theme } from "../../theme/theme";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSendToDevelopment?: (storyContent: string) => void | Promise<void>;
  onSendAllToDevelopment?: (stories: string[]) => void | Promise<void>;
}

/** Scrollable conversation area; auto-scrolls to the newest message. */
const ChatWindow: FC<ChatWindowProps> = ({ messages, isLoading, onSendToDevelopment, onSendAllToDevelopment }) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  return (
    <div
      style={{
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.radiusLg,
        padding: 16,
        minHeight: 320,
        maxHeight: 480,
        overflowY: "auto",
        background: theme.colors.surface,
        boxShadow: theme.shadow,
      }}
    >
      {messages.length === 0 && !isLoading ? (
        <EmptyState
          title="No messages yet"
          description="Describe a business requirement below. The RTE agent will draft a user story and ask clarifying questions if anything is unclear."
        />
      ) : (
        messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onSendToDevelopment={onSendToDevelopment}
            onSendAllToDevelopment={onSendAllToDevelopment}
          />
        ))
      )}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;
