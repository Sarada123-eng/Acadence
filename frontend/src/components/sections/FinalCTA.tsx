const desk =
  "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1000&q=85";

export default function FinalCTA() {
  return (
    <section className="final-cta-section" id="contact">
      <div className="final-cta-container">
        <div
          className="final-cta-photo polaroid"
          style={{ transform: "rotate(-2deg)" }}
        >
          <img src={desk} alt="University study desk with notebooks and coffee" />
          <div className="polaroid-caption">
            Same students. Brighter possibilities.
          </div>
        </div>

        <div className="final-cta-content">
          <span className="eyebrow-pill">GET STARTED</span>
          <h2>
            Let’s Build <br />
            <span className="serif-italic">Brighter</span> Classrooms.
          </h2>
          <p>
            Join educators and students who are already reimagining academic life with Acadence. Simple setup, instant value.
          </p>

          <div className="cta-actions">
            <a className="button" href="/onboarding">
              Get Started for Free <span>→</span>
            </a>
            <button className="button ghost">Request a Faculty Demo</button>
          </div>

          <aside className="note note--mustard" style={{ marginTop: "24px", transform: "rotate(2deg)" }}>
            More Learning.
            <br />
            Less Admin.
          </aside>
        </div>
      </div>
    </section>
  );
}
