import "bootstrap/dist/css/bootstrap.min.css";
import { useState } from "react";
import QueryBox from "./components/QueryBox";
import Results from "./components/Results";
import "./App.css";

function App() {
  const [fetchQuery, setQuery] = useState("");

  return (
    <>
      <div className="flex-grid">
        <QueryBox fetchQuery={fetchQuery} setQuery={setQuery}></QueryBox>
        <Results query={fetchQuery}></Results>
      </div>
    </>
  );
}

export default App;
