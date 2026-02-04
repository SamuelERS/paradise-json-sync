"""
Tests de validación para workflows de GitHub Actions
OT-006: Pipeline CI/CD

Estos tests verifican que los workflows estén correctamente configurados
y cumplan con los requisitos del proyecto.
"""
import yaml
import pytest
from pathlib import Path


# Obtener la raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / ".github" / "workflows"


def get_on_key(workflow: dict):
    """
    Obtener la clave 'on' del workflow.
    YAML interpreta 'on' como True (booleano), por lo que
    necesitamos buscar tanto 'on' como True.
    """
    if "on" in workflow:
        return workflow["on"]
    if True in workflow:
        return workflow[True]
    return None


class TestCIWorkflow:
    """Tests para el workflow de CI principal"""

    @pytest.fixture
    def ci_workflow(self):
        """Cargar el workflow ci.yml"""
        workflow_path = WORKFLOWS_DIR / "ci.yml"
        assert workflow_path.exists(), "ci.yml no encontrado"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_tiene_nombre(self, ci_workflow):
        """Verificar que el workflow tiene nombre correcto"""
        assert ci_workflow["name"] == "CI Pipeline"

    def test_triggers_correctos(self, ci_workflow):
        """Verificar triggers en push y pull_request"""
        on_config = get_on_key(ci_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        assert "push" in on_config
        assert "pull_request" in on_config
        assert "main" in on_config["push"]["branches"]
        assert "develop" in on_config["push"]["branches"]

    def test_jobs_requeridos(self, ci_workflow):
        """Verificar que todos los jobs requeridos existen"""
        jobs_requeridos = ["lint", "test-backend", "test-frontend", "build", "security"]
        for job in jobs_requeridos:
            assert job in ci_workflow["jobs"], f"Job '{job}' no encontrado"

    def test_cobertura_70(self, ci_workflow):
        """Verificar que la cobertura mínima es 70%"""
        assert "env" in ci_workflow
        assert ci_workflow["env"]["COVERAGE_MINIMUM"] == 70

    def test_dependencias_correctas(self, ci_workflow):
        """Verificar que las dependencias entre jobs son correctas"""
        # test-backend depende de lint
        assert "lint" in ci_workflow["jobs"]["test-backend"]["needs"]
        # test-frontend depende de lint
        assert "lint" in ci_workflow["jobs"]["test-frontend"]["needs"]
        # build depende de tests
        build_needs = ci_workflow["jobs"]["build"]["needs"]
        assert "test-backend" in build_needs
        assert "test-frontend" in build_needs

    def test_python_version(self, ci_workflow):
        """Verificar versión de Python"""
        assert ci_workflow["env"]["PYTHON_VERSION"] == "3.11"

    def test_node_version(self, ci_workflow):
        """Verificar versión de Node.js"""
        assert ci_workflow["env"]["NODE_VERSION"] == "18"

    def test_lint_job_tiene_steps(self, ci_workflow):
        """Verificar que el job lint tiene steps"""
        lint_job = ci_workflow["jobs"]["lint"]
        assert "steps" in lint_job
        assert len(lint_job["steps"]) > 0

    def test_security_job_existe(self, ci_workflow):
        """Verificar que existe job de seguridad"""
        assert "security" in ci_workflow["jobs"]


class TestCDStagingWorkflow:
    """Tests para el workflow de CD Staging"""

    @pytest.fixture
    def staging_workflow(self):
        """Cargar el workflow cd-staging.yml"""
        workflow_path = WORKFLOWS_DIR / "cd-staging.yml"
        assert workflow_path.exists(), "cd-staging.yml no encontrado"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_tiene_nombre(self, staging_workflow):
        """Verificar nombre del workflow"""
        assert staging_workflow["name"] == "CD Staging"

    def test_trigger_main(self, staging_workflow):
        """Verificar que se dispara en push a main"""
        on_config = get_on_key(staging_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        assert "push" in on_config
        assert "main" in on_config["push"]["branches"]

    def test_workflow_dispatch(self, staging_workflow):
        """Verificar que permite ejecución manual"""
        on_config = get_on_key(staging_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        assert "workflow_dispatch" in on_config

    def test_job_deploy_existe(self, staging_workflow):
        """Verificar que existe job de deploy"""
        assert "deploy-staging" in staging_workflow["jobs"]

    def test_environment_staging(self, staging_workflow):
        """Verificar que usa environment staging"""
        deploy_job = staging_workflow["jobs"]["deploy-staging"]
        assert deploy_job["environment"] == "staging"


class TestCDProductionWorkflow:
    """Tests para el workflow de CD Production"""

    @pytest.fixture
    def production_workflow(self):
        """Cargar el workflow cd-production.yml"""
        workflow_path = WORKFLOWS_DIR / "cd-production.yml"
        assert workflow_path.exists(), "cd-production.yml no encontrado"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_tiene_nombre(self, production_workflow):
        """Verificar nombre del workflow"""
        assert production_workflow["name"] == "CD Production"

    def test_requiere_confirm(self, production_workflow):
        """Verificar que requiere confirmación manual"""
        on_config = get_on_key(production_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        assert "workflow_dispatch" in on_config
        inputs = on_config["workflow_dispatch"]["inputs"]
        assert "confirm" in inputs
        assert inputs["confirm"]["required"] is True

    def test_requiere_version(self, production_workflow):
        """Verificar que requiere versión"""
        on_config = get_on_key(production_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        inputs = on_config["workflow_dispatch"]["inputs"]
        assert "version" in inputs
        assert inputs["version"]["required"] is True

    def test_job_deploy_existe(self, production_workflow):
        """Verificar que existe job de deploy"""
        assert "deploy-production" in production_workflow["jobs"]

    def test_environment_production(self, production_workflow):
        """Verificar que usa environment production"""
        deploy_job = production_workflow["jobs"]["deploy-production"]
        assert deploy_job["environment"] == "production"

    def test_conditional_confirm(self, production_workflow):
        """Verificar que el deploy requiere confirmación"""
        deploy_job = production_workflow["jobs"]["deploy-production"]
        assert "if" in deploy_job
        assert "inputs.confirm" in deploy_job["if"]


class TestSecurityWorkflow:
    """Tests para el workflow de Security Scan"""

    @pytest.fixture
    def security_workflow(self):
        """Cargar el workflow security-scan.yml"""
        workflow_path = WORKFLOWS_DIR / "security-scan.yml"
        assert workflow_path.exists(), "security-scan.yml no encontrado"
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_tiene_nombre(self, security_workflow):
        """Verificar nombre del workflow"""
        assert security_workflow["name"] == "Security Scan"

    def test_tiene_schedule(self, security_workflow):
        """Verificar que tiene programación periódica"""
        on_config = get_on_key(security_workflow)
        assert on_config is not None, "No se encontró configuración 'on'"
        assert "schedule" in on_config

    def test_jobs_seguridad_existen(self, security_workflow):
        """Verificar que existen jobs de seguridad"""
        jobs = security_workflow["jobs"]
        assert "security-backend" in jobs or "security" in jobs


class TestGitHubFiles:
    """Tests para archivos de configuración de GitHub"""

    def test_codeowners_existe(self):
        """Verificar que CODEOWNERS existe"""
        codeowners_path = PROJECT_ROOT / ".github" / "CODEOWNERS"
        assert codeowners_path.exists(), "CODEOWNERS no encontrado"

    def test_codeowners_contiene_owner(self):
        """Verificar que CODEOWNERS contiene al owner"""
        codeowners_path = PROJECT_ROOT / ".github" / "CODEOWNERS"
        content = codeowners_path.read_text()
        assert "@SamuelERS" in content

    def test_pr_template_existe(self):
        """Verificar que PR template existe"""
        pr_template_path = PROJECT_ROOT / ".github" / "pull_request_template.md"
        assert pr_template_path.exists(), "pull_request_template.md no encontrado"

    def test_pr_template_tiene_checklist(self):
        """Verificar que PR template tiene checklist"""
        pr_template_path = PROJECT_ROOT / ".github" / "pull_request_template.md"
        content = pr_template_path.read_text()
        assert "- [ ]" in content  # Tiene checkboxes

    def test_bug_report_template_existe(self):
        """Verificar que bug report template existe"""
        bug_template = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
        assert bug_template.exists(), "bug_report.md no encontrado"

    def test_feature_request_template_existe(self):
        """Verificar que feature request template existe"""
        feature_template = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md"
        assert feature_template.exists(), "feature_request.md no encontrado"


class TestScripts:
    """Tests para scripts de CI/CD"""

    def test_run_backend_tests_existe(self):
        """Verificar que script de tests backend existe"""
        script_path = PROJECT_ROOT / "scripts" / "ci" / "run-backend-tests.sh"
        assert script_path.exists(), "run-backend-tests.sh no encontrado"

    def test_run_frontend_tests_existe(self):
        """Verificar que script de tests frontend existe"""
        script_path = PROJECT_ROOT / "scripts" / "ci" / "run-frontend-tests.sh"
        assert script_path.exists(), "run-frontend-tests.sh no encontrado"

    def test_check_coverage_existe(self):
        """Verificar que script de cobertura existe"""
        script_path = PROJECT_ROOT / "scripts" / "ci" / "check-coverage.sh"
        assert script_path.exists(), "check-coverage.sh no encontrado"

    def test_deploy_staging_existe(self):
        """Verificar que script de deploy staging existe"""
        script_path = PROJECT_ROOT / "scripts" / "deploy" / "deploy-staging.sh"
        assert script_path.exists(), "deploy-staging.sh no encontrado"

    def test_deploy_production_existe(self):
        """Verificar que script de deploy production existe"""
        script_path = PROJECT_ROOT / "scripts" / "deploy" / "deploy-production.sh"
        assert script_path.exists(), "deploy-production.sh no encontrado"

    def test_backend_script_tiene_coverage_minimum(self):
        """Verificar que script backend usa COVERAGE_MINIMUM"""
        script_path = PROJECT_ROOT / "scripts" / "ci" / "run-backend-tests.sh"
        content = script_path.read_text()
        assert "COVERAGE_MINIMUM" in content
        assert "70" in content


class TestWorkflowsYAMLValidity:
    """Tests para validar que los YAML son válidos"""

    def test_all_workflows_valid_yaml(self):
        """Verificar que todos los workflows son YAML válidos"""
        workflows = list(WORKFLOWS_DIR.glob("*.yml"))
        assert len(workflows) >= 3, "Deben existir al menos 3 workflows"

        for workflow_path in workflows:
            with open(workflow_path) as f:
                try:
                    data = yaml.safe_load(f)
                    assert data is not None, f"{workflow_path.name} está vacío"
                    assert "name" in data, f"{workflow_path.name} no tiene nombre"
                    # YAML interpreta 'on' como True, verificar ambos
                    on_config = get_on_key(data)
                    assert on_config is not None, f"{workflow_path.name} no tiene triggers"
                    assert "jobs" in data, f"{workflow_path.name} no tiene jobs"
                except yaml.YAMLError as e:
                    pytest.fail(f"YAML inválido en {workflow_path.name}: {e}")
