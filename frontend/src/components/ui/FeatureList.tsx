export default function FeatureList({ items }: { items: string[] }) {
  return (
    <ul className="feature-list">
      {items.map((item, index) => (
        <li key={item}>
          <i>{["◉", "↗", "◌", "□", "◒"][index]}</i>
          {item}
        </li>
      ))}
    </ul>
  );
}
