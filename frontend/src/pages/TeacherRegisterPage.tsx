import { useState, type FormEvent } from "react";
import { registerTeacher } from "../api/auth";
import FormField from "../components/auth/FormField";
import PasswordField from "../components/auth/PasswordField";
import HandwrittenNote from "../components/onboarding/HandwrittenNote";
import "./TeacherRegisterPage.css";

type FormValues = { username: string; name: string; password: string; confirmPassword: string };
type FieldName = keyof FormValues;
type FormErrors = Partial<Record<FieldName, string>>;

const initialValues: FormValues = { username: "", name: "", password: "", confirmPassword: "" };

function validate(values: FormValues): FormErrors {
	const errors: FormErrors = {};
	if (!values.username.trim()) errors.username = "Username is required.";
	else if (!/^[a-zA-Z0-9._-]{3,20}$/.test(values.username.trim())) errors.username = "Use 3–20 letters, numbers, dots, hyphens, or underscores.";
	if (!values.name.trim()) errors.name = "Name is required.";
	if (!values.password) errors.password = "Password is required.";
	else if (values.password.length < 8) errors.password = "Password must be at least 8 characters.";
	if (!values.confirmPassword) errors.confirmPassword = "Please confirm your password.";
	else if (values.confirmPassword !== values.password) errors.confirmPassword = "Passwords do not match.";
	return errors;
}

export default function TeacherRegisterPage() {
	const [values, setValues] = useState(initialValues);
	const [touched, setTouched] = useState<Partial<Record<FieldName, boolean>>>({});
	const [submitted, setSubmitted] = useState(false);
	const [isCreating, setIsCreating] = useState(false);
	const [apiError, setApiError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const errors = validate(values);

	const updateField = (field: FieldName, value: string) => setValues((current) => ({ ...current, [field]: value }));
	const fieldError = (field: FieldName) => (touched[field] || submitted ? errors[field] : undefined);

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		if (isCreating) return;
		setApiError("");
		setSuccessMessage("");
		setSubmitted(true);
		if (Object.keys(errors).length > 0) return;

		setIsCreating(true);
		try {
			await registerTeacher({
				username: values.username.trim(),
				name: values.name.trim(),
				password: values.password,
			});
			setSuccessMessage("Your teacher account was created. Redirecting to login…");
			window.setTimeout(() => window.location.assign("/login"), 900);
		} catch (error) {
			setApiError(error instanceof Error ? error.message : "Registration failed. Please try again.");
			setIsCreating(false);
		}
	};

	return (
		<main className="teacher-register-page">
			<header className="teacher-register-header">
				<a className="teacher-register-logo" href="/" aria-label="Acadence home">
					<img src="/images/acadence-logo.png" alt="Acadence" />
					<span>PEOPLE · LEARNING · INTEGRITY</span>
				</a>
				<a className="teacher-home-link" href="/">← Back to Home</a>
			</header>

			<HandwrittenNote className="teacher-note teacher-note--top">More<br />Learning.<br />Less<br />Admin.<span className="note-underline" /></HandwrittenNote>
			<div className="teacher-organic-shape" aria-hidden="true" />
			<div className="teacher-botanical" aria-hidden="true">╱╲<br />╲╱<br />╱╲</div>
			<HandwrittenNote className="teacher-note teacher-note--bottom">Education<br />for what's next.<span className="note-underline" /></HandwrittenNote>
			<div className="teacher-signature">PEOPLE<br />LEARNING<br />INTEGRITY<span className="note-underline" /></div>

			<section className="teacher-register-card" aria-labelledby="teacher-register-title">
				<p className="teacher-eyebrow">TEACHER REGISTRATION</p>
				<span className="teacher-heading-mark" aria-hidden="true" />
				<h1 id="teacher-register-title">Create your teacher account</h1>
				<p className="teacher-intro">Manage classrooms. Inspire minds. Make a difference.</p>

				<form onSubmit={handleSubmit} noValidate>
					{apiError && <p className="teacher-form-message teacher-form-message--error" role="alert">{apiError}</p>}
					{successMessage && <p className="teacher-form-message teacher-form-message--success" role="status">{successMessage}</p>}
					<FormField label="Enter username" name="username" placeholder="e.g. ananyaroy" value={values.username} error={fieldError("username")} onChange={(value) => updateField("username", value)} onBlur={() => setTouched((current) => ({ ...current, username: true }))} />
					<FormField label="Enter name" name="name" placeholder="e.g. Ananya Roy" value={values.name} error={fieldError("name")} onChange={(value) => updateField("name", value)} onBlur={() => setTouched((current) => ({ ...current, name: true }))} />
					<PasswordField name="password" label="Enter password" value={values.password} error={fieldError("password")} onChange={(value) => updateField("password", value)} onBlur={() => setTouched((current) => ({ ...current, password: true }))} />
					<PasswordField name="confirmPassword" label="Confirm your password" value={values.confirmPassword} error={fieldError("confirmPassword")} onChange={(value) => updateField("confirmPassword", value)} onBlur={() => setTouched((current) => ({ ...current, confirmPassword: true }))} />

					<div className="teacher-form-actions">
						<button className="teacher-register-button" type="submit" disabled={isCreating}>{isCreating ? "Creating account…" : "Register now →"}</button>
						<a className="teacher-login-button" href="/login">Login instead</a>
					</div>
				</form>
			</section>
		</main>
	);
}