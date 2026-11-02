import type { KeyboardEvent } from "react";
import RoleIllustration from "./RoleIllustration";

type Role = "student" | "teacher";

const roleDetails: Record<Role, { title: string; description: string }> = {
  student: { title: "Student", description: "Join classes, track attendance, submit assignments, and be part of your learning journey." },
  teacher: { title: "Teacher", description: "Create and manage classrooms, take attendance, set assignments, and engage with your students." },
};

export default function RoleCard({ role, onSelect }: { role: Role; onSelect: (role: Role) => void }) {
  const details = roleDetails[role];
  const activate = () => onSelect(role);
  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      activate();
    }
  };

  return (
    <article className={`role-choice role-choice--${role}`} tabIndex={0} onClick={activate} onKeyDown={handleKeyDown}>
      <div className="role-art"><RoleIllustration role={role} /></div>
      <h2>{details.title}</h2>
      <p>{details.description}</p>
      <button type="button" onClick={(event) => { event.stopPropagation(); activate(); }}>
        Continue as {details.title} <span aria-hidden="true">→</span>
      </button>
    </article>
  );
}