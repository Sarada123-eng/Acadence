import type { ReactNode } from "react";
export default function Button({
  children,
  ghost = false,
}: {
  children: ReactNode;
  ghost?: boolean;
}) {
  return (
    <button className={ghost ? "button ghost" : "button"}>{children}</button>
  );
}
