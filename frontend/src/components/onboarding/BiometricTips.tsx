export default function BiometricTips({ title, tips }: { title: string; tips: string[] }) {
	return (
		<div className="biometric-tips">
			<span className="biometric-tips__icon material-symbols-outlined" aria-hidden="true">lightbulb</span>
			<div>
				<h3>{title}</h3>
				<ul>{tips.map((tip) => <li key={tip}>{tip}</li>)}</ul>
			</div>
		</div>
	);
}