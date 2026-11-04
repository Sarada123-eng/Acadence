const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const ACCESS_TOKEN_KEY = "acadence.accessToken";

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

export type TeacherProfile = TeacherRegistrationResponse;

export type TeacherLoginResponse = TeacherProfile & {
	access_token: string;
	token_type: string;
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

export async function loginTeacher(data: TeacherLoginData): Promise<TeacherLoginResponse> {
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

	let payload: FastAPIError & Partial<TeacherLoginResponse> = {};
	try {
		payload = await response.json();
	} catch {
		// Keep the status-based message when the server returns no JSON body.
	}

	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status, "Login failed. Please check your username and password."));
	}

	return payload as TeacherLoginResponse;
}

export function getAccessToken() {
	return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(accessToken: string) {
	// Development uses sessionStorage; production should prefer an HTTP-only,
	// Secure cookie with appropriate CSRF protection.
	sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}

export function clearAuthSession() {
	sessionStorage.removeItem(ACCESS_TOKEN_KEY);
	sessionStorage.removeItem("acadence.teacherName");
}

export async function authenticatedRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
	const token = getAccessToken();
	const headers = new Headers(init.headers);
	headers.set("Authorization", `Bearer ${token ?? ""}`);

	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running.");
	}

	let payload: FastAPIError & Partial<T> = {};
	try {
		payload = await response.json();
	} catch {
		// The status-based error below is used when the server has no JSON body.
	}

	if (response.status === 401) {
		clearAuthSession();
		window.location.assign("/login");
		throw new Error("Your teacher session has expired. Please log in again.");
	}
	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status, "The request could not be completed."));
	}
	return payload as T;
}

export async function publicRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}${path}`, init);
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running.");
	}

	let payload: FastAPIError & Partial<T> = {};
	try {
		payload = await response.json();
	} catch {
		// The status-based error below is used when the server has no JSON body.
	}

	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status, "The request could not be completed."));
	}
	return payload as T;
}

export function getCurrentTeacher() {
	return authenticatedRequest<TeacherProfile>("/auth/teacher/me");
}
