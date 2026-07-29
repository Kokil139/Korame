import type { FC } from "react";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useStoryRunStore } from "../store/storyRunStore";
import AgentWorkflow from "../components/workflow/AgentWorkflow";
import TodoChecklist from "../components/workflow/TodoChecklist";
import ActivityLog from "../components/workflow/ActivityLog";
import ErrorAlert from "../components/common/ErrorAlert";
import EmptyState from "../components/common/EmptyState";
import { theme } from "../theme/theme";

const TERMINAL_RUN_STATUSES = new Set(["complete", "failed", "error"]);

/**
 * Live view of an automatic, sequential multi-story development run: an
 * overall stepper across every story RTE split the requirement into, plus
 * the same agent-pipeline/task-checklist/activity-feed view used for a
 * single story (see WorkflowPage), showing whichever story is currently active.
 */
const StoryRunPage: FC = () => {
  const [searchParams] = useSearchParams();
  const { runStatus, currentTodoStatus, activityLog, error, loadExisting, stopPolling } = useStoryRunStore();

  useEffect(() => {
    const id = searchParams.get("id");
    if (id) {
      loadExisting(id);
    }
    return () => stopPolling();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  if (!searchParams.get("id")) {
    return (
      <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
        <EmptyState
          title="No development run selected"
          description="Send a split, multi-story requirement to development from the RTE page to see its progress here."
        />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 4 }}>Multi-Story Development</h2>
      <p style={{ color: theme.colors.textSecondary, marginTop: 0 }}>
        {runStatus ? `Story ${runStatus.current_index + 1} of ${runStatus.stories.length}` : "Starting..."}
      </p>

      {runStatus && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 20 }}>
          {runStatus.stories.map((story, idx) => {
            const isActive = idx === runStatus.current_index && !TERMINAL_RUN_STATUSES.has(runStatus.status);
            const isStuck = story.status === "failed" || story.status === "error";
            // Priority matters here: once the whole run terminates, isActive
            // goes false for every story - without checking isStuck first,
            // the one that actually broke would render identically to a
            // story that was simply never reached (both would fall through
            // to the default "pending" icon).
            const icon = story.all_complete ? "\u2705" : isStuck ? "\u26a0\ufe0f" : isActive ? "\ud83d\udd27" : "\u26aa";
            return (
              <div
                key={idx}
                className="korame-message-in"
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 2,
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: `1px solid ${isActive ? theme.colors.primary : isStuck ? theme.colors.errorText : theme.colors.border}`,
                  background: isActive ? theme.colors.assistantBubble : isStuck ? theme.colors.errorBg : theme.colors.surface,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span>{icon}</span>
                  <span style={{ flex: 1, fontSize: 13 }}>{story.title}</span>
                  {story.pull_request?.created && (
                    <a
                      href={story.pull_request.pr_url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: 12, color: theme.colors.primary }}
                    >
                      PR &rarr;
                    </a>
                  )}
                </div>
                {isStuck && story.error && (
                  <div style={{ fontSize: 11, color: theme.colors.errorText, paddingLeft: 20 }}>{story.error}</div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {currentTodoStatus && (
        <>
          <AgentWorkflow
            currentAgent={currentTodoStatus.current_agent}
            currentActivity={currentTodoStatus.current_activity}
            hasPullRequest={Boolean(currentTodoStatus.pull_request?.created)}
          />

          <div style={{ textAlign: "center", marginBottom: 20, fontSize: 13, color: theme.colors.textSecondary }}>
            {currentTodoStatus.current_activity || "Starting..."}
          </div>

          <h3 style={{ fontSize: 14, marginBottom: 8 }}>Tasks</h3>
          <TodoChecklist items={currentTodoStatus.items} />

          <h3 style={{ fontSize: 14, margin: "16px 0 8px" }}>Activity</h3>
          <ActivityLog entries={activityLog} />
        </>
      )}

      {runStatus?.status === "complete" && (
        <div style={{ marginTop: 16, fontSize: 13, color: theme.colors.textSecondary }}>
          All stories complete.
        </div>
      )}

      {error && <ErrorAlert message={error} />}
    </div>
  );
};

export default StoryRunPage;
