import SectionLabel from "../ui/SectionLabel";

export default function WhyAcadence() {
  const principles = [
    {
      num: "01",
      symbol: "⌁",
      title: "AI Where It Helps",
      desc: "Designed to eliminate administrative overhead, not replace human judgment or pedagogy.",
    },
    {
      num: "02",
      symbol: "♢",
      title: "Privacy First",
      desc: "Institutional data remains strictly confidential and encrypted. No training on student submissions.",
    },
    {
      num: "03",
      symbol: "◌",
      title: "Built for Real Classrooms",
      desc: "Tested in high-density lecture halls and lab environments with real network conditions.",
    },
    {
      num: "04",
      symbol: "↗",
      title: "All-in-One Architecture",
      desc: "Attendance, live discussions, assignment distribution, and integrity reports under one roof.",
    },
    {
      num: "05",
      symbol: "□",
      title: "Tactile Simplicity",
      desc: "Clean editorial interfaces with minimal clicks, zero cognitive load, and instant responses.",
    },
    {
      num: "06",
      symbol: "◉",
      title: "Scales with Excellence",
      desc: "From small seminar groups of 10 to massive university lectures of 1,000+ students.",
    },
  ];

  return (
    <section className="why-section" id="why">
      <div className="why-header">
        <SectionLabel>WHY ACADENCE</SectionLabel>
        <h2>
          Thoughtfully <span className="serif-italic">Different.</span>
        </h2>
        <p className="why-intro">
          We designed Acadence from the ground up for academic institutions that value speed, clarity, and human connection over complex enterprise software.
        </p>
      </div>

      <div className="principles-grid">
        {principles.map((p) => (
          <article key={p.title} className="principle-card">
            <div className="principle-num">{p.num}</div>
            <div className="principle-content">
              <h3>
                <span className="principle-icon">{p.symbol}</span> {p.title}
              </h3>
              <p>{p.desc}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
