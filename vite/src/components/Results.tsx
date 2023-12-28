interface Props {
  fetchComparisonResult: string;
}

const Results = ({ fetchComparisonResult }: Props) => {
  return (
    <div dangerouslySetInnerHTML={{ __html: fetchComparisonResult }}></div>
  );
};

export default Results;
