import { useState } from "react";
import type { FC } from "react";
import type { TodoItemStatus, WorkflowTodoItem } from "../../types/workflow";
import { theme } from "../../theme/theme";

interface TodoChecklistProps {
  items: WorkflowTodoItem[];
}

const STATUS_ICON: Record<TodoItemStatus, string> = {
  pending: "\u26aa",
  in_progress: "\ud83d\udd27",
  testing: "\ud83e\uddea",
  failed: "\u26a0\ufe0f",
  complete: "\u2705",
};

const PRE_STYLE = {
  margin: 0,
  padding: 10,
  borderRadius: 6,
  background: "#1e1e2e",
  color: "#e2e2e8",
  fontSize: 12,
  fontFamily: "monospace",
  whiteSpace: "pre-wrap" as const,
  wordBreak: "break-word" as const,
  maxHeight: 260,
  overflowY: "auto" as const,
};

/** Live per-task checklist for a development workflow run. */
const TodoChecklist: FC<TodoChecklistProps> = ({ items }) => {
  // Tracks which single item's code/test output panel is expanded (if any).
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (items.length === 0) {
    return (
      <div style={{ color: theme.colors.textSecondary, fontSize: 13 }}>
        Breaking the story into tasks...
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((item) => {
        const hasDetails = Boolean(item.code || item.test_output);
        const isExpanded = expandedId === item.id;

        return (
          <div
            key={item.id}
            className="korame-message-in"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
              padding: "8px 12px",
              borderRadius: 8,
              border: `1px solid ${theme.colors.border}`,
              background: item.status === "failed" ? theme.colors.errorBg : theme.colors.surface,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span>{STATUS_ICON[item.status] ?? "\u26aa"}</span>
              <span style={{ flex: 1, fontSize: 13 }}>{item.title}</span>
              {item.attempts > 0 && (
                <span style={{ fontSize: 11, color: theme.colors.textSecondary }}>attempt {item.attempts}</span>
              )}
              {hasDetails && (
                <button
                  type="button"
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}
                  className="korame-btn korame-btn-secondary"
                  style={{ fontSize: 11, padding: "3px 8px" }}
                >
                  {isExpanded ? "Hide details" : "Show details"}
                </button>
              )}
            </div>

            {isExpanded && (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {item.code && (
                  <div>
                    <div style={{ fontSize: 11, color: theme.colors.textSecondary, marginBottom: 4 }}>
                      Generated code
                    </div>
                    <pre style={PRE_STYLE}>{item.code}</pre>
                  </div>
                )}
                {item.test_output && (
                  <div>
                    <div style={{ fontSize: 11, color: theme.colors.textSecondary, marginBottom: 4 }}>
                      Test output
                    </div>
                    <pre style={PRE_STYLE}>{item.test_output}</pre>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default TodoChecklist;
