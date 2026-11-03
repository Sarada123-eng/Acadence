import "./RoleSelectionPage.css";
import AcadenceLogo from "../components/onboarding/AcadenceLogo";
import HandwrittenNote from "../components/onboarding/HandwrittenNote";
import RoleCard from "../components/onboarding/RoleCard";

export default function RoleSelectionPage() {
  const selectRole = (role: "student" | "teacher") => window.location.assign(`/auth/${role}`);

  return (
    <main className="onboarding-page">
      <AcadenceLogo />
      <HandwrittenNote className="onboarding-note--top">More<br />Learning.<br />Less<br />Admin.<span className="note-underline" /></HandwrittenNote>
      <HandwrittenNote className="onboarding-note--bottom">Real<br />Classrooms.<br />Real Impact.<span className="note-underline" /></HandwrittenNote>
      <div className="onboarding-leaf" aria-hidden="true">╱╲<br />╲╱</div>

      <section className="onboarding-content" aria-labelledby="role-heading">
        <p className="onboarding-eyebrow">WELCOME TO ACADENCE</p>
        <span className="heading-mark" aria-hidden="true" />
        <h1 id="role-heading">How will you be using<br />Acadence?</h1>
        <p className="onboarding-subtitle">Choose a role to continue. You can always switch later.</p>
        <div className="role-choices">
          <RoleCard role="student" onSelect={selectRole} />
          <RoleCard role="teacher" onSelect={selectRole} />
        </div>
        <p className="login-prompt"><span>Have a classroom code?</span><a href="/join">Join a classroom</a></p>
        <div className="login-prompt"><span>Already have an account?</span><a href="/login">Log in</a></div>
      </section>

      <div className="onboarding-signature">PEOPLE<br />LEARNING<br />INTEGRITY<span className="note-underline" /></div>
    </main>
  );
}