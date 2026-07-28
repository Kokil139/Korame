import type { FC } from "react";
import { useChat } from "../hooks/useChat";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";
import ErrorAlert from "../components/common/ErrorAlert";

const RTEPage: FC = () => {
  const { messages, isLoading, error, sendRequirement, startNewConversation } = useChat();

  return (
    <div style={{ maxWidth: 760, margin: "0 auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>RTE - Business Requirements</h2>
          <p style={{ color: "#5b6270", marginTop: 0 }}>
            Describe what the business needs. The RTE agent will draft a user story and ask
            clarifying questions if anything is missing before finalizing it.
          </p>
        </div>
        <button
          type="button"
          onClick={startNewConversation}
          disabled={messages.length === 0}
          style={{
            background: "transparent",
            border: "1px solid #d7dbe3",
            borderRadius: 8,
            padding: "6px 12px",
            fontSize: 13,
            whiteSpace: "nowrap",
            cursor: messages.length === 0 ? "not-allowed" : "pointer",
          }}
        >
          New conversation
        </button>
      </div>

      <ChatWindow messages={messages} isLoading={isLoading} />
      <ChatInput onSubmit={sendRequirement} disabled={isLoading} />
      {error && <ErrorAlert message={error} />}
    </div>
  );
};

export default RTEPage;

