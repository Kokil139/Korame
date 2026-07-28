import type { FC } from "react";

interface LoadingSpinnerProps {
  size?: number;
}

/** Small inline spinner (keyframes defined in index.css). */
const LoadingSpinner: FC<LoadingSpinnerProps> = ({ size = 16 }) => (
  <span
    aria-label="Loading"
    role="status"
    style={{
      display: "inline-block",
      width: size,
      height: size,
      border: "2px solid #d7dbe3",
      borderTopColor: "#2f5bea",
      borderRadius: "50%",
      animation: "korame-spin 0.7s linear infinite",
    }}
  />
);

export default LoadingSpinner;
