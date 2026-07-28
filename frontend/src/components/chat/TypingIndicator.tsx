import type { FC } from "react";
import { theme } from "../../theme/theme";

/** Animated "RTE agent is thinking" indicator shown while awaiting a response. */
const TypingIndicator: FC = () => (
  <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 12 }}>
    <div
      style={{
        background: theme.colors.assistantBubble,
        borderRadius: theme.radius,
        padding: "10px 14px",
        color: theme.colors.textSecondary,
        fontSize: 14,
      }}
    >
      RTE agent is thinking
      <span className="typing-dots">
        <span>.</span>
        <span>.</span>
        <span>.</span>
      </span>
    </div>
  </div>
);

export default TypingIndicator;
