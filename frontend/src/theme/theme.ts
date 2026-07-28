/** Shared design tokens for the Korame frontend. Kept minimal (no UI framework dependency). */
export const theme = {
  colors: {
    background: "#f5f6fa",
    surface: "#ffffff",
    border: "#e2e5eb",
    primary: "#2f5bea",
    primaryGradientStart: "#4d7bff",
    primaryGradientEnd: "#1f3fae",
    accent: "#7c5cff",
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
  radiusLg: "16px",
  shadow: "0 1px 2px rgba(16, 24, 40, 0.06), 0 1px 3px rgba(16, 24, 40, 0.08)",
  shadowLg: "0 12px 32px rgba(16, 24, 40, 0.10)",
  fontFamily:
    "'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
};

export type Theme = typeof theme;
