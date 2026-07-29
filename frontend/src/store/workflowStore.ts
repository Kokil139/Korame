import { create } from "zustand";
import { startDevelopment, getWorkflowStatus } from "../api/developmentApi";
import type { ActivityLogEntry, WorkflowStatus } from "../types/workflow";

interface WorkflowState {
  todoListId: string | null;
  status: WorkflowStatus | null;
  activityLog: ActivityLogEntry[];
  isPolling: boolean;
  error: string | null;
  start: (params: { storyTitle: string; story?: string; conversationId?: string }) => Promise<void>;
  loadExisting: (todoListId: string) => void;
  stopPolling: () => void;
  reset: () => void;
}

const POLL_INTERVAL_MS = 1500;
const TERMINAL_STATUSES = new Set(["complete", "failed", "error"]);

// Kept outside the store's reactive state - it's a handle, not data to render.
let pollTimer: ReturnType<typeof setInterval> | null = null;

function createLogId(): string {
  return `log-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function clearPollTimer(): void {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

export const useWorkflowStore = create<WorkflowState>((set, get) => {
  const poll = async (todoListId: string) => {
    // Ignore stale polls left over from a previous run.
    if (get().todoListId !== todoListId) return;

    try {
      const status = await getWorkflowStatus(todoListId);
      if (get().todoListId !== todoListId) return;

      set((state) => {
        const lastEntry = state.activityLog[state.activityLog.length - 1];
        const activityChanged = !lastEntry || lastEntry.text !== status.current_activity;
        const activityLog = activityChanged
          ? [
              ...state.activityLog,
              {
                id: createLogId(),
                agent: status.current_agent,
                text: status.current_activity,
                timestamp: new Date().toISOString(),
              },
            ]
          : state.activityLog;

        return { status, activityLog };
      });

      if (TERMINAL_STATUSES.has(status.status)) {
        clearPollTimer();
        set({ isPolling: false });
      }
    } catch (err) {
      // Transient network hiccups shouldn't stop polling; just surface a message.
      set({ error: err instanceof Error ? err.message : "Failed to fetch workflow status" });
    }
  };

  return {
    todoListId: null,
    status: null,
    activityLog: [],
    isPolling: false,
    error: null,

    start: async ({ storyTitle, story, conversationId }) => {
      clearPollTimer();
      set({ error: null, activityLog: [], status: null, todoListId: null, isPolling: true });

      try {
        const result = await startDevelopment({ storyTitle, story, conversationId });
        set({ todoListId: result.todo_list_id });
        await poll(result.todo_list_id);
        pollTimer = setInterval(() => poll(result.todo_list_id), POLL_INTERVAL_MS);
      } catch (err) {
        set({
          isPolling: false,
          error: err instanceof Error ? err.message : "Failed to start the development workflow",
        });
      }
    },

    loadExisting: (todoListId: string) => {
      // If we're already tracking this exact run (e.g. WorkflowPage just
      // mounted right after start() navigated here), don't wipe out the
      // progress start() already fetched - just make sure polling is active.
      if (get().todoListId === todoListId && get().status) {
        if (!pollTimer) {
          pollTimer = setInterval(() => poll(todoListId), POLL_INTERVAL_MS);
        }
        return;
      }

      clearPollTimer();
      set({ todoListId, error: null, activityLog: [], status: null, isPolling: true });
      poll(todoListId);
      pollTimer = setInterval(() => poll(todoListId), POLL_INTERVAL_MS);
    },

    stopPolling: () => {
      clearPollTimer();
      set({ isPolling: false });
    },

    reset: () => {
      clearPollTimer();
      set({ todoListId: null, status: null, activityLog: [], isPolling: false, error: null });
    },
  };
});
