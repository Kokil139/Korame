import type { FC } from "react";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useWorkflowStore } from "../store/workflowStore";
import AgentWorkflow from "../components/workflow/AgentWorkflow";
import TodoChecklist from "../components/workflow/TodoChecklist";
import ActivityLog from "../components/workflow/ActivityLog";
import ErrorAlert from "../components/common/ErrorAlert";
import EmptyState from "../components/common/EmptyState";

/**
 * Live view of a Developer/Testing workflow run: which agent is active right
 * now, the todo list's per-task status, a scrolling activity feed, and the
 * resulting pull request once the story is fully implemented and tested.
 */
const WorkflowPage: FC = () => {
  const [searchParams] = useSearchParams();
  const { status, activityLog, error, loadExisting, stopPolling } = useWorkflowStore();

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
          title="No workflow selected"
          description="Send a finalized user story to development from the RTE page to see its progress here."
        />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <h2 style={{ marginBottom: 4 }}>Development Workflow</h2>
      <p style={{ color: "#5b6270", marginTop: 0 }}>
        {status?.story_title || "Watching the Developer and Testing agents work through the todo list."}
      </p>

      <AgentWorkflow
        currentAgent={status?.current_agent ?? null}
        currentActivity={status?.current_activity ?? ""}
        hasPullRequest={Boolean(status?.pull_request?.created)}
      />

      <div style={{ textAlign: "center", marginBottom: 20, fontSize: 13, color: "#5b6270" }}>
        {status?.current_activity || "Starting..."}
      </div>

      <h3 style={{ fontSize: 14, marginBottom: 8 }}>Tasks</h3>
      <TodoChecklist items={status?.items ?? []} />

      <h3 style={{ fontSize: 14, margin: "16px 0 8px" }}>Activity</h3>
      <ActivityLog entries={activityLog} />

      {status?.pull_request?.created && (
        <div style={{ marginTop: 16 }}>
          <a
            href={status.pull_request.pr_url}
            target="_blank"
            rel="noreferrer"
            className="korame-btn korame-btn-primary"
          >
            View Pull Request &rarr;
          </a>
        </div>
      )}

      {status?.pull_request && !status.pull_request.created && (
        <div style={{ marginTop: 16, fontSize: 13, color: "#5b6270" }}>{status.pull_request.reason}</div>
      )}

      {error && <ErrorAlert message={error} />}
    </div>
  );
};

export default WorkflowPage;
