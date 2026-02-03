"""
Validation tests for configuration files.
Tests YAML, JSON, and other configuration file formats.
"""

import pytest
import yaml
import json
from pathlib import Path


class TestGitAttributes:
    """Test .gitattributes file"""

    FILE_PATH = Path("/home/jailuser/git/.gitattributes")

    def test_file_exists(self):
        """Test .gitattributes file exists"""
        assert self.FILE_PATH.exists()

    def test_file_not_empty(self):
        """Test .gitattributes file is not empty"""
        content = self.FILE_PATH.read_text()
        assert len(content.strip()) > 0

    def test_tft_files_marked_as_binary(self):
        """Test .tft files are marked as binary"""
        content = self.FILE_PATH.read_text()
        assert '*.tft binary' in content

    def test_hmi_files_marked_as_binary(self):
        """Test .HMI files are marked as binary"""
        content = self.FILE_PATH.read_text()
        assert '*.HMI binary' in content

    def test_no_duplicate_entries(self):
        """Test no duplicate pattern entries"""
        lines = self.FILE_PATH.read_text().strip().split('\n')
        # Filter out empty lines
        lines = [line for line in lines if line.strip()]
        patterns = [line.split()[0] for line in lines]
        assert len(patterns) == len(set(patterns)), "Duplicate patterns found"


class TestGitIgnore:
    """Test .gitignore file"""

    FILE_PATH = Path("/home/jailuser/git/.gitignore")

    def test_file_exists(self):
        """Test .gitignore file exists"""
        assert self.FILE_PATH.exists()

    def test_file_not_empty(self):
        """Test .gitignore file is not empty"""
        content = self.FILE_PATH.read_text()
        assert len(content.strip()) > 0

    def test_ignores_ds_store(self):
        """Test .DS_Store files are ignored"""
        content = self.FILE_PATH.read_text()
        assert '.DS_Store' in content

    def test_ignores_idea_directory(self):
        """Test .idea directory is ignored"""
        content = self.FILE_PATH.read_text()
        assert '.idea' in content

    def test_ignores_esphome_directory(self):
        """Test .esphome directory is ignored"""
        content = self.FILE_PATH.read_text()
        assert '.esphome' in content

    def test_ignores_pycache(self):
        """Test __pycache__ is ignored"""
        content = self.FILE_PATH.read_text()
        assert '__pycache__' in content

    def test_has_comments(self):
        """Test .gitignore has descriptive comments"""
        content = self.FILE_PATH.read_text()
        assert '#' in content


class TestYamlLintConfig:
    """Test yamllint configuration"""

    FILE_PATH = Path("/home/jailuser/git/.rules/yamllint.yml")

    def test_file_exists(self):
        """Test yamllint.yml exists"""
        assert self.FILE_PATH.exists()

    def test_valid_yaml(self):
        """Test file is valid YAML"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert data is not None

    def test_has_rules_section(self):
        """Test has rules section"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert 'rules' in data

    def test_line_length_configured(self):
        """Test line length is configured"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert 'line-length' in data['rules']
            assert data['rules']['line-length']['max'] == 200

    def test_key_duplicates_enabled(self):
        """Test key-duplicates rule is enabled"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert 'key-duplicates' in data['rules']
            assert data['rules']['key-duplicates'] == 'enable'

    def test_anchors_configuration(self):
        """Test anchors are properly configured"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert 'anchors' in data['rules']
            anchors = data['rules']['anchors']
            assert anchors['forbid-undeclared-aliases'] is True
            assert anchors['forbid-duplicated-anchors'] is True

    def test_yaml_files_patterns(self):
        """Test yaml-files patterns are defined"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert 'yaml-files' in data
            assert '*.yaml' in data['yaml-files']
            assert '*.yml' in data['yaml-files']


class TestMarkdownLintConfig:
    """Test markdownlint configuration"""

    FILE_PATH = Path("/home/jailuser/git/.rules/.markdownlint.jsonc")

    def test_file_exists(self):
        """Test .markdownlint.jsonc exists"""
        assert self.FILE_PATH.exists()

    def test_valid_json(self):
        """Test file is valid JSON (ignoring comments)"""
        content = self.FILE_PATH.read_text()
        # Remove comments for JSON parsing
        lines = [line for line in content.split('\n') if not line.strip().startswith('//')]
        json_content = '\n'.join(lines)
        data = json.loads(json_content)
        assert data is not None

    def test_line_length_configured(self):
        """Test MD013 (line length) is configured"""
        content = self.FILE_PATH.read_text()
        lines = [line for line in content.split('\n') if not line.strip().startswith('//')]
        json_content = '\n'.join(lines)
        data = json.loads(json_content)
        assert 'MD013' in data
        assert 'line_length' in data['MD013']
        assert data['MD013']['line_length'] == 200


class TestMLCConfig:
    """Test markdown link checker configuration"""

    FILE_PATH = Path("/home/jailuser/git/.rules/mlc_config.json")

    def test_file_exists(self):
        """Test mlc_config.json exists"""
        assert self.FILE_PATH.exists()

    def test_valid_json(self):
        """Test file is valid JSON"""
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            assert data is not None

    def test_has_ignore_patterns(self):
        """Test has ignorePatterns section"""
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            assert 'ignorePatterns' in data
            assert isinstance(data['ignorePatterns'], list)
            assert len(data['ignorePatterns']) > 0

    def test_ignores_local_homeassistant(self):
        """Test ignores local homeassistant URLs"""
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            patterns = [p['pattern'] for p in data['ignorePatterns']]
            has_homeassistant = any('homeassistant' in p and 'local' in p for p in patterns)
            assert has_homeassistant

    def test_patterns_are_valid_regex(self):
        """Test all patterns are valid regex"""
        import re
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            for item in data['ignorePatterns']:
                pattern = item['pattern']
                # Remove ^ and $ for basic validation
                pattern = pattern.replace('^', '').replace('$', '')
                try:
                    re.compile(pattern)
                except re.error:
                    pytest.fail(f"Invalid regex pattern: {pattern}")


class TestVSCodeSettings:
    """Test VS Code settings"""

    FILE_PATH = Path("/home/jailuser/git/.vscode/settings.json")

    def test_file_exists(self):
        """Test settings.json exists"""
        assert self.FILE_PATH.exists()

    def test_valid_json(self):
        """Test file is valid JSON"""
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            assert data is not None

    def test_yaml_association_configured(self):
        """Test YAML files associated with home-assistant"""
        with open(self.FILE_PATH, 'r') as f:
            data = json.load(f)
            assert 'files.associations' in data
            assert '*.yaml' in data['files.associations']
            assert data['files.associations']['*.yaml'] == 'home-assistant'


class TestIssueTemplates:
    """Test GitHub issue templates"""

    TEMPLATE_DIR = Path("/home/jailuser/git/.github/ISSUE_TEMPLATE")

    def test_template_directory_exists(self):
        """Test issue template directory exists"""
        assert self.TEMPLATE_DIR.exists()
        assert self.TEMPLATE_DIR.is_dir()

    def test_bug_template_exists(self):
        """Test bug template exists"""
        bug_template = self.TEMPLATE_DIR / "bug.yml"
        assert bug_template.exists()

    def test_enhancement_template_exists(self):
        """Test enhancement template exists"""
        enhancement_template = self.TEMPLATE_DIR / "enhancement.yml"
        assert enhancement_template.exists()

    def test_config_file_exists(self):
        """Test config.yml exists"""
        config_file = self.TEMPLATE_DIR / "config.yml"
        assert config_file.exists()


class TestBugTemplate:
    """Test bug report template"""

    FILE_PATH = Path("/home/jailuser/git/.github/ISSUE_TEMPLATE/bug.yml")

    @pytest.fixture
    def template_data(self):
        """Load template data"""
        with open(self.FILE_PATH, 'r') as f:
            return yaml.safe_load(f)

    def test_valid_yaml(self):
        """Test template is valid YAML"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert data is not None

    def test_has_required_fields(self, template_data):
        """Test template has required fields"""
        assert 'name' in template_data
        assert 'description' in template_data
        assert 'title' in template_data
        assert 'labels' in template_data
        assert 'body' in template_data

    def test_name_is_bug_report(self, template_data):
        """Test template name is Bug Report"""
        assert template_data['name'] == "Bug Report"

    def test_has_bug_label(self, template_data):
        """Test template has Bug label"""
        assert 'Bug' in template_data['labels']

    def test_title_prefix(self, template_data):
        """Test title has prefix"""
        assert '`Bug`' in template_data['title']

    def test_has_version_fields(self, template_data):
        """Test template has version input fields"""
        body = template_data['body']
        input_fields = [item for item in body if item.get('type') == 'input']

        labels = [field['attributes']['label'] for field in input_fields if 'attributes' in field]
        assert 'TFT Version' in labels
        assert 'Firmware Version' in labels
        assert 'Blueprint Version' in labels

    def test_has_panel_model_dropdown(self, template_data):
        """Test template has panel model dropdown"""
        body = template_data['body']
        dropdowns = [item for item in body if item.get('type') == 'dropdown']
        assert len(dropdowns) > 0

        # Check for panel model options
        for dropdown in dropdowns:
            if dropdown['attributes']['label'] == 'Panel Model':
                options = dropdown['attributes']['options']
                assert 'EU' in options
                assert 'US' in options

    def test_has_steps_to_reproduce(self, template_data):
        """Test template has steps to reproduce field"""
        body = template_data['body']
        textareas = [item for item in body if item.get('type') == 'textarea']

        labels = [field['attributes']['label'] for field in textareas if 'attributes' in field]
        assert 'Steps to Reproduce' in labels


class TestEnhancementTemplate:
    """Test enhancement request template"""

    FILE_PATH = Path("/home/jailuser/git/.github/ISSUE_TEMPLATE/enhancement.yml")

    @pytest.fixture
    def template_data(self):
        """Load template data"""
        with open(self.FILE_PATH, 'r') as f:
            return yaml.safe_load(f)

    def test_valid_yaml(self):
        """Test template is valid YAML"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert data is not None

    def test_has_required_fields(self, template_data):
        """Test template has required fields"""
        assert 'name' in template_data
        assert 'description' in template_data
        assert 'title' in template_data
        assert 'labels' in template_data
        assert 'body' in template_data

    def test_name_is_enhancement_request(self, template_data):
        """Test template name is Enhancement Request"""
        assert template_data['name'] == "Enhancement Request"

    def test_has_enhancement_label(self, template_data):
        """Test template has Enhancement label"""
        assert 'Enhancement' in template_data['labels']

    def test_has_summary_field(self, template_data):
        """Test template has enhancement summary field"""
        body = template_data['body']
        inputs = [item for item in body if item.get('type') == 'input']

        labels = [field['attributes']['label'] for field in inputs if 'attributes' in field]
        assert 'Enhancement Summary' in labels

    def test_summary_is_required(self, template_data):
        """Test summary field is required"""
        body = template_data['body']
        for item in body:
            if item.get('type') == 'input':
                if item['attributes']['label'] == 'Enhancement Summary':
                    assert item['validations']['required'] is True

    def test_has_detailed_description(self, template_data):
        """Test template has detailed description field"""
        body = template_data['body']
        textareas = [item for item in body if item.get('type') == 'textarea']

        labels = [field['attributes']['label'] for field in textareas if 'attributes' in field]
        assert 'Detailed Description' in labels


class TestIssueTemplateConfig:
    """Test issue template configuration"""

    FILE_PATH = Path("/home/jailuser/git/.github/ISSUE_TEMPLATE/config.yml")

    @pytest.fixture
    def config_data(self):
        """Load config data"""
        with open(self.FILE_PATH, 'r') as f:
            return yaml.safe_load(f)

    def test_valid_yaml(self):
        """Test config is valid YAML"""
        with open(self.FILE_PATH, 'r') as f:
            data = yaml.safe_load(f)
            assert data is not None

    def test_blank_issues_disabled(self, config_data):
        """Test blank issues are disabled"""
        assert config_data['blank_issues_enabled'] is False

    def test_has_contact_links(self, config_data):
        """Test has contact links"""
        assert 'contact_links' in config_data
        assert len(config_data['contact_links']) > 0

    def test_contact_links_have_required_fields(self, config_data):
        """Test contact links have required fields"""
        for link in config_data['contact_links']:
            assert 'name' in link
            assert 'url' in link
            assert 'about' in link

    def test_has_troubleshooting_link(self, config_data):
        """Test has TFT troubleshooting link"""
        links = config_data['contact_links']
        names = [link['name'] for link in links]
        has_tft_link = any('TFT' in name or 'Troubleshooting' in name for name in names)
        assert has_tft_link

    def test_has_getting_started_link(self, config_data):
        """Test has getting started guide link"""
        links = config_data['contact_links']
        names = [link['name'] for link in links]
        has_getting_started = any('Getting Started' in name or 'Guide' in name for name in names)
        assert has_getting_started


class TestConfigurationConsistency:
    """Test consistency across configuration files"""

    def test_line_length_consistency(self):
        """Test line length is consistent across configs"""
        # Yamllint config
        with open(Path("/home/jailuser/git/.rules/yamllint.yml"), 'r') as f:
            yamllint_data = yaml.safe_load(f)
            yamllint_line_length = yamllint_data['rules']['line-length']['max']

        # Markdownlint config
        content = Path("/home/jailuser/git/.rules/.markdownlint.jsonc").read_text()
        lines = [line for line in content.split('\n') if not line.strip().startswith('//')]
        json_content = '\n'.join(lines)
        markdownlint_data = json.loads(json_content)
        markdownlint_line_length = markdownlint_data['MD013']['line_length']

        # Should both be 200
        assert yamllint_line_length == 200
        assert markdownlint_line_length == 200
        assert yamllint_line_length == markdownlint_line_length

    def test_all_config_files_are_tracked(self):
        """Test all config files are properly tracked by git"""
        gitignore_content = Path("/home/jailuser/git/.gitignore").read_text()

        # Config files should not be ignored
        config_patterns = ['.rules', '.vscode/settings.json', '.gitattributes']
        for pattern in config_patterns:
            assert pattern not in gitignore_content or f'!{pattern}' in gitignore_content


class TestConfigurationEdgeCases:
    """Test edge cases and potential issues"""

    def test_no_trailing_whitespace_in_gitignore(self):
        """Test .gitignore has no trailing whitespace"""
        lines = Path("/home/jailuser/git/.gitignore").read_text().split('\n')
        for i, line in enumerate(lines):
            if line and not line.startswith('#'):
                assert line == line.rstrip(), f"Line {i+1} has trailing whitespace"

    def test_json_files_properly_formatted(self):
        """Test JSON files are properly formatted"""
        json_files = [
            Path("/home/jailuser/git/.rules/mlc_config.json"),
            Path("/home/jailuser/git/.vscode/settings.json")
        ]

        for json_file in json_files:
            with open(json_file, 'r') as f:
                content = f.read()
                # Should be valid JSON
                data = json.loads(content)
                # Re-encode and check it's valid
                reencoded = json.dumps(data, indent=2)
                assert len(reencoded) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])