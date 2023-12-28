import axios from "axios";

interface Props {
  fetchQuery: string;
  setQuery: Function;
  setComparisonResult: Function;
}

const QueryBox = ({ fetchQuery, setQuery, setComparisonResult }: Props) => {
  const handleSubmit = (event: React.ChangeEvent<HTMLFormElement>) => {
    event.preventDefault();

    const getLtlaList = async () => {
      try {
        setComparisonResult("Loading...");

        axios({
          method: "get",
          url: import.meta.env.VITE_API_PATH + "/compare/?topic=" + fetchQuery,
        }).then(function (response) {
          setComparisonResult(response.data.replace(/(?:\r\n|\r|\n)/g, "<br>"));
        });
      } catch (err) {
        setComparisonResult("Error");
      }
    };
    getLtlaList();
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        onChange={(e) => setQuery(e.target.value)}
        value={fetchQuery}
      ></input>
      <button type="submit">Click to submit</button>
    </form>
  );
};

export default QueryBox;
