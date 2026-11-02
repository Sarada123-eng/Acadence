import { useState } from "react";

export default function ClassroomMockup() {
  const [tab, setTab] = useState("Chat");
  return (
    <div className="classroom-mock">
      <h3>Data Structures</h3>
      <div className="tabs">
        {["Classroom", "Assignments", "People", "Chat"].map((item) => (
          <button
            key={item}
            onClick={() => setTab(item)}
            className={tab === item ? "active" : ""}
          >
            {item}
          </button>
        ))}
      </div>
      {tab === "Chat" ? (
        <>
          <div className="chat-messages">
            <p>
              <b>
                Prof. Iyer<small>10:21 AM</small>
              </b>
              Assignment 2 is now live!
            </p>
            <p>
              <b>
                Ananya<small>10:30 AM</small>
              </b>
              Will the solutions be discussed in the next class?
            </p>
            <p>
              <b>
                Prof. Iyer<small>10:42 AM</small>
              </b>
              Yes, we'll go through them on Friday.
            </p>
          </div>
          <div className="chat-input">
            Type a message... <span>◉</span>
          </div>
        </>
      ) : (
        <div className="tab-placeholder">
          {tab}
          <small>Everything your class needs, in one calm place.</small>
        </div>
      )}
    </div>
  );
}
