import "bootstrap/dist/css/bootstrap.min.css";
import { useState } from "react";
import QueryBox from "./components/QueryBox";
import Results from "./components/Results";
import "./App.css";

function App() {
  const [fetchQuery, setQuery] = useState("");
  const [fetchComparisonResult, setComparisonResult] = useState("");

  return (
    <>
      <div className="container">
        <p>
          Type a topic into the below box to get a comparison of Southwark,
          Tower Hamlets and Islington's planning approaches.
        </p>

        <p>Examples: 'Increasing housing supply', 'net biodiversity gain'</p>
        <QueryBox
          fetchQuery={fetchQuery}
          setQuery={setQuery}
          setComparisonResult={setComparisonResult}
        ></QueryBox>
        <Results fetchComparisonResult={fetchComparisonResult}></Results>
      </div>
    </>
  );
}

export default App;
