import type { FC } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RTEPage from "../pages/RTEPage";

const AppRoutes: FC = () => {
  return (
	<BrowserRouter>
	  <nav style={{ padding: 8, borderBottom: "1px solid #eee" }}>
		<Link to="/">Home</Link>
		<span style={{ margin: "0 8px" }}>|</span>
		<Link to="/rte">RTE - Requirements</Link>
	  </nav>
	  <Routes>
		<Route path="/rte" element={<RTEPage />} />
		<Route
		  path="/"
		  element={
			<div style={{ padding: 20 }}>
			  <h2>Welcome</h2>
			  <p>
				Use the <Link to="/rte">RTE - Requirements</Link> page to submit a business
				requirement and receive clarifying questions or a response from the RTE agent.
			  </p>
			</div>
		  }
		/>
	  </Routes>
	</BrowserRouter>
  );
};

export default AppRoutes;


