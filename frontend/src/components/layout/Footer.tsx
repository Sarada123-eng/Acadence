export default function Footer() {
  return (
    <footer>
      <div style={{ display: "flex", alignItems: "center" }}>
        <a className="logo" href="#top">
          <img
            src="/images/acadence-logo.png"
            alt="Acadence — People, Learning, Integrity"
          />
        </a>
        <span className="footer-tagline">PEOPLE · LEARNING · INTEGRITY</span>
      </div>
      <div className="footer-links">
        <a href="#features">Features</a>
        <a href="#why">Privacy</a>
        <a href="#top">Terms</a>
        <a href="#contact">Contact</a>
      </div>
      <div className="footer-social">
        <span>◌</span>
        <span>◇</span>
        <span>◉</span>
      </div>
    </footer>
  );
}
