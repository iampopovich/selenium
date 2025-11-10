# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Unit tests for ChromiumDriver ClientConfig support."""

from unittest.mock import Mock, patch

import pytest

from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.service import ChromiumService
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.client_config import ClientConfig


@pytest.fixture
def mock_driver_service():
    """Mock ChromiumService for testing."""
    service = Mock(spec=ChromiumService)
    service.service_url = "http://localhost:9515"
    return service


@pytest.fixture
def driver_options():
    """Create ChromiumOptions for testing."""
    options = ChromiumOptions()
    return options


class TestChromiumDriverClientConfig:
    """Test cases for ChromiumDriver ClientConfig initialization and usage."""

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_accepts_client_config(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that ChromiumDriver accepts ClientConfig parameter."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        client_config = ClientConfig(
            remote_server_addr="http://localhost:9515",
            keep_alive=True,
            timeout=30,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                client_config=client_config,
            )

        # Assert
        # Verify RemoteConnection was called with the client_config
        assert mock_remote_connection.called
        call_kwargs = mock_remote_connection.call_args[1]
        assert call_kwargs["client_config"] == client_config

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_creates_default_client_config_when_not_provided(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that ChromiumDriver creates default ClientConfig when not provided."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                keep_alive=True,
            )

        # Assert
        # Verify RemoteConnection was called with a ClientConfig
        assert mock_remote_connection.called
        call_kwargs = mock_remote_connection.call_args[1]
        client_config = call_kwargs["client_config"]
        assert isinstance(client_config, ClientConfig)
        assert client_config.remote_server_addr == mock_driver_service.service_url
        assert client_config.keep_alive is True
        assert client_config.timeout == 120

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_normalizes_remote_server_addr_from_service(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that ChromiumDriver normalizes remote_server_addr from service URL."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        # Create client_config without remote_server_addr
        client_config = ClientConfig(
            keep_alive=True,
            timeout=30,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                client_config=client_config,
            )

        # Assert
        # Verify the remote_server_addr was set from service
        call_kwargs = mock_remote_connection.call_args[1]
        actual_config = call_kwargs["client_config"]
        assert actual_config.remote_server_addr == mock_driver_service.service_url

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_client_config_takes_precedence_over_keep_alive_parameter(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that ClientConfig settings take precedence over individual parameters."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        client_config = ClientConfig(
            remote_server_addr="http://localhost:9515",
            keep_alive=False,  # Explicitly set to False
            timeout=60,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                keep_alive=True,  # Trying to override with True
                client_config=client_config,
            )

        # Assert
        # Verify ClientConfig's keep_alive=False is used, not the parameter's keep_alive=True
        call_kwargs = mock_remote_connection.call_args[1]
        actual_config = call_kwargs["client_config"]
        assert actual_config.keep_alive is False
        assert actual_config.timeout == 60

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_preserves_client_config_attributes(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that all ClientConfig attributes are preserved when normalized."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        client_config = ClientConfig(
            keep_alive=False,
            timeout=45,
            ignore_certificates=True,
            user_agent="CustomAgent/1.0",
            websocket_timeout=15,
            websocket_interval=0.05,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                client_config=client_config,
            )

        # Assert
        call_kwargs = mock_remote_connection.call_args[1]
        actual_config = call_kwargs["client_config"]
        assert actual_config.remote_server_addr == mock_driver_service.service_url
        assert actual_config.keep_alive is False
        assert actual_config.timeout == 45
        assert actual_config.ignore_certificates is True
        assert actual_config.user_agent == "CustomAgent/1.0"
        assert actual_config.websocket_timeout == 15
        assert actual_config.websocket_interval == 0.05

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_passes_all_client_config_fields_to_remote_connection(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that all ClientConfig fields are passed to RemoteConnection."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        from selenium.webdriver.remote.client_config import AuthType

        client_config = ClientConfig(
            remote_server_addr="http://localhost:9515",
            keep_alive=True,
            timeout=30,
            ignore_certificates=False,
            username="testuser",
            password="testpass",
            auth_type=AuthType.BASIC,
            ca_certs="/path/to/certs",
            user_agent="TestAgent",
            websocket_timeout=10,
            websocket_interval=0.1,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                client_config=client_config,
            )

        # Assert
        call_kwargs = mock_remote_connection.call_args[1]
        actual_config = call_kwargs["client_config"]
        assert actual_config.remote_server_addr == "http://localhost:9515"
        assert actual_config.keep_alive is True
        assert actual_config.timeout == 30
        assert actual_config.ignore_certificates is False
        assert actual_config.username == "testuser"
        assert actual_config.password == "testpass"
        assert actual_config.auth_type == AuthType.BASIC
        assert actual_config.ca_certs == "/path/to/certs"
        assert actual_config.user_agent == "TestAgent"
        assert actual_config.websocket_timeout == 10
        assert actual_config.websocket_interval == 0.1

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_browser_name_and_vendor_prefix_passed_correctly(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that browser_name and vendor_prefix are passed to RemoteConnection."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        client_config = ClientConfig(
            remote_server_addr="http://localhost:9515",
            keep_alive=True,
        )

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                browser_name="chrome",
                vendor_prefix="goog",
                service=mock_driver_service,
                options=driver_options,
                client_config=client_config,
            )

        # Assert
        call_kwargs = mock_remote_connection.call_args[1]
        assert call_kwargs["browser_name"] == "chrome"
        assert call_kwargs["vendor_prefix"] == "goog"
        assert call_kwargs["client_config"] == client_config

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_default_keep_alive_is_true(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that default keep_alive parameter is True."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        # Act - Not providing keep_alive parameter (should default to True)
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
            )

        # Assert
        call_kwargs = mock_remote_connection.call_args[1]
        client_config = call_kwargs["client_config"]
        assert client_config.keep_alive is True

        driver.quit()

    @patch("selenium.webdriver.chromium.webdriver.DriverFinder")
    @patch("selenium.webdriver.chromium.webdriver.ChromiumRemoteConnection")
    def test_chromium_driver_client_config_none_creates_from_params(
        self, mock_remote_connection, mock_finder, mock_driver_service, driver_options
    ):
        """Test that None client_config uses keep_alive parameter."""
        # Arrange
        mock_finder.return_value.get_browser_path.return_value = None
        mock_finder.return_value.get_driver_path.return_value = "/path/to/driver"

        # Act
        with patch.object(mock_driver_service, "start"):
            driver = ChromiumDriver(
                service=mock_driver_service,
                options=driver_options,
                keep_alive=False,
                client_config=None,
            )

        # Assert
        call_kwargs = mock_remote_connection.call_args[1]
        client_config = call_kwargs["client_config"]
        assert client_config.keep_alive is False
        assert client_config.timeout == 120  # Default timeout

        driver.quit()
