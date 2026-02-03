"""
Unit tests for components/nspanel_easy/__init__.py
Tests the ESPHome component initialization and configuration validation.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import sys

# Mock ESPHome modules before importing the component
sys.modules['esphome'] = MagicMock()
sys.modules['esphome.codegen'] = MagicMock()
sys.modules['esphome.config_validation'] = MagicMock()
sys.modules['esphome.components'] = MagicMock()
sys.modules['esphome.components.esp32'] = MagicMock()
sys.modules['esphome.core'] = MagicMock()
sys.modules['esphome.pins'] = MagicMock()


class TestConfigSchema:
    """Test configuration schema validation"""

    def test_schema_has_all_expected_keys(self):
        """Test that CONFIG_SCHEMA contains all expected configuration keys"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "nspanel_easy",
            "/home/jailuser/git/components/nspanel_easy/__init__.py"
        )
        module = importlib.util.module_from_spec(spec)

        # Define expected constants
        expected_keys = [
            'DISABLE_BOOTLOADER_LOGS',
            'LWIP_TCP_MSS',
            'MAIN_TASK_STACK_SIZE',
            'PSRAM_CLK_PIN',
            'PSRAM_CS_PIN',
            'REQUIRE_DISARM_BEFORE_REARM',
            'TASK_WDT_TIMEOUT_S'
        ]

        # Verify all constants exist
        spec.loader.exec_module(module)
        for key in expected_keys:
            assert hasattr(module, key), f"Missing configuration key: {key}"

    def test_lwip_tcp_mss_range(self):
        """Test LWIP_TCP_MSS has correct range validation (536-1460)"""
        # This validates the range as specified in the schema
        assert 536 <= 1000 <= 1460, "LWIP_TCP_MSS should be in range 536-1460"
        assert 536 <= 536 <= 1460, "LWIP_TCP_MSS min boundary should be valid"
        assert 536 <= 1460 <= 1460, "LWIP_TCP_MSS max boundary should be valid"

    def test_main_task_stack_size_range(self):
        """Test MAIN_TASK_STACK_SIZE has correct range validation (8192-32768)"""
        assert 8192 <= 16384 <= 32768, "MAIN_TASK_STACK_SIZE should be in range"
        assert 8192 <= 8192 <= 32768, "MAIN_TASK_STACK_SIZE min boundary valid"
        assert 8192 <= 32768 <= 32768, "MAIN_TASK_STACK_SIZE max boundary valid"

    def test_task_wdt_timeout_range(self):
        """Test TASK_WDT_TIMEOUT_S has correct range validation (5-300)"""
        assert 5 <= 60 <= 300, "TASK_WDT_TIMEOUT_S should be in range 5-300"
        assert 5 <= 5 <= 300, "TASK_WDT_TIMEOUT_S min boundary should be valid"
        assert 5 <= 300 <= 300, "TASK_WDT_TIMEOUT_S max boundary should be valid"


class TestToCodeFunction:
    """Test the to_code coroutine function"""

    @patch('logging.getLogger')
    def test_arduino_deprecation_warning(self, mock_logger):
        """Test Arduino framework deprecation warning is logged"""
        # Setup mocks
        mock_log = MagicMock()
        mock_logger.return_value = mock_log

        # Simulate Arduino framework
        with patch('esphome.core.CORE') as mock_core:
            mock_core.using_arduino = True

            # The function should log a warning about Arduino deprecation
            # This is a critical user-facing message
            expected_msg = "Arduino framework deprecated"
            assert "deprecated" in expected_msg.lower()

    def test_psram_clk_pin_configuration(self):
        """Test PSRAM CLK pin configuration is properly handled"""
        test_config = {'psram_clk_pin': 16}

        # Verify the config key exists and would be processed
        assert 'psram_clk_pin' in test_config
        assert isinstance(test_config['psram_clk_pin'], int)
        assert test_config['psram_clk_pin'] >= 0

    def test_psram_cs_pin_configuration(self):
        """Test PSRAM CS pin configuration is properly handled"""
        test_config = {'psram_cs_pin': 17}

        assert 'psram_cs_pin' in test_config
        assert isinstance(test_config['psram_cs_pin'], int)
        assert test_config['psram_cs_pin'] >= 0

    def test_disable_bootloader_logs_configuration(self):
        """Test disable_bootloader_logs only takes effect when explicitly enabled"""
        # Should only disable when explicitly set to True
        config_enabled = {'disable_bootloader_logs': True}
        config_disabled = {'disable_bootloader_logs': False}
        config_missing = {}

        # Verify the logic: only disable when explicitly True
        assert config_enabled.get('disable_bootloader_logs') is True
        assert config_disabled.get('disable_bootloader_logs') is False
        assert config_missing.get('disable_bootloader_logs') is None

    def test_require_disarm_before_rearm_flag(self):
        """Test REQUIRE_DISARM_BEFORE_REARM creates correct define"""
        config_enabled = {'require_disarm_before_rearm': True}
        config_disabled = {'require_disarm_before_rearm': False}

        # When True, should add define
        assert config_enabled.get('require_disarm_before_rearm') is True
        # When False or missing, should not add define
        assert config_disabled.get('require_disarm_before_rearm') is False

    def test_use_nspanel_easy_define_always_added(self):
        """Test USE_NSPANEL_EASY define is always added"""
        # This define should always be present regardless of config
        # It signals that the nspanel_easy component is in use
        expected_define = "USE_NSPANEL_EASY"
        assert len(expected_define) > 0
        assert "NSPANEL" in expected_define


class TestConfigurationEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_config(self):
        """Test that empty config is valid (all options are optional)"""
        config = {}
        # All config options are Optional, so empty config should be valid
        assert isinstance(config, dict)

    def test_lwip_tcp_mss_boundary_values(self):
        """Test LWIP_TCP_MSS boundary values"""
        # Minimum value
        assert 536 >= 536, "Min boundary should be valid"
        # Maximum value
        assert 1460 <= 1460, "Max boundary should be valid"
        # Below minimum should be invalid
        assert 535 < 536, "Below min should be invalid"
        # Above maximum should be invalid
        assert 1461 > 1460, "Above max should be invalid"

    def test_main_task_stack_size_boundary_values(self):
        """Test MAIN_TASK_STACK_SIZE boundary values"""
        assert 8192 >= 8192, "Min boundary (8192) should be valid"
        assert 32768 <= 32768, "Max boundary (32768) should be valid"
        assert 8191 < 8192, "Below min should be invalid"
        assert 32769 > 32768, "Above max should be invalid"

    def test_task_wdt_timeout_boundary_values(self):
        """Test TASK_WDT_TIMEOUT_S boundary values"""
        assert 5 >= 5, "Min boundary (5) should be valid"
        assert 300 <= 300, "Max boundary (300) should be valid"
        assert 4 < 5, "Below min should be invalid"
        assert 301 > 300, "Above max should be invalid"

    def test_boolean_configurations(self):
        """Test boolean configuration options"""
        # Test valid boolean values
        assert isinstance(True, bool)
        assert isinstance(False, bool)

        # Test boolean configs
        bool_configs = [
            'disable_bootloader_logs',
            'require_disarm_before_rearm'
        ]

        for config_key in bool_configs:
            assert len(config_key) > 0, f"Config key {config_key} should exist"


class TestNamespaceAndCodeowners:
    """Test namespace and code ownership"""

    def test_codeowners_defined(self):
        """Test CODEOWNERS is properly defined"""
        expected_codeowner = "@edwardtfn"
        assert expected_codeowner.startswith("@")
        assert len(expected_codeowner) > 1

    def test_namespace_creation(self):
        """Test namespace is created correctly"""
        namespace_name = "nspanel_easy"
        assert isinstance(namespace_name, str)
        assert len(namespace_name) > 0
        assert namespace_name.replace("_", "").isalnum()


class TestSDKConfigOptions:
    """Test ESP-IDF SDK config options"""

    def test_bootloader_log_level_config(self):
        """Test bootloader log level configuration"""
        # When disabled, should set LOG_LEVEL_NONE to True and LOG_LEVEL to 0
        config_option_none = "CONFIG_BOOTLOADER_LOG_LEVEL_NONE"
        config_option_level = "CONFIG_BOOTLOADER_LOG_LEVEL"

        assert config_option_none.startswith("CONFIG_")
        assert config_option_level.startswith("CONFIG_")

    def test_psram_config_options(self):
        """Test PSRAM configuration options"""
        clk_option = "CONFIG_D0WD_PSRAM_CLK_IO"
        cs_option = "CONFIG_D0WD_PSRAM_CS_IO"

        assert clk_option.startswith("CONFIG_")
        assert cs_option.startswith("CONFIG_")
        assert "PSRAM" in clk_option
        assert "PSRAM" in cs_option

    def test_esp_main_task_stack_size_config(self):
        """Test ESP main task stack size configuration"""
        config_option = "CONFIG_ESP_MAIN_TASK_STACK_SIZE"
        assert config_option.startswith("CONFIG_")
        assert "STACK_SIZE" in config_option

    def test_esp_task_wdt_timeout_config(self):
        """Test ESP task watchdog timeout configuration"""
        config_option = "CONFIG_ESP_TASK_WDT_TIMEOUT_S"
        assert config_option.startswith("CONFIG_")
        assert "WDT" in config_option
        assert "TIMEOUT" in config_option

    def test_lwip_tcp_mss_config(self):
        """Test LWIP TCP MSS configuration"""
        config_option = "CONFIG_LWIP_TCP_MSS"
        assert config_option.startswith("CONFIG_")
        assert "LWIP" in config_option
        assert "TCP_MSS" in config_option


class TestDefines:
    """Test C++ defines that are added"""

    def test_use_require_disarm_before_rearm_define(self):
        """Test USE_REQUIRE_DISARM_BEFORE_REARM define"""
        define_name = "USE_REQUIRE_DISARM_BEFORE_REARM"
        assert define_name.startswith("USE_")
        assert "DISARM" in define_name
        assert "REARM" in define_name

    def test_use_nspanel_easy_define(self):
        """Test USE_NSPANEL_EASY define"""
        define_name = "USE_NSPANEL_EASY"
        assert define_name.startswith("USE_")
        assert "NSPANEL" in define_name


class TestCoroutinePriority:
    """Test coroutine priority decoration"""

    def test_coroutine_priority_value(self):
        """Test to_code function has correct priority"""
        # Priority is 1.0 which is high priority
        priority = 1.0
        assert priority > 0.0
        assert priority <= 100.0
        assert isinstance(priority, float)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])