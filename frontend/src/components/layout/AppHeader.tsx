import type { FC } from "react";
import type { CSSProperties } from "react";
import { NavLink } from "react-router-dom";
import Logo from "../common/Logo";

const navLinkStyle = ({ isActive }: { isActive: boolean }): CSSProperties => ({
  padding: "6px 12px",
  borderRadius: 8,
  fontSize: 14,
  fontWeight: 500,
  textDecoration: "none",
  color: isActive ? "#2f5bea" : "#5b6270",
  background: isActive ? "rgba(47, 91, 234, 0.08)" : "transparent",
  transition: "background-color 0.15s ease, color 0.15s ease",
});

/** Sticky top-level app header: logo/wordmark + primary navigation. */
const AppHeader: FC = () => {
  return (
    <header className="korame-header">
      <div className="korame-header-inner">
        <NavLink to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
          <Logo size={30} />
          <span style={{ fontSize: 16, fontWeight: 700, letterSpacing: "-0.01em", color: "#1b1f27" }}>Korame</span>
        </NavLink>
        <nav style={{ display: "flex", gap: 4 }}>
          <NavLink to="/" style={navLinkStyle} end>
            Home
          </NavLink>
          <NavLink to="/rte" style={navLinkStyle}>
            RTE - Requirements
          </NavLink>
          <NavLink to="/requirements" style={navLinkStyle}>
            Requirements
          </NavLink>
        </nav>
      </div>
    </header>
  );
};

export default AppHeader;
