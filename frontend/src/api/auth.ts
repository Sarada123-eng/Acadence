const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type TeacherRegistrationData = {
	username: string;
	name: string;
	password: string;
};

export type TeacherRegistrationResponse = {
	id: number;
	username: string;
	name: string;
};

export type TeacherLoginData = {
	username: string;
	password: string;
};

type FastAPIError = {
	detail?: string | Array<{ msg?: string }>;
};

function getErrorMessage(payload: FastAPIError, status: number, fallback: string) {
	if (typeof payload.detail === "string") return payload.detail;
	if (Array.isArray(payload.detail)) {
		const messages = payload.detail.map((item) => item.msg).filter(Boolean);
		if (messages.length > 0) return messages.join(" ");
	}
	if (status === 422) return "Please check the information entered and try again.";
	if (status >= 500) return "The server is unavailable. Please try again.";
	return fallback;
}

export async function registerTeacher(data: TeacherRegistrationData): Promise<TeacherRegistrationResponse> {
	let response: Response;

	try {
		response = await fetch(`${API_BASE_URL}/auth/teacher/register`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(data),
		});
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running and try again.");
	}

	let payload: FastAPIError & Partial<TeacherRegistrationResponse> = {};
	try {
		payload = await response.json();
	} catch {
		// Keep the status-based message when the server returns no JSON body.
	}

	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status, "Registration failed. Please check your details and try again."));
	}

	return payload as TeacherRegistrationResponse;
}

export async function loginTeacher(data: TeacherLoginData): Promise<TeacherRegistrationResponse> {
	let response: Response;

	try {
		response = await fetch(`${API_BASE_URL}/auth/teacher/login`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(data),
		});
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running and try again.");
	}

	let payload: FastAPIError & Partial<TeacherRegistrationResponse> = {};
	try {
		payload = await response.json();
	} catch {
		// Keep the status-based message when the server returns no JSON body.
	}

	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status, "Login failed. Please check your username and password."));
	}

	return payload as TeacherRegistrationResponse;
}
