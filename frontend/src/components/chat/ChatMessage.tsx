import { useState } from "react";
import type { FC } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import { theme } from "../../theme/theme";

interface ChatMessageProps {
  message: ChatMessageType;
  /** Shown as a button on finalized (non-clarification) assistant messages. */
  onSendToDevelopment?: (message: ChatMessageType) => void | Promise<void>;
}

/** Renders a single chat bubble, styled differently for user/assistant/clarification/error messages. */
const ChatMessage: FC<ChatMessageProps> = ({ message, onSendToDevelopment }) => {
  const [isSending, setIsSending] = useState(false);
  const isUser = message.role === "user";
  const isError = Boolean(message.isError);
  const isClarification = Boolean(message.needsClarification);
  const canSendToDevelopment = !isUser && !isError && !isClarification && Boolean(onSendToDevelopment);

  const bubbleBackground = isError
    ? theme.colors.errorBg
    : isClarification
      ? theme.colors.clarificationBg
      : isUser
        ? theme.colors.userBubble
        : theme.colors.assistantBubble;

  const textColor = isUser && !isError && !isClarification ? theme.colors.primaryText : theme.colors.textPrimary;

  const label = isUser ? "You" : isError ? "System" : "RTE Agent";

  return (
    <div
      className="korame-message-in"
      style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 12 }}
    >
      <div
        style={{
          maxWidth: "75%",
          background: bubbleBackground,
          color: isError ? theme.colors.errorText : textColor,
          borderRadius: theme.radius,
          padding: "10px 14px",
          border: isClarification ? `1px solid ${theme.colors.clarificationBorder}` : "none",
          boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
        }}
      >
        <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>
          {label}
          {isClarification && !isUser ? " · Needs clarification" : ""}
        </div>
        <div className="chat-markdown">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        {message.suggestions && message.suggestions.length > 0 && (
          <div
            style={{
              marginTop: 8,
              paddingTop: 8,
              borderTop: `1px dashed ${theme.colors.border}`,
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>💡 Suggestions</div>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {message.suggestions.map((suggestion, idx) => (
                <li key={idx} style={{ fontSize: 13 }}>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}
        {canSendToDevelopment && (
          <div style={{ marginTop: 8 }}>
            <button
              type="button"
              className="korame-btn korame-btn-primary"
              style={{ fontSize: 12, padding: "6px 12px" }}
              disabled={isSending}
              onClick={async () => {
                if (isSending) return;
                setIsSending(true);
                try {
                  await onSendToDevelopment?.(message);
                } finally {
                  setIsSending(false);
                }
              }}
            >
              {isSending ? "Starting..." : "Send to Development \u2192"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
