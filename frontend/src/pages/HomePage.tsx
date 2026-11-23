import type { FC } from "react";
import { Link } from "react-router-dom";
import Logo from "../components/common/Logo";

/** Minimal landing page introducing Korame and linking to the two main flows. */
const HomePage: FC = () => (
  <div className="korame-hero-section">
    <div className="korame-hero">
      <Logo size={56} />
      <h1 className="korame-hero-title">Korame</h1>
      <p className="korame-hero-subtitle">
        Describe what the business needs in plain language. The RTE agent turns it into a clear,
        ready-to-build user story - asking questions only when it genuinely needs to, and drawing on
        similar past requirements to suggest useful patterns.
      </p>
      <div className="korame-hero-actions">
        <Link to="/rte" className="korame-btn korame-btn-primary">
          Start a requirement &rarr;
        </Link>
        <Link to="/requirements" className="korame-btn korame-btn-secondary">
          Browse requirements
        </Link>
      </div>
    </div>
  </div>
);

export default HomePage;
