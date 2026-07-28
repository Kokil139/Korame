import { useEffect, useRef } from "react";
import type { FC } from "react";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import ChatMessage from "./ChatMessage";
import TypingIndicator from "./TypingIndicator";
import EmptyState from "../common/EmptyState";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
}

/** Scrollable conversation area; auto-scrolls to the newest message. */
const ChatWindow: FC<ChatWindowProps> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  return (
    <div
      style={{
        border: "1px solid #e2e5eb",
        borderRadius: 10,
        padding: 16,
        minHeight: 320,
        maxHeight: 480,
        overflowY: "auto",
        background: "#fafbfc",
      }}
    >
      {messages.length === 0 && !isLoading ? (
        <EmptyState
          title="No messages yet"
          description="Describe a business requirement below. The RTE agent will draft a user story and ask clarifying questions if anything is unclear."
        />
      ) : (
        messages.map((message) => <ChatMessage key={message.id} message={message} />)
      )}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
};

export default ChatWindow;
