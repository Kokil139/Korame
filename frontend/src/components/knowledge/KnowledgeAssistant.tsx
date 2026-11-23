import { useEffect, useRef, useState } from "react";
import type { FC, FormEvent, KeyboardEvent } from "react";
import ReactMarkdown from "react-markdown";
import { useKnowledgeStore } from "../../store/knowledgeStore";
import type { KnowledgeMessage } from "../../types/knowledge";
import { theme } from "../../theme/theme";
import EmptyState from "../common/EmptyState";

/** Small chat-bubble glyph for the collapsed launcher tab. */
const ChatIcon: FC = () => (
    <svg width={18} height={18} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
            d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v9A2.5 2.5 0 0 1 17.5 17H11l-5.5 4v-4A2.5 2.5 0 0 1 4 14.5v-9Z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
        />
    </svg>
);

/** Renders one user/assistant/system message bubble, with cited sources beneath assistant answers. */
const KnowledgeBubble: FC<{ message: KnowledgeMessage }> = ({ message }) => {
    const isUser = message.role === "user";
    const isError = Boolean(message.isError);

    const bubbleBackground = isError ? theme.colors.errorBg : isUser ? theme.colors.userBubble : theme.colors.assistantBubble;
    const textColor = isUser && !isError ? theme.colors.primaryText : theme.colors.textPrimary;

    return (
        <div
            className="korame-message"
            style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", marginBottom: 10 }}
        >
            <div
                style={{
                    maxWidth: "88%",
                    background: bubbleBackground,
                    color: isError ? theme.colors.errorText : textColor,
                    border: isError ? `1px solid ${theme.colors.errorBorder}` : undefined,
                    borderRadius: theme.radius,
                    padding: "8px 12px",
                    fontSize: 13,
                    lineHeight: 1.5,
                }}
            >
                <div className="chat-markdown">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
                {!isUser && !isError && message.sources && message.sources.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                        {message.sources.map((s, i) => (
                            <span
                                key={`${s.source}-${i}`}
                                title={`Relevance score: ${s.score}`}
                                style={{
                                    fontSize: 11,
                                    color: theme.colors.textSecondary,
                                    background: theme.colors.surface,
                                    border: `1px solid ${theme.colors.border}`,
                                    borderRadius: 999,
                                    padding: "2px 8px",
                                }}
                            >
                                {s.source}
                                {s.start_line && s.end_line ? ` (${s.start_line}-${s.end_line})` : ""}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

/**
 * Floating "ask a question" launcher + panel, fixed to the bottom-right of
 * the viewport. Mounted once at the app shell level (sibling to <main>) so
 * it persists - and keeps its conversation - across page navigation.
 */
const KnowledgeAssistant: FC = () => {
    const { isOpen, messages, isLoading, toggleOpen, askQuestion } = useKnowledgeStore();
    const [value, setValue] = useState("");
    const bottomRef = useRef<HTMLDivElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages, isLoading]);

    useEffect(() => {
        if (isOpen) inputRef.current?.focus();
    }, [isOpen]);

    const handleSubmit = (e: FormEvent) => {
        e?.preventDefault();
        const trimmed = value.trim();
        if (!trimmed || isLoading) return;
        setValue("");
        void askQuestion(trimmed);
    };

    if (!isOpen) {
        return (
            <button
                type="button"
                onClick={toggleOpen}
                className="korame-btn"
                aria-label="Open Knowledge Assistant"
                style={{
                    position: "fixed",
                    bottom: 24,
                    right: 24,
                    zIndex: 1000,
                    background: `linear-gradient(135deg, ${theme.colors.primaryGradientStart}, ${theme.colors.primaryGradientEnd})`,
                    color: theme.colors.primaryText,
                    boxShadow: theme.shadowLg,
                    padding: "12px 18px",
                }}
            >
                <ChatIcon />
                Ask Knowledge Base
            </button>
        );
    }

    return (
        <div
            className="korame-page-fade"
            style={{
                position: "fixed",
                bottom: 24,
                right: 24,
                zIndex: 1000,
                width: 380,
                maxWidth: "calc(100vw - 32px)",
                height: "min(560px, 75vh)",
                display: "flex",
                flexDirection: "column",
                background: theme.colors.surface,
                borderRadius: theme.radiusLg,
                border: `1px solid ${theme.colors.border}`,
                boxShadow: theme.shadowLg,
                overflow: "hidden",
            }}
        >
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 16px",
                    borderBottom: `1px solid ${theme.colors.border}`,
                }}
            >
                <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: theme.colors.textPrimary }}>Knowledge Assistant</div>
                    <div style={{ fontSize: 11, color: theme.colors.textSecondary }}>Ask about Korame's docs</div>
                </div>
                <button
                    type="button"
                    onClick={toggleOpen}
                    aria-label="Close Knowledge Assistant"
                    style={{
                        border: "none",
                        background: "transparent",
                        cursor: "pointer",
                        fontSize: 18,
                        lineHeight: 1,
                        color: theme.colors.textSecondary,
                        padding: 4,
                    }}
                >
                    ×
                </button>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px", background: theme.colors.background }}>
                {messages.length === 0 && !isLoading ? (
                    <EmptyState
                        title="Ask me anything about Korame"
                        description="I can search the project's indexed documents (README, build notes, architecture, specs) and answer using exact excerpts."
                    />
                ) : (
                    messages.map((message) => <KnowledgeBubble key={message.id} message={message} />)
                )}
                {isLoading && (
                    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 10 }}>
                        <div
                            style={{
                                background: theme.colors.assistantBubble,
                                borderRadius: theme.radius,
                                padding: "8px 12px",
                                color: theme.colors.textSecondary,
                                fontSize: 13,
                            }}
                        >
                            Searching the knowledge base
                            <span className="typing-dots">
                                <span>.</span>
                                <span>.</span>
                                <span>.</span>
                            </span>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <form
                onSubmit={handleSubmit}
                style={{ display: "flex", gap: 8, padding: 12, borderTop: `1px solid ${theme.colors.border}` }}
            >
                <input
                    ref={inputRef}
                    type="text"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
                        if (e.key === "Enter") {
                            e.preventDefault();
                            handleSubmit();
                        }
                    }}
                    placeholder="Ask a question..."
                    disabled={isLoading}
                    className="korame-textarea"
                    style={{
                        flex: 1,
                        padding: "8px 10px",
                        borderRadius: theme.radiusMd,
                        border: `1px solid ${theme.colors.border}`,
                        fontFamily: "inherit",
                        fontSize: 13,
                    }}
                />
                <button
                    type="submit"
                    disabled={isLoading || !value.trim()}
                    className="korame-btn korame-btn-primary"
                    style={{
                        cursor: isLoading ? "not-allowed" : "pointer",
                        opacity: isLoading || !value.trim() ? 0.6 : 1,
                        padding: "8px 16px",
                        fontSize: 13,
                    }}
                >
                    {isLoading ? "..." : "Ask"}
                </button>
            </form>
        </div>
    );
};

export default KnowledgeAssistant;
