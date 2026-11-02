import SectionLabel from "../ui/SectionLabel";

export default function RolesSection() {
  const roles = [
    {
      symbol: "◕",
      title: "Students",
      tagline: "Engage & Excel",
      desc: "Join active class sessions, submit assignments seamlessly, track your performance, and collaborate with peers in real time.",
      bgNote: "Seamless submission",
    },
    {
      symbol: "◔",
      title: "Professors",
      tagline: "Teach & Inspire",
      desc: "Automate attendance, broadcast assignments, review integrity flags, and spend more time lecturing and mentoring students.",
      bgNote: "Less admin time",
    },
    {
      symbol: "◑",
      title: "Teaching Assistants",
      tagline: "Guide & Support",
      desc: "Assist with grading rubrics, moderate classroom queries, support office hours, and keep track of submission queues.",
      bgNote: "Faster feedback",
    },
  ];

  return (
    <section className="roles-section">
      <div className="roles-header">
        <SectionLabel>FOR EVERY ROLE</SectionLabel>
        <h2>
          Built for Everyone <br />
          <span className="serif-italic">in the Loop.</span>
        </h2>
        <p>
          Different roles. A shared purpose. Acadence adapts specifically to students, professors, and TAs with tailored workflows.
        </p>
      </div>

      <div className="role-cards-grid">
        {roles.map((role) => (
          <article className="role-card" key={role.title}>
            <div className="role-card-top">
              <span className="role-symbol">{role.symbol}</span>
              <span className="role-tagline">{role.tagline}</span>
            </div>
            <h3>{role.title}</h3>
            <p>{role.desc}</p>
            <div className="role-card-footer">
              <span className="handwritten-mini">✦ {role.bgNote}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
