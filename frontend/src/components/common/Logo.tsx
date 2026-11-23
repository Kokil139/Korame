import type { FC } from "react";

interface LogoProps {
  size?: number;
  animated?: boolean;
}

/**
 * Korame mark: a "K" built from five connected nodes - each node is an agent,
 * each line is agents talking to one another, converging on the central hub
 * (which pulses) the way requirements flow through the multi-agent pipeline.
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
      d="M13 9 L13 31 M13 20 L29 9 M13 20 L29 31"
      stroke="#ffffff"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      opacity="0.85"
      className={animated ? "korame-logo-flow" : undefined}
    />
    <circle cx="13" cy="9" r="2.75" fill="#ffffff" />
    <circle cx="13" cy="31" r="2.75" fill="#ffffff" />
    <circle cx="29" cy="9" r="2.75" fill="#ffffff" />
    <circle cx="29" cy="31" r="2.75" fill="#ffffff" />
    <circle cx="13" cy="20" r="3.25" fill="#ffffff" className={animated ? "korame-logo-pulse" : undefined} />
    <defs>
      <linearGradient id="korame-logo-gradient" x1="0" y1="0" x2="40" y2="40">
        <stop offset="0%" stopColor="#4d7bff" />
        <stop offset="100%" stopColor="#1f3fae" />
      </linearGradient>
    </defs>
  </svg>
);

export default Logo;
