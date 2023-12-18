interface Props {
  query: string;
}

const Results = ({ query }: Props) => {
  return <div>{query}</div>;
};

export default Results;
