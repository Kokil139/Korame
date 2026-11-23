import { useEffect, useRef } from "react";
import type { FC } from "react";
import type { ActivityLogEntry, WorkflowAgentName } from "../../types/workflow";
import { theme } from "../../theme/theme";

interface ActivityLogProps {
  entries: ActivityLogEntry[];
}

const AGENT_LABEL: Record<WorkflowAgentName, string> = {
  rte: "RTE",
  developer: "Developer",
  testing: "Testing",
};

/** Scrolling feed of "who did what" derived from workflow status polls. */
const ActivityLog: FC<ActivityLogProps> = ({ entries }) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [entries]);

  return (
    <div
      style={{
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.radius,
        padding: 12,
        maxHeight: 220,
        overflowY: "auto",
        background: theme.colors.surface,
        fontSize: 13,
      }}
    >
      {entries.length === 0 && <div style={{ color: theme.colors.textSecondary }}>Waiting to start...</div>}
      {entries.map((entry) => (
        <div key={entry.id} className="korame-message-in" style={{ marginBottom: 6, display: "flex", gap: 8 }}>
          <span style={{ fontWeight: 600, color: theme.colors.primary, whiteSpace: "nowrap" }}>
            {entry.agent ? AGENT_LABEL[entry.agent] : "\u2014"}
          </span>
          <span style={{ color: theme.colors.textPrimary }}>{entry.text}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
};

export default ActivityLog;
