import type { FC } from "react";

interface LogoProps {
  size?: number;
  animated?: boolean;
}

/**
 * Korame mark: three nodes connected by a flowing line - a business
 * requirement moving through the multi-agent pipeline into a finished user
 * story. Optionally animates the connecting flow and the endpoint pulse.
 */
const Logo: FC<LogoProps> = ({ size = 32, animated = true }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 40 40"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Korame logo"
  >
    <rect width="40" height="40" rx="11" fill="url(#korame-logo-gradient)" />
    <path
      d="M11 28 L20 17 L30 10"
      stroke="#ffffff"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      opacity="0.85"
      className={animated ? "korame-logo-flow" : undefined}
    />
    <circle cx="11" cy="28" r="2.75" fill="#ffffff" />
    <circle cx="20" cy="17" r="2.75" fill="#ffffff" />
    <circle cx="30" cy="10" r="3.25" fill="#ffffff" className={animated ? "korame-logo-pulse" : undefined} />
    <defs>
      <linearGradient id="korame-logo-gradient" x1="0" y1="0" x2="40" y2="40">
        <stop offset="0%" stopColor="#4d7bff" />
        <stop offset="100%" stopColor="#1f3fae" />
      </linearGradient>
    </defs>
  </svg>
);

export default Logo;
