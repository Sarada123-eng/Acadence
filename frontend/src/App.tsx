import Page from "./app/page";
import RoleSelectionPage from "./pages/RoleSelectionPage";
import TeacherRegisterPage from "./pages/TeacherRegisterPage";
import TeacherLoginPage from "./pages/TeacherLoginPage";
import StudentOnboardingPage from "./pages/StudentOnboardingPage";
import BiometricSetup from "./pages/BiometricSetup";
import StudentJoinPage from "./pages/StudentJoinPage";
import TeacherDashboardPage from "./pages/TeacherDashboardPage";

export default function App() {
	const path = window.location.pathname;

	if (path === "/onboarding") return <RoleSelectionPage />;
	if (path === "/auth/student") {
		return <StudentOnboardingPage />;
	}
	if (path === "/join") return <StudentJoinPage />;
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
		return <TeacherDashboardPage />;
	}

	return <Page />;
}
