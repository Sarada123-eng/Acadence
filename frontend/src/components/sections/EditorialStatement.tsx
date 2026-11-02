const hallPhoto =
  "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1300&q=85";

export default function EditorialStatement() {
  return (
    <section className="statement">
      <div className="statement-text">
        <p className="statement-script">
          Classrooms
          <br />
          are more than
          <br />
          roll calls.
        </p>
        <p className="statement-body">
          They're conversations, ideas, mistakes, progress, and people.
        </p>
        <p className="statement-body">
          We built Acadence to remove the friction, so you can focus on what
          actually matters.
        </p>
        <aside className="statement-note">
          Same students.
          <br />A smarter way.
        </aside>
      </div>
      <div className="statement-photo">
        <div className="statement-photo-overlay" />
        <img src={hallPhoto} alt="University lecture hall" />
      </div>
    </section>
  );
}
