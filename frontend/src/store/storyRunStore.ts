import { create } from "zustand";
import { startStoryRun, getStoryRunStatus, getWorkflowStatus } from "../api/developmentApi";
import type { ActivityLogEntry, StoryRunStatus, WorkflowStatus } from "../types/workflow";

interface StoryRunState {
  storyRunId: string | null;
  runStatus: StoryRunStatus | null;
  /** Task-level detail for whichever story is currently active. */
  currentTodoStatus: WorkflowStatus | null;
  activityLog: ActivityLogEntry[];
  isPolling: boolean;
  error: string | null;
  start: (params: { stories: string[]; storyTitles: string[]; conversationId?: string }) => Promise<void>;
  loadExisting: (storyRunId: string) => void;
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

/**
 * Tracks an automatic, sequential multi-story development run: polls the
 * overall run (which story is active, each story's completion/PR), and also
 * polls the currently-active story's own todo-list detail so the same
 * AgentWorkflow/TodoChecklist/ActivityLog components used for a single-story
 * run can be reused here for "what's happening right now".
 */
export const useStoryRunStore = create<StoryRunState>((set, get) => {
  const poll = async (storyRunId: string) => {
    // Ignore stale polls left over from a previous run.
    if (get().storyRunId !== storyRunId) return;

    try {
      const runStatus = await getStoryRunStatus(storyRunId);
      if (get().storyRunId !== storyRunId) return;

      const currentTodoListId = runStatus.stories[runStatus.current_index]?.todo_list_id;
      let currentTodoStatus = get().currentTodoStatus;
      if (currentTodoListId) {
        try {
          currentTodoStatus = await getWorkflowStatus(currentTodoListId);
        } catch {
          // Keep the previous snapshot if this particular poll tick fails -
          // a transient miss here shouldn't blank out what's already shown.
        }
      }

      set((state) => {
        const lastEntry = state.activityLog[state.activityLog.length - 1];
        const activityText = currentTodoStatus?.current_activity;
        const activityChanged = Boolean(activityText) && (!lastEntry || lastEntry.text !== activityText);
        const activityLog = activityChanged
          ? [
              ...state.activityLog,
              {
                id: createLogId(),
                agent: currentTodoStatus?.current_agent ?? null,
                text: activityText as string,
                timestamp: new Date().toISOString(),
              },
            ]
          : state.activityLog;

        // Surface a business-level failure the same way a network/poll
        // failure is shown, so it's actually visible - covers both a hard
        // internal error and a story simply getting stuck out of retries
        // (backend sets runStatus.error for both "error" and "failed").
        const error =
          (runStatus.status === "error" || runStatus.status === "failed") && runStatus.error
            ? runStatus.error
            : state.error;

        return { runStatus, currentTodoStatus, activityLog, error };
      });

      if (TERMINAL_STATUSES.has(runStatus.status)) {
        clearPollTimer();
        set({ isPolling: false });
      }
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to fetch story run status" });
    }
  };

  return {
    storyRunId: null,
    runStatus: null,
    currentTodoStatus: null,
    activityLog: [],
    isPolling: false,
    error: null,

    start: async ({ stories, storyTitles, conversationId }) => {
      clearPollTimer();
      set({
        error: null,
        runStatus: null,
        currentTodoStatus: null,
        activityLog: [],
        storyRunId: null,
        isPolling: true,
      });

      try {
        const result = await startStoryRun({ stories, storyTitles, conversationId });
        set({ storyRunId: result.story_run_id });
        await poll(result.story_run_id);
        pollTimer = setInterval(() => poll(result.story_run_id), POLL_INTERVAL_MS);
      } catch (err) {
        set({
          isPolling: false,
          error: err instanceof Error ? err.message : "Failed to start the multi-story development run",
        });
      }
    },

    loadExisting: (storyRunId: string) => {
      // If we're already tracking this exact run (e.g. this page just
      // mounted right after start() navigated here), don't wipe out the
      // progress start() already fetched - just make sure polling is active.
      if (get().storyRunId === storyRunId && get().runStatus) {
        if (!pollTimer) {
          pollTimer = setInterval(() => poll(storyRunId), POLL_INTERVAL_MS);
        }
        return;
      }

      clearPollTimer();
      set({ storyRunId, error: null, runStatus: null, currentTodoStatus: null, activityLog: [], isPolling: true });
      poll(storyRunId);
      pollTimer = setInterval(() => poll(storyRunId), POLL_INTERVAL_MS);
    },

    stopPolling: () => {
      clearPollTimer();
      set({ isPolling: false });
    },

    reset: () => {
      clearPollTimer();
      set({
        storyRunId: null,
        runStatus: null,
        currentTodoStatus: null,
        activityLog: [],
        isPolling: false,
        error: null,
      });
    },
  };
});
