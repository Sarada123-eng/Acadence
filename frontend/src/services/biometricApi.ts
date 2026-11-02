const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function uploadFace(studentId: string, imageBlob: Blob): Promise<void> {
	const formData = new FormData();
	formData.append("image", imageBlob, "face.jpg");

	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}/students/${studentId}/face/enroll`, {
			method: "POST",
			body: formData,
		});
	} catch {
		throw new Error("Unable to connect to Acadence. Please check your connection and try again.");
	}

	if (!response.ok) {
		let message = "Face registration failed. Please try again.";
		try {
			const payload = await response.json();
			if (typeof payload.detail === "string") message = payload.detail;
		} catch {
			// use default message
		}
		throw new Error(message);
	}
}

export async function uploadVoice(studentId: string, audioBlob: Blob): Promise<void> {
	const formData = new FormData();
	formData.append("audio", audioBlob, "voice.wav");

	let response: Response;
	try {
		response = await fetch(`${API_BASE_URL}/students/${studentId}/voice/enroll`, {
			method: "POST",
			body: formData,
		});
	} catch {
		throw new Error("Unable to connect to Acadence. Please check your connection and try again.");
	}

	if (!response.ok) {
		let message = "Voice registration failed. Please try again.";
		try {
			const payload = await response.json();
			if (typeof payload.detail === "string") message = payload.detail;
		} catch {
			// use default message
		}
		throw new Error(message);
	}
}
