import type { FC } from "react";

interface EmptyStateProps {
  title: string;
  description?: string;
}

/** Simple placeholder shown when there is no content to display yet. */
const EmptyState: FC<EmptyStateProps> = ({ title, description }) => (
  <div className="korame-empty-state" style={{ textAlign: "center", color: "#5b6270", padding: "32px 16px" }}>
    <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{title}</div>
    {description && <div style={{ fontSize: 13 }}>{description}</div>}
  </div>
);

export default EmptyState;
