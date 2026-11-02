const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type StudentRegistrationData = {
	name: string;
};

export type StudentRegistrationResponse = {
	id: number;
	name: string;
	face_embedding_enrolled: boolean;
	voice_embedding_enrolled: boolean;
};

type FastAPIError = {
	detail?: string | Array<{ msg?: string }>;
};

function getErrorMessage(payload: FastAPIError, status: number) {
	if (typeof payload.detail === "string") return payload.detail;
	if (Array.isArray(payload.detail)) {
		const messages = payload.detail.map((item) => item.msg).filter(Boolean);
		if (messages.length > 0) return messages.join(" ");
	}
	if (status === 422) return "Please enter a valid full name and try again.";
	if (status >= 500) return "The server is unavailable. Please try again.";
	return "Unable to save your name. Please try again.";
}

export async function registerStudent(data: StudentRegistrationData): Promise<StudentRegistrationResponse> {
	let response: Response;

	try {
		response = await fetch(`${API_BASE_URL}/students`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(data),
		});
	} catch {
		throw new Error("Unable to reach Acadence. Please check that the server is running and try again.");
	}

	let payload: FastAPIError & Partial<StudentRegistrationResponse> = {};
	try {
		payload = await response.json();
	} catch {
		// Keep the status-based message when the server returns no JSON body.
	}

	if (!response.ok) {
		throw new Error(getErrorMessage(payload, response.status));
	}

	return payload as StudentRegistrationResponse;
}