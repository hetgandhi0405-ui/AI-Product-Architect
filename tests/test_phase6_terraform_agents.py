"""
Tests for Phase 6 Terraform Generation and Validation agents.
"""
import pytest
from backend.agents.terraform_generation_agent import terraform_generation_agent
from backend.agents.terraform_validation_agent import terraform_validation_agent


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _base_state(**kwargs):
    state = {
        "project_id": "proj-test01",
        "project_name": "Test App",
        "assembled_project_path": "",
        "infrastructure_state": {
            "architecture_id": "ARCH-TEST001",
            "resources": [],
            "relationships": [],
        },
        "cloud_architecture_spec": {
            "region": "ap-south-1",
            "compute": {"service": "ecs_fargate", "fargate_cpu": 512, "fargate_memory": 1024,
                        "port": 8000, "desired_count": 2, "min_count": 1, "max_count": 4,
                        "autoscaling": True},
            "database": {"engine": "postgres", "instance_class": "db.t3.medium",
                        "allocated_storage_gb": 20, "multi_az": False, "port": 5432},
            "network": {"public_subnets": 2, "private_subnets": 2},
            "cache": {"enabled": False},
            "storage": {"enabled": False},
            "load_balancer": {"port": 80},
            "monitoring": {"alarms": ["CPUUtilization"]},
            "security": {"waf": False, "tls": True, "secrets_manager": True},
        },
    }
    state.update(kwargs)
    return state


# ─── terraform_generation_agent ───────────────────────────────────────────────

class TestTerraformGenerationAgent:

    def test_generates_required_files(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        tg = result["terraform_generation"]
        assert tg["status"] == "GENERATED"
        files = tg["file_contents"]
        for required in ["provider.tf", "variables.tf", "vpc.tf", "security.tf",
                         "compute.tf", "database.tf", "load_balancer.tf", "outputs.tf"]:
            assert required in files, f"Missing {required}"

    def test_provider_tf_has_aws_provider(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        provider = result["terraform_generation"]["file_contents"]["provider.tf"]
        assert 'provider "aws"' in provider
        assert "var.aws_region" in provider

    def test_variables_tf_has_project_name(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        variables = result["terraform_generation"]["file_contents"]["variables.tf"]
        assert 'variable "project_name"' in variables
        assert 'variable "db_password"' in variables
        assert "sensitive   = true" in variables

    def test_vpc_tf_has_subnets(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        vpc = result["terraform_generation"]["file_contents"]["vpc.tf"]
        assert 'resource "aws_vpc" "main"' in vpc
        assert 'resource "aws_subnet" "public"' in vpc
        assert 'resource "aws_subnet" "private"' in vpc
        assert 'resource "aws_nat_gateway"' in vpc

    def test_compute_tf_has_ecs_fargate(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        compute = result["terraform_generation"]["file_contents"]["compute.tf"]
        assert 'resource "aws_ecs_cluster"' in compute
        assert 'resource "aws_ecs_task_definition"' in compute
        assert 'resource "aws_ecs_service"' in compute

    def test_database_tf_has_rds(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        db = result["terraform_generation"]["file_contents"]["database.tf"]
        assert 'resource "aws_db_instance"' in db
        assert "var.db_password" in db
        assert "deletion_protection    = true" in db

    def test_no_cache_tf_when_disabled(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        assert "cache.tf" not in result["terraform_generation"]["file_contents"]

    def test_cache_tf_generated_when_enabled(self):
        state = _base_state()
        state["cloud_architecture_spec"]["cache"] = {
            "enabled": True, "node_type": "cache.t4g.micro"
        }
        result = terraform_generation_agent(state)
        files = result["terraform_generation"]["file_contents"]
        assert "cache.tf" in files
        assert 'resource "aws_elasticache_replication_group"' in files["cache.tf"]

    def test_storage_tf_generated_when_enabled(self):
        state = _base_state()
        state["cloud_architecture_spec"]["storage"] = {"enabled": True}
        result = terraform_generation_agent(state)
        files = result["terraform_generation"]["file_contents"]
        assert "storage.tf" in files
        assert 'resource "aws_s3_bucket"' in files["storage.tf"]

    def test_outputs_tf_has_alb_output(self):
        state = _base_state()
        result = terraform_generation_agent(state)
        outputs = result["terraform_generation"]["file_contents"]["outputs.tf"]
        assert 'output "alb_dns_name"' in outputs
        assert 'output "db_endpoint"' in outputs

    def test_no_hardcoded_credentials(self):
        """Generated Terraform must never contain actual AWS keys or passwords."""
        state = _base_state()
        result = terraform_generation_agent(state)
        all_tf = "\n".join(result["terraform_generation"]["file_contents"].values())
        import re
        # Real 20-char AWS access keys (AKIA...)
        assert not re.search(r'AKIA[A-Z0-9]{16}', all_tf)
        # Literal passwords (not var references)
        literal_pass = re.findall(r'password\s*=\s*"(?!var\.)[^"]+"', all_tf)
        assert len(literal_pass) == 0, f"Hardcoded passwords: {literal_pass}"

    def test_skipped_when_no_spec(self):
        state = {
            "project_id": "empty",
            "project_name": "Empty",
            "assembled_project_path": "",
            "infrastructure_state": {},
            "cloud_architecture_spec": {},
        }
        result = terraform_generation_agent(state)
        assert result["terraform_generation"]["status"] == "SKIPPED"


# ─── terraform_validation_agent ───────────────────────────────────────────────

class TestTerraformValidationAgent:

    def _run_with_generated_tf(self, **spec_overrides):
        state = _base_state()
        state["cloud_architecture_spec"].update(spec_overrides)
        state = terraform_generation_agent(state)
        return terraform_validation_agent(state)

    def test_passes_for_valid_generation(self):
        result = self._run_with_generated_tf()
        tv = result["terraform_validation"]
        assert tv["status"] == "PASS"
        assert len(tv["issues"]) == 0

    def test_checks_include_required_files(self):
        result = self._run_with_generated_tf()
        tv = result["terraform_validation"]
        check_names = [c["name"] for c in tv["checks"]]
        assert "required_files_present" in check_names
        assert "hcl_structure" in check_names
        assert "variable_consistency" in check_names
        assert "no_hardcoded_secrets" in check_names

    def test_fail_on_missing_file(self):
        state = _base_state()
        state = terraform_generation_agent(state)
        # Remove a required file to simulate failure
        del state["terraform_generation"]["file_contents"]["vpc.tf"]
        result = terraform_validation_agent(state)
        tv = result["terraform_validation"]
        assert tv["status"] == "FAIL"
        assert any("vpc.tf" in iss for iss in tv["issues"])

    def test_fail_on_hardcoded_secret(self):
        state = _base_state()
        state = terraform_generation_agent(state)
        # Inject a hardcoded password
        state["terraform_generation"]["file_contents"]["provider.tf"] += '\npassword = "MyHardcoded123"\n'
        result = terraform_validation_agent(state)
        tv = result["terraform_validation"]
        # Should detect the hardcoded password
        assert tv["status"] == "FAIL"
        assert any("secret" in iss.lower() or "hardcoded" in iss.lower() for iss in tv["issues"])

    def test_skipped_passthrough(self):
        state = {
            "project_id": "skip-proj",
            "project_name": "Skip",
            "assembled_project_path": "",
            "terraform_generation": {"status": "SKIPPED", "file_contents": {}},
        }
        result = terraform_validation_agent(state)
        assert result["terraform_validation"]["status"] == "SKIPPED"

    def test_deployment_ready_key_present(self):
        result = self._run_with_generated_tf()
        assert "deployment_ready" in result["terraform_validation"]
