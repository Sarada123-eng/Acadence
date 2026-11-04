import { useEffect, useState, type FormEvent } from "react";
import { getCurrentTeacher } from "../api/auth";
import { createClassroom, createSubject, listTeacherClassrooms, type ClassroomResponse } from "../api/classrooms";

export default function TeacherDashboardPage() {
	const [classrooms, setClassrooms] = useState<ClassroomResponse[]>([]);
	const [subjectName, setSubjectName] = useState("");
	const [subjectCode, setSubjectCode] = useState("");
	const [classroomName, setClassroomName] = useState("");
	const [message, setMessage] = useState("");
	const [error, setError] = useState("");

	useEffect(() => {
		getCurrentTeacher()
			.then(() => listTeacherClassrooms())
			.then(setClassrooms)
			.catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "Unable to load classrooms."));
	}, []);

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		setError("");
		setMessage("");
		try {
			const subject = await createSubject({ name: subjectName.trim(), subject_code: subjectCode.trim() });
			const classroom = await createClassroom(subject.id, { name: classroomName.trim() });
			setClassrooms((current) => [...current, classroom]);
			setMessage(`Classroom created. Join code: ${classroom.join_code}`);
			setSubjectName("");
			setSubjectCode("");
			setClassroomName("");
		} catch (reason: unknown) {
			setError(reason instanceof Error ? reason.message : "Unable to create classroom.");
		}
	}

	return (
		<main className="classroom-entry">
			<section className="classroom-entry__card">
				<a href="/" className="classroom-entry__logo">Acadence</a>
				<p className="classroom-entry__eyebrow">TEACHER CLASSROOMS</p>
				<h1>Create a classroom</h1>
				<form onSubmit={handleSubmit}>
					<label htmlFor="subject-name">Subject name</label>
					<input id="subject-name" value={subjectName} onChange={(event) => setSubjectName(event.target.value)} required />
					<label htmlFor="subject-code">Subject code</label>
					<input id="subject-code" value={subjectCode} onChange={(event) => setSubjectCode(event.target.value)} required />
					<label htmlFor="classroom-name">Classroom name</label>
					<input id="classroom-name" value={classroomName} onChange={(event) => setClassroomName(event.target.value)} required />
					{error && <p className="classroom-entry__error" role="alert">{error}</p>}
					{message && <p role="status">{message}</p>}
					<button type="submit">Create classroom</button>
				</form>
				<h2>Existing classrooms</h2>
				<ul>{classrooms.map((classroom) => <li key={classroom.id}>{classroom.name} — {classroom.join_code}</li>)}</ul>
			</section>
		</main>
	);
}
