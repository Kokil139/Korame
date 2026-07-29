import type { FC } from "react";
import type { WorkflowAgentName } from "../../types/workflow";
import { theme } from "../../theme/theme";

interface AgentWorkflowProps {
  currentAgent: WorkflowAgentName | null;
  currentActivity: string;
  hasPullRequest: boolean;
}

const AGENTS: { key: WorkflowAgentName; label: string }[] = [
  { key: "rte", label: "RTE" },
  { key: "developer", label: "Developer" },
  { key: "testing", label: "Testing" },
];

/** Pipeline visualization: RTE -> Developer <-> Testing -> GitHub PR, highlighting the active agent. */
const AgentWorkflow: FC<AgentWorkflowProps> = ({ currentAgent, currentActivity, hasPullRequest }) => {
  // Distinct from the regular implement/test cycle (which also sets
  // currentAgent to "developer") so this connector only lights up during the
  // actual PR-creation moment, not on every task the Developer works on.
  const isOpeningPullRequest = currentActivity === "Opening pull request";

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "24px 8px", flexWrap: "wrap" }}>
      {AGENTS.map((agent, idx) => {
        const isActive = currentAgent === agent.key;
        const nextIsActive = currentAgent === AGENTS[idx + 1]?.key;
        const lineActive = isActive || nextIsActive;

        return (
          <div key={agent.key} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 6,
                padding: "12px 16px",
                borderRadius: 12,
                border: `1.5px solid ${isActive ? theme.colors.primary : theme.colors.border}`,
                background: isActive ? theme.colors.assistantBubble : theme.colors.surface,
                minWidth: 96,
                boxShadow: isActive ? theme.shadowLg : theme.shadow,
                transition: "border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease",
              }}
            >
              <span
                className={isActive ? "korame-agent-dot-pulse" : undefined}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: isActive ? theme.colors.primary : theme.colors.border,
                }}
              />
              <span style={{ fontSize: 13, fontWeight: 600 }}>{agent.label}</span>
            </div>

            {idx < AGENTS.length - 1 && (
              <div
                className={lineActive ? "korame-agent-line-active" : undefined}
                style={
                  lineActive
                    ? { width: 32, height: 2, borderRadius: 1 }
                    : { width: 32, height: 2, background: theme.colors.border, borderRadius: 1 }
                }
              />
            )}
          </div>
        );
      })}

      <div
        className={isOpeningPullRequest ? "korame-agent-line-active" : undefined}
        style={
          isOpeningPullRequest
            ? { width: 32, height: 2, borderRadius: 1 }
            : { width: 32, height: 2, background: theme.colors.border, borderRadius: 1 }
        }
      />

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 6,
          padding: "12px 16px",
          borderRadius: 12,
          border: `1.5px solid ${hasPullRequest ? theme.colors.primary : theme.colors.border}`,
          background: hasPullRequest ? theme.colors.assistantBubble : theme.colors.surface,
          minWidth: 96,
          transition: "border-color 0.2s ease, background 0.2s ease",
        }}
      >
        <span style={{ fontSize: 18 }}>&#128257;</span>
        <span style={{ fontSize: 13, fontWeight: 600 }}>GitHub PR</span>
      </div>
    </div>
  );
};

export default AgentWorkflow;
