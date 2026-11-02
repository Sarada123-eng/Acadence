type FormFieldProps = {
	label: string;
	name: string;
	type?: string;
	placeholder: string;
	value: string;
	error?: string;
	onChange: (value: string) => void;
	onBlur: () => void;
};

export default function FormField({ label, name, type = "text", placeholder, value, error, onChange, onBlur }: FormFieldProps) {
	const inputId = `teacher-${name}`;

	return (
		<div className="teacher-field">
			<label htmlFor={inputId}>{label}</label>
			<input
				id={inputId}
				name={name}
				type={type}
				placeholder={placeholder}
				value={value}
				onChange={(event) => onChange(event.target.value)}
				onBlur={onBlur}
				aria-invalid={Boolean(error)}
				aria-describedby={error ? `${inputId}-error` : undefined}
			/>
			{error && <p className="teacher-field__error" id={`${inputId}-error`}>{error}</p>}
		</div>
	);
}