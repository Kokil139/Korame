import { useState } from "react";
import type { FC } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage as ChatMessageType } from "../../types/chat";
import { theme } from "../../theme/theme";

interface ChatMessageProps {
  message: ChatMessageType;
  /** Shown as a button on each finalized story block; receives that story's own text. */
  onSendToDevelopment?: (storyContent: string) => void | Promise<void>;
}

interface SendToDevelopmentButtonProps {
  storyContent: string;
  onSend: (storyContent: string) => void | Promise<void>;
}

/** Its own isSending state per instance, so sending one story in a multi-story reply doesn't disable the others. */
const SendToDevelopmentButton: FC<SendToDevelopmentButtonProps> = ({ storyContent, onSend }) => {
  const [isSending, setIsSending] = useState(false);

  return (
    <button
      type="button"
      className="korame-btn korame-btn-primary"
      style={{ fontSize: 12, padding: "6px 12px" }}
      disabled={isSending}
      onClick={async () => {
        if (isSending) return;
        setIsSending(true);
        try {
          await onSend(storyContent);
        } finally {
          setIsSending(false);
        }
      }}
    >
      {isSending ? "Starting..." : "Send to Development \u2192"}
    </button>
  );
};

/** Renders a single chat bubble, styled differently for user/assistant/clarification/error messages. */
const ChatMessage: FC<ChatMessageProps> = ({ message, onSendToDevelopment }) => {
  const isUser = message.role === "user";
  const isError = Boolean(message.isError);
  const isClarification = Boolean(message.needsClarification);
  const canSendToDevelopment = !isUser && !isError && !isClarification && Boolean(onSendToDevelopment);
  // RTE usually finalizes one story; only treat it as a "split" reply (and
  // show separate blocks/buttons) when there's genuinely more than one.
  const stories = message.stories && message.stories.length > 1 ? message.stories : null;

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
          {stories ? ` · Split into ${stories.length} stories` : ""}
        </div>
        {stories ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {stories.map((storyContent, idx) => (
              <div
                key={idx}
                style={{
                  paddingBottom: idx < stories.length - 1 ? 12 : 0,
                  borderBottom: idx < stories.length - 1 ? `1px dashed ${theme.colors.border}` : "none",
                }}
              >
                <div style={{ fontSize: 11, fontWeight: 600, opacity: 0.6, marginBottom: 4 }}>
                  Story {idx + 1} of {stories.length}
                </div>
                <div className="chat-markdown">
                  <ReactMarkdown>{storyContent}</ReactMarkdown>
                </div>
                {canSendToDevelopment && onSendToDevelopment && (
                  <div style={{ marginTop: 8 }}>
                    <SendToDevelopmentButton storyContent={storyContent} onSend={onSendToDevelopment} />
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="chat-markdown">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
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
        {!stories && canSendToDevelopment && onSendToDevelopment && (
          <div style={{ marginTop: 8 }}>
            <SendToDevelopmentButton storyContent={message.content} onSend={onSendToDevelopment} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
