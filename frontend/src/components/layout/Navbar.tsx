import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav>
      <a className="logo" href="#top">
        <img
          src="/images/acadence-logo.png"
          alt="Acadence — People, Learning, Integrity"
        />
      </a>
      <div className={open ? "nav-links open" : "nav-links"}>
        <a href="#features">Features</a>
        <a href="#pricing">Pricing</a>
        <a href="#why">About</a>
      </div>
      <button className="menu" onClick={() => setOpen(!open)}>
        MENU
      </button>
      <a className="nav-cta" href="/onboarding">
        Get Started <span>→</span>
      </a>
    </nav>
  );
}
