/** Shared design tokens for the Korame frontend. Kept minimal (no UI framework dependency). */
export const theme = {
  colors: {
    background: "#f5f6fa",
    surface: "#ffffff",
    border: "#e2e5eb",
    primary: "#2f5bea",
    primaryText: "#ffffff",
    textPrimary: "#1b1f27",
    textSecondary: "#5b6270",
    userBubble: "#2f5bea",
    assistantBubble: "#eef1f7",
    clarificationBg: "#fff8e6",
    clarificationBorder: "#f0c766",
    errorBg: "#fdeceb",
    errorBorder: "#f3b8b5",
    errorText: "#a12622",
  },
  radius: "10px",
  fontFamily:
    "'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
};

export type Theme = typeof theme;
