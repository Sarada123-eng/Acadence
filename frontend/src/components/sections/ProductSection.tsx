import type { ReactNode } from "react";
import SectionLabel from "../ui/SectionLabel";
import FeatureList from "../ui/FeatureList";
import HandwrittenNote from "../ui/HandwrittenNote";
type Props = {
  label: string;
  title: ReactNode;
  copy: string;
  features: string[];
  mockup: ReactNode;
  reverse?: boolean;
  note?: string;
};
export default function ProductSection({
  label,
  title,
  copy,
  features,
  mockup,
  reverse,
  note,
}: Props) {
  return (
    <section className={reverse ? "split-section reverse" : "split-section"}>
      <div className="copy">
        <SectionLabel>{label}</SectionLabel>
        <h2>{title}</h2>
        <p>{copy}</p>
        <FeatureList items={features} />
        {note && (
          <HandwrittenNote className="inline-note">{note}</HandwrittenNote>
        )}
      </div>
      <div className="mock-wrap">{mockup}</div>
    </section>
  );
}
