interface Props {
  fetchQuery: string;
  setQuery: Function;
}

const QueryBox = ({ fetchQuery, setQuery }: Props) => {
  const handleSubmit = (event: React.ChangeEvent<HTMLFormElement>) => {
    event.preventDefault();
    alert(fetchQuery);
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
