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

/** Live per-task checklist for a development workflow run. */
const TodoChecklist: FC<TodoChecklistProps> = ({ items }) => {
  if (items.length === 0) {
    return (
      <div style={{ color: theme.colors.textSecondary, fontSize: 13 }}>
        Breaking the story into tasks...
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((item) => (
        <div
          key={item.id}
          className="korame-message-in"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "8px 12px",
            borderRadius: 8,
            border: `1px solid ${theme.colors.border}`,
            background: item.status === "failed" ? theme.colors.errorBg : theme.colors.surface,
          }}
        >
          <span>{STATUS_ICON[item.status] ?? "\u26aa"}</span>
          <span style={{ flex: 1, fontSize: 13 }}>{item.title}</span>
          {item.attempts > 0 && (
            <span style={{ fontSize: 11, color: theme.colors.textSecondary }}>attempt {item.attempts}</span>
          )}
        </div>
      ))}
    </div>
  );
};

export default TodoChecklist;
