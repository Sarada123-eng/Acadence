import { useState } from "react";

type PasswordFieldProps = {
	name: "password" | "confirmPassword";
	label: string;
	value: string;
	error?: string;
	onChange: (value: string) => void;
	onBlur: () => void;
};

export default function PasswordField({ name, label, value, error, onChange, onBlur }: PasswordFieldProps) {
	const [visible, setVisible] = useState(false);
	const inputId = `teacher-${name}`;

	return (
		<div className="teacher-field">
			<label htmlFor={inputId}>{label}</label>
			<div className="teacher-password-input">
				<input
					id={inputId}
					name={name}
					type={visible ? "text" : "password"}
					placeholder="Enter password"
					value={value}
					onChange={(event) => onChange(event.target.value)}
					onBlur={onBlur}
					aria-invalid={Boolean(error)}
					aria-describedby={error ? `${inputId}-error` : undefined}
				/>
				<button type="button" className="password-toggle" onClick={() => setVisible((current) => !current)} aria-label={visible ? "Hide password" : "Show password"}>
					{visible ? "◉" : "◌"}
				</button>
			</div>
			{error && <p className="teacher-field__error" id={`${inputId}-error`}>{error}</p>}
		</div>
	);
}