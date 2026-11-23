import type { FC } from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import AppHeader from "../components/layout/AppHeader";
import HomePage from "../pages/HomePage";
import RTEPage from "../pages/RTEPage";
import RequirementsPage from "../pages/RequirementsPage";
import WorkflowPage from "../pages/WorkflowPage";
import StoryRunPage from "../pages/StoryRunPage";

/**
 * Rendered inside <BrowserRouter> so it can read the current location. Keying
 * <main> on the pathname forces React to remount it on every page change,
 * which is what actually re-triggers the CSS fade-in animation - without the
 * key, React just swaps the Route's children in place and the animation
 * (tied to the element's initial mount) never replays after the first load.
 */
const AppShell: FC = () => {
  const location = useLocation();

  return (
    <>
      <AppHeader />
      <main key={location.pathname} className="korame-page-fade">
        <Routes>
          <Route path="/rte" element={<RTEPage />} />
          <Route path="/requirements" element={<RequirementsPage />} />
          <Route path="/workflow" element={<WorkflowPage />} />
          <Route path="/story-run" element={<StoryRunPage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </main>
    </>
  );
};

const AppRoutes: FC = () => {
  return (
	<BrowserRouter>
	  <AppShell />
	</BrowserRouter>
  );
};

export default AppRoutes;


