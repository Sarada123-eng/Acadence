const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type SubjectData = {
	name: string;
	subject_code: string;
	section?: string;
};

export type SubjectResponse = SubjectData & {
	id: number;
	teacher_id: number | null;
};

export type ClassroomData = {
	name: string;
	section?: string;
};

export type ClassroomResponse = ClassroomData & {
	id: number;
	subject_id: number;
	join_code: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
};

type ApiError = { detail?: string };

async function request<T>(path: string, init: RequestInit): Promise<T> {
	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}${path}`, init);
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running.");
	}

	let payload: ApiError & Partial<T> = {};
	try {
		payload = await response.json();
	} catch {
		// The status-based error below is used when the server has no JSON body.
	}

	if (!response.ok) {
		throw new Error(payload.detail ?? "The request could not be completed.");
	}
	return payload as T;
}

export function createSubject(teacherId: number, data: SubjectData) {
	return request<SubjectResponse>(`/classrooms/teachers/${teacherId}/subjects`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	});
}

export function createClassroom(subjectId: number, data: ClassroomData) {
	return request<ClassroomResponse>(`/classrooms/subjects/${subjectId}/classrooms`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	});
}

export function listTeacherClassrooms(teacherId: number) {
	return request<ClassroomResponse[]>(`/classrooms/teachers/${teacherId}`, {
		method: "GET",
	});
}

export function joinClassroom(studentId: number, joinCode: string) {
	return request<{ classroom_id: number; student_id: number; joined: boolean; message: string }>("/classrooms/join", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ student_id: studentId, join_code: joinCode }),
	});
}
