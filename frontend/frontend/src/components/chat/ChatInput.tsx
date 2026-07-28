import { useState } from "react";
import type { KeyboardEvent, FormEvent, FC } from "react";

interface ChatInputProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
}

/** Textarea + send button. Enter submits, Shift+Enter inserts a newline. */
const ChatInput: FC<ChatInputProps> = ({ onSubmit, disabled }) => {
  const [value, setValue] = useState("");

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 12 }}>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={4}
        placeholder="Describe the business requirement, or answer the RTE agent's questions..."
        disabled={disabled}
        style={{
          width: "100%",
          padding: 10,
          borderRadius: 8,
          border: "1px solid #d7dbe3",
          resize: "vertical",
          fontFamily: "inherit",
          fontSize: 14,
        }}
      />
      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          style={{
            background: "#2f5bea",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            padding: "8px 18px",
            fontSize: 14,
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled || !value.trim() ? 0.6 : 1,
          }}
        >
          {disabled ? "Sending..." : "Send"}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
