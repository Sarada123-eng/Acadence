import "./globals.css";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";
import Hero from "../components/hero/Hero";
import EditorialStatement from "../components/sections/EditorialStatement";
import AttendanceSection from "../components/sections/AttendanceSection";
import ClassroomSection from "../components/sections/ClassroomSection";
import AssignmentsSection from "../components/sections/AssignmentsSection";
import IntegritySection from "../components/sections/IntegritySection";
import RolesSection from "../components/sections/RolesSection";
import WhyAcadence from "../components/sections/WhyAcadence";
import FinalCTA from "../components/sections/FinalCTA";

export default function Page() {
  return (
    <main>
      <section className="hero" id="top">
        <Navbar />
        <Hero />
      </section>
      <EditorialStatement />
      <div id="features">
        <AttendanceSection />
        <ClassroomSection />
        <AssignmentsSection />
        <IntegritySection />
      </div>
      <RolesSection />
      <WhyAcadence />
      <FinalCTA />
      <Footer />
    </main>
  );
}
