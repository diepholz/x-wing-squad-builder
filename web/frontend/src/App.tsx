import { Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import HomePage from "./pages/HomePage";
import BuilderPage from "./pages/BuilderPage";
import MySquadsPage from "./pages/MySquadsPage";
import SharePage from "./pages/SharePage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="build" element={<BuilderPage />} />
        <Route path="squads" element={<MySquadsPage />} />
      </Route>
      <Route path="/share/:token" element={<SharePage />} />
    </Routes>
  );
}
