import Page from "./app/page";
import RoleSelectionPage from "./pages/RoleSelectionPage";
import TeacherRegisterPage from "./pages/TeacherRegisterPage";
import TeacherLoginPage from "./pages/TeacherLoginPage";
import StudentOnboardingPage from "./pages/StudentOnboardingPage";
import BiometricSetup from "./pages/BiometricSetup";

function PlaceholderPage({ title, description }: { title: string; description: string }) {
	return (
		<main className="route-placeholder">
			<a className="route-placeholder__back" href="/onboarding">← Back to role selection</a>
			<img src="/images/acadence-logo.png" alt="Acadence — People, Learning, Integrity" />
			<p className="label">ACADENCE</p>
			<h1>{title}</h1>
			<p>{description}</p>
		</main>
	);
}

export default function App() {
	const path = window.location.pathname;

	if (path === "/onboarding") return <RoleSelectionPage />;
	if (path === "/auth/student") {
		return <StudentOnboardingPage />;
	}
	if (path === "/auth/student/biometrics") {
		return <BiometricSetup />;
	}
	if (path === "/auth/teacher") {
		return <TeacherRegisterPage />;
	}
	if (path === "/login") {
		return <TeacherLoginPage />;
	}
	if (path === "/teacher/dashboard") {
		return <PlaceholderPage title="Teacher dashboard" description="Your classroom workspace will live here." />;
	}

	return <Page />;
}
