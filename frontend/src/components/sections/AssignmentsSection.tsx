import AssignmentMockup from "../mockups/AssignmentMockup";

export default function AssignmentsSection() {
  return (
    <section className="product-section product-section--assignments">
      <div className="product-copy">
        <span className="eyebrow-pill">ASSIGNMENTS</span>
        <h2>
          Manage Work.
          <br />
          <span className="serif-italic">Not Workflows.</span>
        </h2>
        <p>
          Upload assignments, set deadlines, collect submissions, and provide feedback — all in one smooth flow without administrative clutter.
        </p>
        <ul className="feature-list">
          <li>
            <span className="bullet-dash">—</span> Easy assignment creation & publishing
          </li>
          <li>
            <span className="bullet-dash">—</span> File submissions and version tracking
          </li>
          <li>
            <span className="bullet-dash">—</span> Automated grading workflows & feedback
          </li>
          <li>
            <span className="bullet-dash">—</span> Full visibility for students, faculty & TAs
          </li>
        </ul>
        <aside className="note note--mustard" style={{ marginTop: "24px" }}>
          From submission to feedback,
          <br />
          without the back and forth.
        </aside>
      </div>

      <div className="product-mockup-wrapper">
        <div className="mockup-frame">
          <AssignmentMockup />
        </div>
      </div>
    </section>
  );
}

