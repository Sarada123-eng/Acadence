export default function RoleIllustration({ role }: { role: "student" | "teacher" }) {
  if (role === "student") {
    return (
      <svg className="role-illustration" viewBox="0 0 190 112" role="img" aria-label="Books and graduation cap">
        <ellipse cx="95" cy="61" rx="57" ry="45" fill="#e8ede5" />
        <path d="M54 74h74v10H54zM59 62h64v12H59zM63 50h57v12H63z" fill="#faf8f2" stroke="#102238" strokeWidth="2" />
        <path d="m53 43 43-13 43 13-43 14z" fill="#d7e8ed" stroke="#102238" strokeWidth="2" strokeLinejoin="round" />
        <path d="M96 44v12m43-13v19" stroke="#102238" strokeWidth="2" />
        <circle cx="139" cy="71" r="3" fill="#d8a62a" />
        <path d="M40 53h-9m12 10-7 5m112-18 8-4" stroke="#29493f" strokeWidth="2" strokeLinecap="round" />
      </svg>
    );
  }

  return (
    <svg className="role-illustration" viewBox="0 0 190 112" role="img" aria-label="Document and pencil">
      <ellipse cx="95" cy="61" rx="57" ry="45" fill="#ebc9bd" opacity=".72" />
      <rect x="48" y="31" width="77" height="56" rx="3" fill="#faf8f2" stroke="#102238" strokeWidth="2" />
      <path d="M61 47h50M61 59h42M61 71h31" stroke="#29493f" strokeWidth="2" strokeLinecap="round" />
      <path d="m137 37 12 5-20 48-12-5z" fill="#d8a62a" stroke="#102238" strokeWidth="2" />
      <path d="m117 85-3 9 9-5" fill="#faf8f2" stroke="#102238" strokeWidth="2" />
      <path d="m137 37 4-7 12 5-4 7" fill="#d7e8ed" stroke="#102238" strokeWidth="2" />
    </svg>
  );
}