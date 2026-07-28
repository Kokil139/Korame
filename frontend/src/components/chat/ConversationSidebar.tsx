import type { FC } from "react";
import type { ConversationSummary } from "../../types/chat";
import { theme } from "../../theme/theme";

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onSelect: (id: string) => void;
  onNewConversation: () => void;
}

/** Lists past RTE conversations (tracked in localStorage) and lets the user switch between them. */
const ConversationSidebar: FC<ConversationSidebarProps> = ({
  conversations,
  activeConversationId,
  onSelect,
  onNewConversation,
}) => {
  return (
    <div
      style={{
        width: 260,
        flexShrink: 0,
        borderRight: `1px solid ${theme.colors.border}`,
        paddingRight: 16,
        marginRight: 16,
      }}
    >
      <button
        type="button"
        onClick={onNewConversation}
        style={{
          width: "100%",
          padding: "8px 12px",
          marginBottom: 12,
          borderRadius: 8,
          border: `1px solid ${theme.colors.primary}`,
          background: theme.colors.primary,
          color: theme.colors.primaryText,
          cursor: "pointer",
          fontSize: 13,
        }}
      >
        + New conversation
      </button>

      <div style={{ fontSize: 12, fontWeight: 600, color: theme.colors.textSecondary, margin: "4px 0 8px" }}>
        Past Conversations
      </div>

      {conversations.length === 0 && (
        <div style={{ fontSize: 13, color: theme.colors.textSecondary }}>No conversations yet.</div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 480, overflowY: "auto" }}>
        {conversations.map((conversation) => (
          <button
            type="button"
            key={conversation.id}
            onClick={() => onSelect(conversation.id)}
            style={{
              textAlign: "left",
              padding: "8px 10px",
              borderRadius: 8,
              border: "1px solid transparent",
              background: conversation.id === activeConversationId ? theme.colors.assistantBubble : "transparent",
              cursor: "pointer",
            }}
          >
            <div
              style={{
                fontSize: 13,
                fontWeight: 500,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                color: theme.colors.textPrimary,
              }}
            >
              {conversation.preview || "Untitled requirement"}
            </div>
            <div
              style={{
                fontSize: 11,
                color: theme.colors.textSecondary,
                display: "flex",
                justifyContent: "space-between",
                marginTop: 2,
              }}
            >
              <span>{new Date(conversation.updatedAt).toLocaleString()}</span>
              {conversation.hasFinalStory && <span title="Story finalized">✓</span>}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ConversationSidebar;
