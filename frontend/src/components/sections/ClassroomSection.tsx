import ClassroomMockup from "../mockups/ClassroomMockup";

export default function ClassroomSection() {
  return (
    <section className="product-section product-section--classroom">
      <div className="product-copy">
        <span className="label">CLASSROOMS</span>
        <h2>
          A Classroom
          <br />
          That Just Works.
        </h2>
        <p>
          Create a class, share a code, and bring everyone together. Share
          materials, post assignments, have discussions — everything in one
          place.
        </p>
        <ul className="feature-list">
          <li>
            <i>◉</i> Create and manage classrooms
          </li>
          <li>
            <i>↗</i> Join with a simple code
          </li>
          <li>
            <i>◌</i> Share announcements & materials
          </li>
          <li>
            <i>□</i> Built-in chat
          </li>
          <li>
            <i>◒</i> Track progress and engagement
          </li>
        </ul>
        <aside
          className="note note--mustard"
          style={{ marginTop: "20px", transform: "rotate(3deg)", display: "inline-block" }}
        >
          Your classroom.
          <br />
          Your way. Always.
        </aside>
      </div>
      <div className="product-mockup-area" style={{ position: "relative" }}>
        <ClassroomMockup />
        <aside
          className="note note--tape classroom-float-note"
          style={{ fontSize: "14px" }}
        >
          Your classroom
          <br />
          without
          <br />
          the chaos.
        </aside>
      </div>
    </section>
  );
}
