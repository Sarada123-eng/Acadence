import type { ReactNode } from "react";
export default function HandwrittenNote({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <aside className={"note " + className}>{children}</aside>;
}
