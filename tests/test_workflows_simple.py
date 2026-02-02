"""
Simple integration tests for GitHub workflows.
Tests workflow file structure and basic validation.
"""

import pytest
import yaml
from pathlib import Path


class TestWorkflowFiles:
    """Test GitHub workflow file validity"""

    WORKFLOW_DIR = Path("/home/jailuser/git/.github/workflows")

    def test_workflow_directory_exists(self):
        """Test that workflow directory exists"""
        assert self.WORKFLOW_DIR.exists()
        assert self.WORKFLOW_DIR.is_dir()

    def test_workflow_files_exist(self):
        """Test that workflow files exist"""
        workflow_files = list(self.WORKFLOW_DIR.glob("*.yml"))
        assert len(workflow_files) >= 9, "Expected at least 9 workflow files"

    def test_all_workflows_are_valid_yaml(self):
        """Test that all workflow files are valid YAML"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                try:
                    yaml.load(f, Loader=yaml.FullLoader)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {workflow_file.name}: {e}")

    def test_all_workflows_have_name(self):
        """Test that all workflows have a name field"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert 'name' in data, f"{workflow_file.name} missing 'name' field"
                assert len(data['name']) > 0, f"{workflow_file.name} has empty name"

    def test_all_workflows_have_jobs(self):
        """Test that all workflows have jobs defined"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert 'jobs' in data, f"{workflow_file.name} missing 'jobs' section"


class TestSpecificWorkflows:
    """Test specific workflow configurations"""

    WORKFLOW_DIR = Path("/home/jailuser/git/.github/workflows")

    def test_esphome_build_workflow_exists(self):
        """Test ESPHome build workflow exists"""
        workflow_file = self.WORKFLOW_DIR / "esphome_build.yml"
        assert workflow_file.exists()

    def test_release_tag_workflow_exists(self):
        """Test release tag workflow exists"""
        workflow_file = self.WORKFLOW_DIR / "release_tag.yml"
        assert workflow_file.exists()

    def test_shellcheck_workflow_exists(self):
        """Test shellcheck workflow exists"""
        workflow_file = self.WORKFLOW_DIR / "shellcheck.yml"
        assert workflow_file.exists()

    def test_stale_workflow_exists(self):
        """Test stale workflow exists"""
        workflow_file = self.WORKFLOW_DIR / "stale.yml"
        assert workflow_file.exists()

    def test_validation_workflows_exist(self):
        """Test validation workflows exist"""
        validation_workflows = [
            "validate_blueprint.yml",
            "validate_clang_format.yml",
            "validate_markdown.yml",
            "validate_python.yml",
            "validate_yamllint.yml"
        ]

        for workflow_name in validation_workflows:
            workflow_file = self.WORKFLOW_DIR / workflow_name
            assert workflow_file.exists(), f"Missing {workflow_name}"


class TestWorkflowConsistency:
    """Test consistency across workflows"""

    WORKFLOW_DIR = Path("/home/jailuser/git/.github/workflows")

    def test_all_workflows_use_ubuntu(self):
        """Test all workflows use ubuntu runners"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if 'jobs' in data:
                    for job_name, job_data in data['jobs'].items():
                        if 'runs-on' in job_data:
                            runs_on = job_data['runs-on']
                            assert 'ubuntu' in runs_on.lower(), \
                                f"{workflow_file.name}:{job_name} doesn't use ubuntu"

    def test_all_workflows_have_yaml_extension(self):
        """Test all workflow files use .yml extension"""
        workflow_files = list(self.WORKFLOW_DIR.glob("*"))
        for wf in workflow_files:
            if wf.is_file():
                assert wf.suffix == '.yml', f"{wf.name} doesn't have .yml extension"

    def test_workflow_names_are_descriptive(self):
        """Test workflow names are descriptive (not empty)"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                name = data.get('name', '')
                assert len(name) >= 5, \
                    f"{workflow_file.name} has short/missing name: '{name}'"


class TestESPHomeBuildWorkflow:
    """Test ESPHome build workflow specifics"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/esphome_build.yml")

    def test_has_code_scan_job(self):
        """Test workflow has code scan job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'jobs' in data
            assert 'code_scan' in data['jobs']

    def test_has_build_latest_jobs(self):
        """Test workflow has build jobs for latest ESPHome"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            jobs = data['jobs']
            expected_jobs = [
                'build_core_latest',
                'build_bluetooth_proxy_latest',
                'build_climate_cool_latest'
            ]
            for job in expected_jobs:
                assert job in jobs, f"Missing job: {job}"

    def test_uses_python_311(self):
        """Test workflow uses Python 3.11"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            jobs = data['jobs']
            found_python_version = False
            for job_name, job_data in jobs.items():
                if 'steps' in job_data:
                    for step in job_data['steps']:
                        if step.get('uses', '').startswith('actions/setup-python'):
                            python_version = step.get('with', {}).get('python-version')
                            if python_version:
                                assert python_version == "3.11"
                                found_python_version = True
            assert found_python_version, "No Python version found in workflow"


class TestStaleWorkflow:
    """Test stale issues workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/stale.yml")

    def test_has_stale_job(self):
        """Test workflow has stale job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'jobs' in data
            assert 'stale' in data['jobs']

    def test_has_correct_permissions(self):
        """Test workflow has correct permissions"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            job = data['jobs']['stale']
            assert 'permissions' in job
            assert job['permissions']['issues'] == 'write'
            assert job['permissions']['pull-requests'] == 'write'

    def test_stale_configuration_values(self):
        """Test stale action has reasonable configuration values"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['stale']['steps']
            stale_step = next(s for s in steps if 'actions/stale' in s.get('uses', ''))
            config = stale_step['with']

            # Check that config values are numbers and reasonable
            assert config['days-before-issue-stale'] > 0
            assert config['days-before-issue-close'] > 0
            assert config['days-before-pr-stale'] > 0
            assert config['days-before-pr-close'] > 0


class TestReleaseTagWorkflow:
    """Test release tag workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/release_tag.yml")

    def test_has_update_tags_job(self):
        """Test workflow has update-tags job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'jobs' in data
            assert 'update-tags' in data['jobs']

    def test_has_write_permissions(self):
        """Test workflow has write permissions"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'permissions' in data
            assert data['permissions']['contents'] == 'write'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])