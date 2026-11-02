export default function IntegrityMockup() {
  return (
    <div className="integrity-mock">
      <div className="similarity-header">
        <b>Similarity Report</b>
        <span className="similarity-score">
          23%<small>Overall Similarity</small>
        </span>
      </div>
      <div className="similarity-bar">
        <div className="similarity-bar-fill" />
      </div>
      {[
        ["Introduction", "4%"],
        ["Methodology", "12%"],
        ["Results", "8%"],
        ["Conclusion", "61%"],
      ].map((row) => (
        <div className="report-row" key={row[0]}>
          <span>{row[0]}</span>
          <b>{row[1]}</b>
        </div>
      ))}
      <div className="flagged-text">
        ...the rapid growth of artificial intelligence has transformed education
        in significant ways, enabling personalised learning experiences and
        intelligent assessment systems...
      </div>
    </div>
  );
}
