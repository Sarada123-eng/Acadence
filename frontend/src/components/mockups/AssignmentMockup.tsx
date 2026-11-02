export default function AssignmentMockup() {
  const rows = [
    { name: "Rohan Mehta", file: "submitted.pdf", status: "On time" },
    { name: "Diya Patel", file: "assignment2.pdf", status: "On time" },
    { name: "Aarav Sharma", file: "ds_a2.pdf", status: "Late" },
    { name: "Kavya Nair", file: "a2_final.pdf", status: "On time" },
    { name: "Sneha Iyer", file: "a2.pdf", status: "On time" },
  ];

  return (
    <div className="assignment-mock">
      <h3>Assignment 2</h3>
      <p className="due-date">
        Due <b>Oct 5, 2024</b> · 11:59 PM
      </p>
      <div className="assignment-tabs">
        Submissions <span>Insights</span>
      </div>
      {rows.map((row) => (
        <div className="submission" key={row.name}>
          <span className="person-avatar">{row.name[0]}</span>
          <b>{row.name}</b>
          <span>{row.file}</span>
          <small className={row.status === "Late" ? "late" : ""}>
            {row.status}
          </small>
        </div>
      ))}
      <button className="grade-btn">Grade All</button>
    </div>
  );
}
