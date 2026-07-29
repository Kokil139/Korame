import type { FC } from "react";
import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useChat } from "../hooks/useChat";
import { useWorkflowStore } from "../store/workflowStore";
import { extractStoryTitle } from "../store/chatStore";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import ConversationSidebar from "../components/chat/ConversationSidebar";
import ErrorAlert from "../components/common/ErrorAlert";

/** Last-resort title when the story text doesn't mention "user story title" at all. */
function firstLineFallback(content: string): string {
  const firstLine = content.split("\n").find((line) => line.trim().length > 0) ?? "";
  const cleaned = firstLine.replace(/[#*_`]/g, "").trim();
  return cleaned.slice(0, 80) || "Untitled story";
}

const RTEPage: FC = () => {
  const {
    messages,
    isLoading,
    isLoadingHistory,
    error,
    conversationId,
    conversations,
    sendRequirement,
    startNewConversation,
    loadConversation,
    refreshConversationList,
  } = useChat();
  const startDevelopmentWorkflow = useWorkflowStore((s) => s.start);
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Sync the local conversation list with the backend once on mount.
  useEffect(() => {
    refreshConversationList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Single source of truth for "which conversation should be showing": the
  // URL's ?c= param, falling back to a conversation restored from a previous
  // session (sessionStorage) if there's no URL param yet. Re-runs on mount and
  // whenever the URL changes (sidebar clicks, Requirements page links).
  // loadConversation() is internally guarded/idempotent, so it's safe to call
  // here without a separate "is this actually new" check (that duplicate
  // check previously caused two effects to both call it on the same mount).
  useEffect(() => {
    const target = searchParams.get("c") || conversationId;
    if (target) {
      loadConversation(target);
      if (!searchParams.get("c")) {
        setSearchParams({ c: target }, { replace: true });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const handleSelectConversation = (id: string) => {
    setSearchParams({ c: id });
  };

  const handleNewConversation = () => {
    setSearchParams({});
    startNewConversation();
  };

  const handleSendToDevelopment = async (storyContent: string) => {
    const storyTitle = extractStoryTitle(storyContent) || firstLineFallback(storyContent);

    await startDevelopmentWorkflow({
      storyTitle,
      story: storyContent,
      conversationId: conversationId ?? undefined,
    });

    const { todoListId } = useWorkflowStore.getState();
    if (todoListId) {
      navigate(`/workflow?id=${todoListId}`);
    }
  };

  return (
    <div style={{ maxWidth: 1080, margin: "0 auto", padding: 24, display: "flex" }}>
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={conversationId}
        onSelect={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
          <div>
            <h2 style={{ marginBottom: 4 }}>RTE - Business Requirements</h2>
            <p style={{ color: "#5b6270", marginTop: 0 }}>
              Describe what the business needs. The RTE agent will draft a user story and ask
              clarifying questions if anything is missing before finalizing it.
            </p>
          </div>
        </div>

        <ChatWindow
          messages={messages}
          isLoading={isLoading || isLoadingHistory}
          onSendToDevelopment={handleSendToDevelopment}
        />
        <ChatInput onSubmit={sendRequirement} disabled={isLoading} />
        {error && <ErrorAlert message={error} />}
      </div>
    </div>
  );
};

export default RTEPage;

