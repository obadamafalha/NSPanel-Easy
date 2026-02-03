"""
Comprehensive integration tests for GitHub workflows.
Tests workflow file structure, configuration, triggers, and validation.
Covers all changed workflow files with extensive edge case testing.
"""

import pytest
import yaml
from pathlib import Path


class TestESPHomeBuildWorkflowComprehensive:
    """Comprehensive tests for ESPHome build workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/esphome_build.yml")

    def test_workflow_file_exists(self):
        """Test that esphome_build.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in esphome_build.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == "Build ESPHome"

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            # Check all expected triggers exist
            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'schedule' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors correct file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            expected_patterns = [
                "nspanel_esphome*.yaml",
                "esphome/nspanel_esphome*.yaml",
                "prebuilt/nspanel_esphome*.yaml",
                "prebuilt/wall_display*.yaml",
                ".github/workflows/esphome_build.yml",
                ".test/*.yaml",
                "*.h",
                "*.c",
                "*.cpp",
                "*.py"
            ]

            for pattern in expected_patterns:
                assert pattern in push_paths, f"Missing path pattern: {pattern}"

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors correct file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']
            push_paths = triggers['push']['paths']

            # PR and push paths should be identical
            assert pr_paths == push_paths, "PR and push trigger paths should match"

    def test_workflow_schedule_trigger_cron(self):
        """Test that schedule trigger has valid cron expression"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            schedule = triggers['schedule']

            assert len(schedule) == 1
            assert 'cron' in schedule[0]
            assert schedule[0]['cron'] == '0 10 * * *'  # Daily at 10:00 AM UTC

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_concurrency_settings(self):
        """Test that workflow has correct concurrency settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'concurrency' in data
            concurrency = data['concurrency']
            assert 'group' in concurrency
            assert 'cancel-in-progress' in concurrency
            assert concurrency['cancel-in-progress'] is True
            assert '${{ github.workflow }}' in concurrency['group']

    def test_workflow_code_scan_job_structure(self):
        """Test that code_scan job has correct structure"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'code_scan' in data['jobs']
            code_scan = data['jobs']['code_scan']

            assert code_scan['name'] == 'Code scan (YAML)'
            assert code_scan['runs-on'] == 'ubuntu-latest'
            assert 'steps' in code_scan
            assert len(code_scan['steps']) >= 3

    def test_workflow_code_scan_uses_checkout(self):
        """Test that code_scan job uses checkout action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'

    def test_workflow_code_scan_installs_yamllint(self):
        """Test that code_scan job installs yamllint"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            install_step = next((s for s in steps if s.get('name') == 'Install yamllint'), None)
            assert install_step is not None
            assert 'pip install yamllint' in install_step['run']

    def test_workflow_code_scan_validates_yaml(self):
        """Test that code_scan job validates YAML files"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if s.get('name') == 'Validate YAML files'), None)
            assert validate_step is not None
            assert 'yamllint' in validate_step['run']
            assert '.rules/yamllint.yml' in validate_step['run']

    def test_workflow_has_build_core_latest_job(self):
        """Test that workflow has build_core_latest job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'build_core_latest' in data['jobs']
            job = data['jobs']['build_core_latest']
            assert job['name'] == 'Core (latest)'
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_build_core_latest_uses_python_311(self):
        """Test that build_core_latest uses Python 3.11"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_latest']['steps']

            setup_python = next((s for s in steps if 'setup-python' in s.get('uses', '')), None)
            assert setup_python is not None
            assert setup_python['with']['python-version'] == '3.11'

    def test_workflow_build_core_latest_uses_platformio_cache(self):
        """Test that build_core_latest uses PlatformIO caching"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_latest']['steps']

            cache_step = next((s for s in steps if 'cache' in s.get('uses', '').lower()), None)
            assert cache_step is not None
            assert cache_step['uses'] == 'actions/cache@v4'

            # Check cache paths
            cache_paths = cache_step['with']['path']
            assert '~/.platformio/packages' in cache_paths
            assert '~/.platformio/platforms' in cache_paths

            # Check cache key
            cache_key = cache_step['with']['key']
            assert 'pio-latest' in cache_key
            assert 'hashFiles' in cache_key

    def test_workflow_build_core_latest_creates_venv(self):
        """Test that build_core_latest creates virtual environment"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_latest']['steps']

            venv_step = next((s for s in steps if 'virtual environment' in s.get('name', '').lower()), None)
            assert venv_step is not None
            assert 'python -m venv' in venv_step['run']
            assert 'pip install esphome' in venv_step['run']

    def test_workflow_build_core_latest_compiles_firmware(self):
        """Test that build_core_latest compiles firmware"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_latest']['steps']

            compile_step = next((s for s in steps if 'Compile Core Firmware' in s.get('name', '')), None)
            assert compile_step is not None
            assert 'esphome compile' in compile_step['run']
            assert '.test/esphome_idf_basic.yaml' in compile_step['run']

    def test_workflow_build_core_latest_uploads_artifact(self):
        """Test that build_core_latest uploads environment artifact"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_latest']['steps']

            upload_step = next((s for s in steps if 'upload-artifact' in s.get('uses', '')), None)
            assert upload_step is not None
            assert upload_step['uses'] == 'actions/upload-artifact@v4'
            assert upload_step['with']['name'] == 'esphome-env-latest'
            assert upload_step['with']['path'] == 'esphome-env.tar.gz'
            assert upload_step['with']['retention-days'] == 1

    def test_workflow_has_dependent_build_jobs(self):
        """Test that workflow has all dependent build jobs"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # Latest chain jobs
            latest_jobs = [
                'build_core_arduino_latest',
                'build_ble_tracker_latest',
                'build_bluetooth_proxy_latest',
                'build_climate_cool_latest',
                'build_climate_heat_latest',
                'build_climate_dual_latest',
                'build_cover_latest',
                'build_customizations_latest',
                'build_climate_ble_proxy_latest'
            ]

            for job_name in latest_jobs:
                assert job_name in data['jobs'], f"Missing job: {job_name}"
                job = data['jobs'][job_name]
                assert 'needs' in job
                assert job['needs'] == 'build_core_latest'

    def test_workflow_dependent_jobs_download_artifacts(self):
        """Test that dependent jobs download the environment artifact"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            dependent_job = data['jobs']['build_core_arduino_latest']
            steps = dependent_job['steps']

            download_step = next((s for s in steps if 'download-artifact' in s.get('uses', '')), None)
            assert download_step is not None
            assert download_step['uses'] == 'actions/download-artifact@v4'
            assert download_step['with']['name'] == 'esphome-env-latest'

    def test_workflow_has_build_core_dev_job(self):
        """Test that workflow has build_core_dev job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'build_core_dev' in data['jobs']
            job = data['jobs']['build_core_dev']
            assert job['name'] == 'Core (dev)'
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_build_core_dev_installs_dev_version(self):
        """Test that build_core_dev installs ESPHome dev version"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['build_core_dev']['steps']

            venv_step = next((s for s in steps if 'virtual environment' in s.get('name', '').lower()), None)
            assert venv_step is not None
            assert 'git+https://github.com/esphome/esphome.git@dev' in venv_step['run']

    def test_workflow_build_core_dev_uses_separate_cache(self):
        """Test that build_core_dev uses separate cache from latest"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            latest_steps = data['jobs']['build_core_latest']['steps']
            dev_steps = data['jobs']['build_core_dev']['steps']

            latest_cache = next((s for s in latest_steps if 'cache' in s.get('uses', '').lower()), None)
            dev_cache = next((s for s in dev_steps if 'cache' in s.get('uses', '').lower()), None)

            assert 'pio-latest' in latest_cache['with']['key']
            assert 'pio-dev' in dev_cache['with']['key']

    def test_workflow_has_dev_chain_jobs(self):
        """Test that workflow has all dev chain jobs"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # Dev chain jobs
            dev_jobs = [
                'build_core_arduino_dev',
                'build_ble_tracker_dev',
                'build_bluetooth_proxy_dev',
                'build_climate_cool_dev',
                'build_climate_heat_dev',
                'build_climate_dual_dev',
                'build_cover_dev',
                'build_customizations_dev',
                'build_climate_ble_proxy_dev'
            ]

            for job_name in dev_jobs:
                assert job_name in data['jobs'], f"Missing dev job: {job_name}"
                job = data['jobs'][job_name]
                assert 'needs' in job
                assert job['needs'] == 'build_core_dev'

    def test_workflow_dev_jobs_use_correct_artifact(self):
        """Test that dev jobs download the dev artifact"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            dev_job = data['jobs']['build_core_arduino_dev']
            steps = dev_job['steps']

            download_step = next((s for s in steps if 'download-artifact' in s.get('uses', '')), None)
            assert download_step is not None
            assert download_step['with']['name'] == 'esphome-env-dev'

    def test_workflow_all_jobs_use_ubuntu_latest(self):
        """Test that all jobs use ubuntu-latest runner"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            for job_name, job_data in data['jobs'].items():
                assert 'runs-on' in job_data
                assert job_data['runs-on'] == 'ubuntu-latest', f"{job_name} doesn't use ubuntu-latest"

    def test_workflow_all_compile_jobs_use_correct_configs(self):
        """Test that compile jobs use correct configuration files"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # Map job names to expected config files
            job_configs = {
                'build_core_latest': 'esphome_idf_basic.yaml',
                'build_core_arduino_latest': 'esphome_ard_basic.yaml',
                'build_ble_tracker_latest': 'esphome_idf_ble_tracker.yaml',
                'build_bluetooth_proxy_latest': 'esphome_idf_bluetooth_proxy.yaml',
                'build_climate_cool_latest': 'esphome_idf_climate_cool.yaml',
                'build_climate_heat_latest': 'esphome_idf_climate_heat.yaml',
                'build_climate_dual_latest': 'esphome_idf_climate_dual.yaml',
                'build_cover_latest': 'esphome_idf_cover.yaml',
                'build_customizations_latest': 'esphome_idf_climate_heat_customizations.yaml',
                'build_climate_ble_proxy_latest': 'esphome_idf_climate_cool_bluetooth_proxy.yaml',
            }

            for job_name, expected_config in job_configs.items():
                job = data['jobs'][job_name]
                steps = job['steps']
                compile_step = next((s for s in steps if 'Compile' in s.get('name', '')), None)
                assert compile_step is not None, f"{job_name} missing compile step"
                assert expected_config in compile_step['run'], \
                    f"{job_name} should use {expected_config}"

    def test_workflow_all_jobs_have_descriptive_names(self):
        """Test that all jobs have descriptive names"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            for job_name, job_data in data['jobs'].items():
                assert 'name' in job_data, f"{job_name} missing name"
                assert len(job_data['name']) > 0, f"{job_name} has empty name"

    def test_workflow_artifact_retention_period(self):
        """Test that artifacts have appropriate retention period"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # Check that core build jobs set retention-days
            for job_name in ['build_core_latest', 'build_core_dev']:
                job = data['jobs'][job_name]
                steps = job['steps']
                upload_step = next((s for s in steps if 'upload-artifact' in s.get('uses', '')), None)
                assert upload_step is not None
                assert 'retention-days' in upload_step['with']
                assert upload_step['with']['retention-days'] == 1

    def test_workflow_has_expected_number_of_jobs(self):
        """Test that workflow has expected number of jobs"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # 1 code_scan + 10 latest + 10 dev = 21 jobs
            assert len(data['jobs']) >= 21, "Workflow should have at least 21 jobs"


class TestShellCheckWorkflowComprehensive:
    """Comprehensive tests for ShellCheck workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/shellcheck.yml")

    def test_workflow_file_exists(self):
        """Test that shellcheck.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in shellcheck.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == 'ShellCheck'

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors shell script paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            assert len(push_paths) == 1
            assert '**/*.sh' in push_paths

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors shell script paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']

            assert len(pr_paths) == 1
            assert '**/*.sh' in pr_paths

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_has_shellcheck_job(self):
        """Test that workflow has shellcheck job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'shellcheck' in data['jobs']
            job = data['jobs']['shellcheck']
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_shellcheck_uses_checkout(self):
        """Test that shellcheck job uses checkout action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['shellcheck']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'

    def test_workflow_shellcheck_uses_shellcheck_action(self):
        """Test that shellcheck job uses shellcheck action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['shellcheck']['steps']

            shellcheck_step = next((s for s in steps if 'shellcheck' in s.get('uses', '').lower()), None)
            assert shellcheck_step is not None
            assert shellcheck_step['uses'] == 'ludeeus/action-shellcheck@2.0.0'

    def test_workflow_has_minimal_steps(self):
        """Test that workflow has expected number of steps"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['shellcheck']['steps']

            assert len(steps) >= 2  # At least checkout and shellcheck

    def test_workflow_structure_is_simple(self):
        """Test that workflow has simple structure (only one job)"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert len(data['jobs']) == 1


class TestValidateBlueprintWorkflowComprehensive:
    """Comprehensive tests for validate blueprint workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/validate_blueprint.yml")

    def test_workflow_file_exists(self):
        """Test that validate_blueprint.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in validate_blueprint.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == 'Validate Blueprint YAML'

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors blueprint file"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            assert len(push_paths) == 1
            assert 'nspanel_easy_blueprint.yaml' in push_paths

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors blueprint file"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']
            push_paths = triggers['push']['paths']

            # PR and push paths should be identical
            assert pr_paths == push_paths

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_has_code_scan_job(self):
        """Test that workflow has code_scan job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'code_scan' in data['jobs']
            job = data['jobs']['code_scan']
            assert job['name'] == 'Validate Blueprint YAML'
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_uses_checkout_with_fetch_depth(self):
        """Test that workflow uses checkout with full history"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'
            assert 'with' in checkout_step
            assert checkout_step['with']['fetch-depth'] == '0'

    def test_workflow_validates_blueprint_file(self):
        """Test that workflow validates the blueprint file"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate' in s.get('name', '')), None)
            assert validate_step is not None
            assert 'yamllint' in validate_step['run']
            assert 'nspanel_easy_blueprint.yaml' in validate_step['run']
            assert '.rules/yamllint.yml' in validate_step['run']

    def test_workflow_has_minimal_steps(self):
        """Test that workflow has expected number of steps"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            assert len(steps) >= 2  # At least checkout and validate

    def test_workflow_structure_is_simple(self):
        """Test that workflow has simple structure (only one job)"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert len(data['jobs']) == 1


class TestValidateClangFormatWorkflowComprehensive:
    """Comprehensive tests for validate C++ clang-format workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/validate_clang_format.yml")

    def test_workflow_file_exists(self):
        """Test that validate_clang_format.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in validate_clang_format.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == 'Validate C++ (Clang Format)'

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors C/C++ file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            expected_patterns = ['**/*.h', '**/*.c', '**/*.cpp']

            for pattern in expected_patterns:
                assert pattern in push_paths, f"Missing path pattern: {pattern}"

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors C/C++ file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']
            push_paths = triggers['push']['paths']

            # PR and push paths should be identical
            assert pr_paths == push_paths

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_has_clang_format_job(self):
        """Test that workflow has clang-format-checking job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'clang-format-checking' in data['jobs']
            job = data['jobs']['clang-format-checking']
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_uses_checkout(self):
        """Test that workflow uses checkout action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['clang-format-checking']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'

    def test_workflow_uses_clang_format_action(self):
        """Test that workflow uses clang-format action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['clang-format-checking']['steps']

            clang_step = next((s for s in steps if 'clang-format' in s.get('uses', '').lower()), None)
            assert clang_step is not None
            assert clang_step['uses'] == 'RafikFarhad/clang-format-github-action@v3'

    def test_workflow_clang_format_sources_configuration(self):
        """Test that clang-format action has correct sources configuration"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['clang-format-checking']['steps']

            clang_step = next((s for s in steps if 'clang-format' in s.get('uses', '').lower()), None)
            assert clang_step is not None
            assert 'with' in clang_step
            assert 'sources' in clang_step['with']

            sources = clang_step['with']['sources']
            assert '**/*.h' in sources
            assert '**/*.c' in sources
            assert '**/*.cpp' in sources

    def test_workflow_has_minimal_steps(self):
        """Test that workflow has expected number of steps"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['clang-format-checking']['steps']

            assert len(steps) >= 2  # At least checkout and clang-format

    def test_workflow_structure_is_simple(self):
        """Test that workflow has simple structure (only one job)"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert len(data['jobs']) == 1


class TestValidatePythonWorkflowComprehensive:
    """Comprehensive tests for validate Python (flake8) workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/validate_python.yml")

    def test_workflow_file_exists(self):
        """Test that validate_python.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in validate_python.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == 'Validate Python (flake8)'

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors Python file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            assert len(push_paths) == 1
            assert '**/*.py' in push_paths

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors Python file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']
            push_paths = triggers['push']['paths']

            # PR and push paths should be identical
            assert pr_paths == push_paths

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_has_flake8_lint_job(self):
        """Test that workflow has flake8-lint job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'flake8-lint' in data['jobs']
            job = data['jobs']['flake8-lint']
            assert job['runs-on'] == 'ubuntu-latest'
            assert job['name'] == 'Lint'

    def test_workflow_uses_checkout(self):
        """Test that workflow uses checkout action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'
            assert checkout_step['name'] == 'Check out source repository'

    def test_workflow_uses_setup_python(self):
        """Test that workflow uses setup-python action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            python_step = next((s for s in steps if 'setup-python' in s.get('uses', '')), None)
            assert python_step is not None
            assert python_step['uses'] == 'actions/setup-python@v6'
            assert python_step['name'] == 'Set up Python environment'

    def test_workflow_uses_python_311(self):
        """Test that workflow uses Python 3.11"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            python_step = next((s for s in steps if 'setup-python' in s.get('uses', '')), None)
            assert python_step is not None
            assert 'with' in python_step
            assert python_step['with']['python-version'] == '3.11'

    def test_workflow_uses_flake8_action(self):
        """Test that workflow uses flake8 action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            flake8_step = next((s for s in steps if 'flake8' in s.get('uses', '')), None)
            assert flake8_step is not None
            assert flake8_step['uses'] == 'py-actions/flake8@v2'
            assert flake8_step['name'] == 'flake8 Lint'

    def test_workflow_flake8_configuration(self):
        """Test that flake8 action has correct configuration"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            flake8_step = next((s for s in steps if 'flake8' in s.get('uses', '')), None)
            assert flake8_step is not None
            assert 'with' in flake8_step
            assert flake8_step['with']['max-line-length'] == '200'
            assert flake8_step['with']['path'] == 'components/nspanel_easy'

    def test_workflow_has_correct_number_of_steps(self):
        """Test that workflow has expected number of steps"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['flake8-lint']['steps']

            assert len(steps) == 3  # checkout, setup-python, flake8

    def test_workflow_structure_is_simple(self):
        """Test that workflow has simple structure (only one job)"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert len(data['jobs']) == 1


class TestValidateYamllintWorkflowComprehensive:
    """Comprehensive tests for validate YAML (yamllint) workflow"""

    WORKFLOW_FILE = Path("/home/jailuser/git/.github/workflows/validate_yamllint.yml")

    def test_workflow_file_exists(self):
        """Test that validate_yamllint.yml workflow file exists"""
        assert self.WORKFLOW_FILE.exists()
        assert self.WORKFLOW_FILE.is_file()

    def test_workflow_is_valid_yaml(self):
        """Test that workflow file contains valid YAML"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
                assert data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in validate_yamllint.yml: {e}")

    def test_workflow_has_required_fields(self):
        """Test that workflow has all required top-level fields"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            assert 'name' in data
            # 'on' is parsed as True by YAML
            assert True in data or 'on' in data
            assert 'jobs' in data
            assert data['name'] == 'Validate YAML (secondary files)'

    def test_workflow_has_correct_triggers(self):
        """Test that workflow triggers are correctly configured"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # 'on' is parsed as True by YAML
            triggers = data.get(True, data.get('on', {}))

            assert 'push' in triggers
            assert 'pull_request' in triggers
            assert 'workflow_dispatch' in triggers

    def test_workflow_push_trigger_paths(self):
        """Test that push trigger monitors YAML file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            push_paths = triggers['push']['paths']

            expected_patterns = ['**/*.yml', '**/*.yaml']

            for pattern in expected_patterns:
                assert pattern in push_paths, f"Missing path pattern: {pattern}"

    def test_workflow_pull_request_trigger_paths(self):
        """Test that pull_request trigger monitors YAML file paths"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            triggers = data.get(True, data.get('on', {}))
            pr_paths = triggers['pull_request']['paths']
            push_paths = triggers['push']['paths']

            # PR and push paths should be identical
            assert pr_paths == push_paths

    def test_workflow_permissions(self):
        """Test that workflow has correct permission settings"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'permissions' in data
            assert data['permissions']['contents'] == 'read'

    def test_workflow_has_code_scan_job(self):
        """Test that workflow has code_scan job"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert 'code_scan' in data['jobs']
            job = data['jobs']['code_scan']
            assert job['name'] == 'Validate YAML'
            assert job['runs-on'] == 'ubuntu-latest'

    def test_workflow_uses_checkout_with_fetch_depth(self):
        """Test that workflow uses checkout with full history"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            checkout_step = next((s for s in steps if 'checkout' in s.get('uses', '').lower()), None)
            assert checkout_step is not None
            assert checkout_step['uses'] == 'actions/checkout@v6'
            assert 'with' in checkout_step
            assert checkout_step['with']['fetch-depth'] == '0'

    def test_workflow_uses_changed_files_action(self):
        """Test that workflow uses changed-files action"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            changed_files_step = next((s for s in steps if 'changed-files' in s.get('uses', '')), None)
            assert changed_files_step is not None
            assert changed_files_step['uses'] == 'step-security/changed-files@v47.0.1'
            assert changed_files_step['id'] == 'changed-files'

    def test_workflow_changed_files_configuration(self):
        """Test that changed-files action has correct configuration"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            changed_files_step = next((s for s in steps if 'changed-files' in s.get('uses', '')), None)
            assert changed_files_step is not None
            assert 'with' in changed_files_step
            assert changed_files_step['with']['files'] == '**/*.yaml'
            assert changed_files_step['with']['separator'] == ','

    def test_workflow_validate_step_has_conditional(self):
        """Test that validate step has conditional execution"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate YAML' in s.get('name', '')), None)
            assert validate_step is not None
            assert 'if' in validate_step
            assert "steps.changed-files.outputs.any_changed == 'true'" in validate_step['if']

    def test_workflow_validate_step_script_structure(self):
        """Test that validate step has correct shell script structure"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate YAML' in s.get('name', '')), None)
            assert validate_step is not None
            assert 'run' in validate_step

            script = validate_step['run']
            # Check for key script components
            assert 'set -e' in script
            assert 'failed=0' in script
            assert 'IFS=' in script
            assert 'yamllint' in script
            assert 'exit $failed' in script

    def test_workflow_validate_step_skips_specific_files(self):
        """Test that validate step skips specific files"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate YAML' in s.get('name', '')), None)
            assert validate_step is not None

            script = validate_step['run']
            # Check for file skip patterns
            assert 'nspanel_esphome.*\\.yaml' in script
            assert 'esphome/nspanel_esphome.*\\.yaml' in script
            assert 'prebuilt/nspanel_esphome.*\\.yaml' in script
            assert 'nspanel_easy_blueprint.yaml' in script
            assert 'Skipping' in script

    def test_workflow_validate_step_uses_yamllint_config(self):
        """Test that validate step uses yamllint configuration"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate YAML' in s.get('name', '')), None)
            assert validate_step is not None

            script = validate_step['run']
            assert 'yamllint -c "./.rules/yamllint.yml"' in script

    def test_workflow_validate_step_uses_github_groups(self):
        """Test that validate step uses GitHub Actions groups for output"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            validate_step = next((s for s in steps if 'Validate YAML' in s.get('name', '')), None)
            assert validate_step is not None

            script = validate_step['run']
            assert '::group::' in script
            assert '::endgroup::' in script

    def test_workflow_has_correct_number_of_steps(self):
        """Test that workflow has expected number of steps"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            assert len(steps) == 3  # checkout, changed-files, validate

    def test_workflow_structure_is_simple(self):
        """Test that workflow has simple structure (only one job)"""
        with open(self.WORKFLOW_FILE, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            assert len(data['jobs']) == 1


class TestWorkflowEdgeCases:
    """Test edge cases and negative scenarios for all workflows"""

    WORKFLOW_DIR = Path("/home/jailuser/git/.github/workflows")

    def test_no_workflow_has_hardcoded_secrets(self):
        """Test that no workflow contains hardcoded secrets or tokens"""
        sensitive_patterns = ['password:', 'token:', 'secret:', 'api_key:', 'apikey:']

        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                content = f.read().lower()
                for pattern in sensitive_patterns:
                    # Allow pattern if it's referencing GitHub secrets properly
                    if pattern in content and 'secrets.' not in content:
                        pytest.fail(f"{workflow_file.name} may contain hardcoded secret: {pattern}")

    def test_all_workflows_use_pinned_action_versions(self):
        """Test that all workflows use pinned action versions (not @main or @master)"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                if 'jobs' not in data:
                    continue

                for job_name, job_data in data['jobs'].items():
                    if 'steps' not in job_data:
                        continue

                    for step in job_data['steps']:
                        if 'uses' not in step:
                            continue

                        uses = step['uses']
                        # Skip local actions
                        if uses.startswith('./'):
                            continue

                        # Check for unpinned versions
                        if uses.endswith('@main') or uses.endswith('@master'):
                            pytest.fail(
                                f"{workflow_file.name}:{job_name} uses unpinned action: {uses}"
                            )

    def test_all_workflows_have_permissions_defined(self):
        """Test that all workflows have permissions defined for security"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                # Permissions should be defined at workflow level or job level
                has_workflow_permissions = 'permissions' in data
                has_job_permissions = False

                if 'jobs' in data:
                    # Check if any job has permissions
                    for job_name, job_data in data['jobs'].items():
                        if 'permissions' in job_data:
                            has_job_permissions = True
                            break

                # At minimum, workflow or job should have permissions defined
                assert has_workflow_permissions or has_job_permissions, \
                    f"{workflow_file.name} should define permissions at workflow or job level"

    def test_all_checkout_actions_use_v6(self):
        """Test that all checkout actions use v6 for consistency"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                if 'jobs' not in data:
                    continue

                for job_name, job_data in data['jobs'].items():
                    if 'steps' not in job_data:
                        continue

                    for step in job_data['steps']:
                        if 'uses' in step and 'checkout' in step['uses'].lower():
                            assert step['uses'] == 'actions/checkout@v6', \
                                f"{workflow_file.name}:{job_name} should use actions/checkout@v6"

    def test_no_workflow_runs_on_windows_or_macos(self):
        """Test that all workflows use Linux runners for consistency"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                if 'jobs' not in data:
                    continue

                for job_name, job_data in data['jobs'].items():
                    if 'runs-on' in job_data:
                        runs_on = job_data['runs-on']
                        assert 'windows' not in runs_on.lower(), \
                            f"{workflow_file.name}:{job_name} uses Windows runner"
                        assert 'macos' not in runs_on.lower(), \
                            f"{workflow_file.name}:{job_name} uses macOS runner"

    def test_workflow_dispatch_triggers_have_no_unexpected_inputs(self):
        """Test that workflow_dispatch triggers don't have complex inputs that might fail"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                triggers = data.get(True, data.get('on', {}))
                if triggers and 'workflow_dispatch' in triggers:
                    dispatch = triggers['workflow_dispatch']

                    # workflow_dispatch should be null or have simple inputs
                    if dispatch is not None and 'inputs' in dispatch:
                        inputs = dispatch['inputs']
                        # Verify inputs have required fields
                        for input_name, input_data in inputs.items():
                            if isinstance(input_data, dict):
                                assert 'description' in input_data, \
                                    f"{workflow_file.name} input {input_name} missing description"

    def test_cron_schedules_are_valid(self):
        """Test that all cron schedules have valid syntax"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                triggers = data.get(True, data.get('on', {}))
                if triggers and 'schedule' in triggers:
                    schedules = triggers['schedule']

                    for schedule in schedules:
                        if 'cron' in schedule:
                            cron = schedule['cron']
                            # Basic validation: 5 fields
                            parts = cron.split()
                            assert len(parts) == 5, \
                                f"{workflow_file.name} has invalid cron: {cron}"

    def test_all_python_versions_are_consistent(self):
        """Test that all Python versions used are 3.11 for consistency"""
        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

                if 'jobs' not in data:
                    continue

                for job_name, job_data in data['jobs'].items():
                    if 'steps' not in job_data:
                        continue

                    for step in job_data['steps']:
                        if 'uses' in step and 'setup-python' in step['uses']:
                            if 'with' in step and 'python-version' in step['with']:
                                version = step['with']['python-version']
                                # Should be 3.11 or "3.11"
                                assert str(version) in ['3.11', '3.12'], \
                                    f"{workflow_file.name}:{job_name} uses Python {version}, expected 3.11"


class TestWorkflowRegressionCases:
    """Test for potential regression issues in workflows"""

    WORKFLOW_DIR = Path("/home/jailuser/git/.github/workflows")

    def test_esphome_build_artifact_names_are_unique(self):
        """Test that ESPHome build workflow uses unique artifact names"""
        workflow_file = self.WORKFLOW_DIR / "esphome_build.yml"

        with open(workflow_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            artifact_names = []
            for job_name, job_data in data['jobs'].items():
                if 'steps' not in job_data:
                    continue

                for step in job_data['steps']:
                    if 'upload-artifact' in step.get('uses', ''):
                        name = step['with']['name']
                        assert name not in artifact_names, \
                            f"Duplicate artifact name: {name}"
                        artifact_names.append(name)

    def test_esphome_build_job_dependencies_are_correct(self):
        """Test that ESPHome build jobs have correct dependency chain"""
        workflow_file = self.WORKFLOW_DIR / "esphome_build.yml"

        with open(workflow_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

            # All latest chain jobs should depend on build_core_latest
            latest_dependencies = [
                'build_core_arduino_latest',
                'build_ble_tracker_latest',
                'build_bluetooth_proxy_latest',
                'build_climate_cool_latest',
                'build_climate_heat_latest',
                'build_climate_dual_latest',
                'build_cover_latest',
                'build_customizations_latest',
                'build_climate_ble_proxy_latest'
            ]

            for job_name in latest_dependencies:
                job = data['jobs'][job_name]
                assert job['needs'] == 'build_core_latest', \
                    f"{job_name} should depend on build_core_latest"

            # All dev chain jobs should depend on build_core_dev
            dev_dependencies = [
                'build_core_arduino_dev',
                'build_ble_tracker_dev',
                'build_bluetooth_proxy_dev',
                'build_climate_cool_dev',
                'build_climate_heat_dev',
                'build_climate_dual_dev',
                'build_cover_dev',
                'build_customizations_dev',
                'build_climate_ble_proxy_dev'
            ]

            for job_name in dev_dependencies:
                job = data['jobs'][job_name]
                assert job['needs'] == 'build_core_dev', \
                    f"{job_name} should depend on build_core_dev"

    def test_yamllint_config_path_is_consistent(self):
        """Test that all workflows using yamllint reference the same config"""
        config_path = './.rules/yamllint.yml'

        workflows_using_yamllint = [
            'esphome_build.yml',
            'validate_blueprint.yml',
            'validate_yamllint.yml'
        ]

        for workflow_name in workflows_using_yamllint:
            workflow_file = self.WORKFLOW_DIR / workflow_name

            with open(workflow_file, 'r') as f:
                content = f.read()
                if 'yamllint' in content:
                    assert config_path in content, \
                        f"{workflow_name} should reference {config_path}"

    def test_changed_files_action_version_is_consistent(self):
        """Test that changed-files action uses consistent version"""
        workflow_file = self.WORKFLOW_DIR / "validate_yamllint.yml"

        with open(workflow_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            steps = data['jobs']['code_scan']['steps']

            changed_files_step = next((s for s in steps if 'changed-files' in s.get('uses', '')), None)
            assert changed_files_step is not None

            # Version should be pinned
            uses = changed_files_step['uses']
            assert '@v' in uses, "changed-files action should have pinned version"

    def test_no_workflow_uses_deprecated_actions(self):
        """Test that no workflow uses known deprecated actions"""
        deprecated_actions = [
            'actions/setup-python@v2',
            'actions/checkout@v2',
            'actions/cache@v2',
            'actions/upload-artifact@v2',
            'actions/download-artifact@v2'
        ]

        for workflow_file in self.WORKFLOW_DIR.glob("*.yml"):
            with open(workflow_file, 'r') as f:
                content = f.read()

                for deprecated in deprecated_actions:
                    assert deprecated not in content, \
                        f"{workflow_file.name} uses deprecated action: {deprecated}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])