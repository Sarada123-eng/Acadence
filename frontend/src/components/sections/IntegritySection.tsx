import IntegrityMockup from "../mockups/IntegrityMockup";

export default function IntegritySection() {
  return (
    <section className="product-section product-section--integrity">
      <div className="product-copy">
        <span className="eyebrow-pill">ACADEMIC INTEGRITY</span>
        <h2>
          Promote Original
          <br />
          <span className="serif-italic">Thinking.</span>
        </h2>
        <p>
          Our AI-powered analysis helps you review submissions and handwritten exam copies for potential similarities while maintaining total transparency.
        </p>
        <ul className="feature-list">
          <li>
            <span className="bullet-dash">—</span> Text and semantic similarity detection
          </li>
          <li>
            <span className="bullet-dash">—</span> Support for PDFs, docs and handwritten OCR
          </li>
          <li>
            <span className="bullet-dash">—</span> Detailed side-by-side similarity reports
          </li>
          <li>
            <span className="bullet-dash">—</span> Compare across class and external sources
          </li>
        </ul>
        <aside className="note note--coral" style={{ marginTop: "24px" }}>
          Flagged —
          <br />
          23% overall similarity
          <br />
          with external source.
        </aside>
      </div>

      <div className="product-mockup-wrapper">
        <div className="mockup-frame">
          <IntegrityMockup />
        </div>
      </div>
    </section>
  );
}

