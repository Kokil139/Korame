export type WorkflowAgentName = "rte" | "developer" | "testing";

export type TodoItemStatus = "pending" | "in_progress" | "testing" | "failed" | "complete";

/** A single task inside a development todo list. */
export interface WorkflowTodoItem {
  id: string;
  title: string;
  status: TodoItemStatus;
  attempts: number;
}

/** Result of an attempted GitHub pull request creation. */
export interface PullRequestResult {
  created: boolean;
  pr_url?: string;
  pr_number?: number;
  reason?: string;
}

/** Shape of the response returned by GET /api/v1/todos/{id}. */
export interface WorkflowStatus {
  todo_list_id: string;
  story_title: string;
  status: "starting" | "planning" | "running" | "complete" | "failed" | "error";
  current_agent: WorkflowAgentName | null;
  current_activity: string;
  items: WorkflowTodoItem[];
  all_complete: boolean;
  pull_request: PullRequestResult | null;
  report: string;
  error?: string | null;
}

/** Shape of the response returned by POST /api/v1/develop. */
export interface StartDevelopmentResponse {
  todo_list_id: string;
  story_title: string;
  status: string;
}

/** A single entry in the frontend-side activity log, derived from status polls. */
export interface ActivityLogEntry {
  id: string;
  agent: WorkflowAgentName | null;
  text: string;
  timestamp: string;
}
