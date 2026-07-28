import type { FC } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import { theme } from "../../theme/theme";

interface ChatMessageProps {
  message: ChatMessageType;
}

/** Renders a single chat bubble, styled differently for user/assistant/clarification/error messages. */
const ChatMessage: FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";
  const isError = Boolean(message.isError);
  const isClarification = Boolean(message.needsClarification);

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
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 12 }}>
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
      </div>
    </div>
  );
};

export default ChatMessage;
