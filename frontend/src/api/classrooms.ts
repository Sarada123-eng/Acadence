import { authenticatedRequest } from "./auth";

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

async function request<T>(path: string, init: RequestInit): Promise<T> {
	return authenticatedRequest<T>(path, init);
}

export function createSubject(data: SubjectData) {
	return request<SubjectResponse>("/classrooms/subjects", {
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

export function listTeacherClassrooms() {
	return request<ClassroomResponse[]>("/classrooms", {
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
