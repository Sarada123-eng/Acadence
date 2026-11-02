import AttendanceMockup from "../mockups/AttendanceMockup";

export default function AttendanceSection() {
  return (
    <section className="product-section product-section--attendance" id="features">
      <div className="product-copy">
        <span className="label">ATTENDANCE</span>
        <h2>
          Take Attendance
          <br />
          in Seconds.
        </h2>
        <p>
          Just capture a photo or use your voice — Acadence identifies who's
          present, accurately and securely.
        </p>
        <ul className="feature-list">
          <li>
            <i>◉</i> Face recognition from class photos
          </li>
          <li>
            <i>↗</i> Voice-based attendance (optional)
          </li>
          <li>
            <i>◌</i> Confidence scores with manual review
          </li>
          <li>
            <i>□</i> Detailed attendance history
          </li>
        </ul>
        <aside className="note note--forest product-note">
          Spends less time
          <br />
          on roll calls.
          <br />
          More time on
          <br />
          real teaching.
        </aside>
      </div>
      <div className="product-mockup-area">
        <AttendanceMockup />
      </div>
    </section>
  );
}
