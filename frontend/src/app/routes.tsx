import { createBrowserRouter } from "react-router";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import NewReport from "./pages/NewReport";
import ReportDetails from "./pages/ReportDetails";
import NotFound from "./pages/NotFound";

export const router = createBrowserRouter([
  {
    path: "/",
    children: [
      { index: true, Component: Home },
      { path: "auth", Component: Auth },
      { path: "dashboard", Component: Dashboard },
      { path: "dashboard/new-report", Component: NewReport },
      { path: "dashboard/report/:id", Component: ReportDetails },
      { path: "*", Component: NotFound },
    ],
  },
]);
