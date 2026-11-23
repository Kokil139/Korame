import type { FC } from "react";
import { theme } from "../../theme/theme";

interface ErrorAlertProps {
  message: string;
}

/** Inline error banner used for API/network failures. */
const ErrorAlert: FC<ErrorAlertProps> = ({ message }) => (
  <div
    role="alert"
    className="korame-alert-in"
    style={{
      background: theme.colors.errorBg,
      color: theme.colors.errorText,
      border: `1px solid ${theme.colors.errorBorder}`,
      borderRadius: 8,
      padding: "10px 14px",
      marginTop: 12,
      fontSize: 14,
    }}
  >
    {message}
  </div>
);

export default ErrorAlert;
