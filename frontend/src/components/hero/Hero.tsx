const classroomPhoto =
  "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=85";
const hallPhoto =
  "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1300&q=85";

export default function Hero() {
  return (
    <section className="hero-section" id="top">
      <div className="hero-grid">
        {/* ─── LEFT: Editorial headline ─── */}
        <div className="hero-left anim-fade-up">
          <p className="eyebrow">AI-POWERED ACADEMIC PLATFORM</p>
          <h1>
            More Learning.
            <br />
            <span className="underline-mustard">Less Admin.</span>
          </h1>
          <p className="hero-desc">
            An AI-powered academic platform for modern classrooms.
            <br />
            Attendance. Assignments. Academic Integrity.
            <br />
            All in one place.
          </p>
          <div className="buttons">
            <button className="button">
              Create Your Classroom <span>→</span>
            </button>
            <button className="button ghost">Watch Demo ◉</button>
          </div>
          <aside
            className="note note--forest hero-note-left anim-fade-up anim-delay-4"
            style={{ fontSize: "16px" }}
          >
            Built for
            <br />
            Real Classrooms.
            <br />
            Not just screens.
          </aside>
        </div>

        {/* ─── RIGHT: Photo collage ─── */}
        <div className="hero-images anim-fade-up anim-delay-2">
          {/* Tape note */}
          <div className="hero-tape">
            <aside className="note note--tape" style={{ transform: "rotate(-8deg)" }}>
              Same People
              <br />
              Brighter
              <br />
              Possibilities.
            </aside>
          </div>

          {/* Main polaroid */}
          <div className="hero-polaroid-main polaroid">
            <img
              src={classroomPhoto}
              alt="Students gathered in a university classroom"
              style={{ height: "260px", objectFit: "cover" }}
            />
            <span className="polaroid-caption">Today's class, less admin.</span>
          </div>

          {/* Background photo */}
          <div className="hero-photo-back">
            <img src={hallPhoto} alt="University hall" />
          </div>

          {/* Bottom-left handwritten note */}
          <aside className="note note--mustard hero-note-right">
            Attendance
            <br />
            done in seconds.
            <br />
            Time back for what
            <br />
            really matters.
          </aside>

          {/* Doodle annotation */}
          <div className="hero-doodle">
            ✦ where learning
            <br />
            &nbsp;&nbsp;comes first
          </div>
        </div>
      </div>

      {/* ─── Proof points ─── */}
      <div className="proof-bar anim-fade-up anim-delay-3">
        <div className="proof-item">
          <span className="proof-big">10×</span>
          <span className="proof-small">Faster Attendance</span>
        </div>
        <div className="proof-item">
          <span className="proof-big">Secure</span>
          <span className="proof-small">& Private</span>
        </div>
        <div className="proof-item">
          <span className="proof-big">All-in-One</span>
          <span className="proof-small">Platform</span>
        </div>
        <div className="proof-item">
          <span className="proof-big">Designed for</span>
          <span className="proof-small">Students, Faculty & TAs</span>
        </div>
      </div>
    </section>
  );
}
