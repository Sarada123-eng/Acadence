import { useState } from "react";

const classroomPhoto =
  "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1200&q=85";

export default function AttendanceMockup() {
  const [marked, setMarked] = useState(false);
  const people = [
    { name: "Aarav Sharma", status: "Present", confidence: "98%" },
    { name: "Diya Patel", status: "Present", confidence: "96%" },
    { name: "Rohan Mehta", status: "Present", confidence: "94%" },
    { name: "Sneha Iyer", status: "Present", confidence: "97%" },
    { name: "Aditya Singh", status: "Present", confidence: "92%" },
    { name: "Kavya Nair", status: "Absent", confidence: "—" },
  ];

  return (
    <div className="attendance-mock">
      <div className="mock-head">
        <strong>LIVE ATTENDANCE</strong>
        <span className="mock-badge">24/28 PRESENT</span>
      </div>
      <div className="attendance-body">
        <div className="class-photo">
          <img src={classroomPhoto} alt="Classroom view for attendance" />
          <span className="scan s1" />
          <span className="scan s2" />
          <span className="scan s3" />
          <span className="scan s4" />
          <span className="camera-icon">📷</span>
        </div>
        <div className="roster">
          {people.map((p) => (
            <div className="person" key={p.name}>
              <span className="person-avatar">{p.name[0]}</span>
              <div className="person-info">
                <span className="person-name">{p.name}</span>
                <span
                  className={
                    p.status === "Absent"
                      ? "person-status person-status--absent"
                      : "person-status person-status--present"
                  }
                >
                  {p.status}
                </span>
              </div>
              {p.status === "Present" && (
                <span className="person-check">✓</span>
              )}
            </div>
          ))}
        </div>
      </div>
      <button
        className={marked ? "mark-btn done" : "mark-btn"}
        onClick={() => setMarked(!marked)}
      >
        {marked ? "Attendance Marked ✓" : "Mark Attendance"}
      </button>
    </div>
  );
}
