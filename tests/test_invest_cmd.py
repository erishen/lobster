"""
Tests for Lobster Invest Commands.
投资命令测试
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lobster.commands.invest_cmd import invest, signals, portfolio, risk, signal, market


class TestInvestGroup:
    """测试投资命令组"""

    def test_invest_group_exists(self):
        """测试投资命令组存在"""
        assert isinstance(invest, click.Group)

    def test_invest_has_commands(self):
        """测试投资命令组包含命令"""
        assert "signals" in invest.commands
        assert "portfolio" in invest.commands
        assert "risk" in invest.commands
        assert "signal" in invest.commands
        assert "market" in invest.commands


class TestSignalsCommand:
    """测试信号命令"""

    def test_signals_no_api(self):
        """测试 API 不可用"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")

            result = runner.invoke(signals, ["--top", "5"])

            assert result.exit_code == 0

    def test_signals_with_data(self):
        """测试有信号数据"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "signals": [
                    {
                        "code": "000001",
                        "name": "平安银行",
                        "prediction": "up",
                        "confidence": 0.85,
                        "up_prob": 0.75,
                        "signal_strength": "strong",
                    },
                    {
                        "code": "000002",
                        "name": "万科A",
                        "prediction": "down",
                        "confidence": 0.70,
                        "up_prob": 0.30,
                        "signal_strength": "medium",
                    },
                ],
                "model_status": "loaded",
            }
            mock_get.return_value = mock_response

            result = runner.invoke(signals, ["--top", "10"])

            assert result.exit_code == 0

    def test_signals_empty(self):
        """测试无信号数据"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "signals": [],
                "model_status": "not_loaded",
            }
            mock_get.return_value = mock_response

            result = runner.invoke(signals)

            assert result.exit_code == 0


class TestPortfolioCommand:
    """测试投资组合命令"""

    def test_portfolio_basic(self):
        """测试基本投资组合"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_assets": 100000,
                "total_profit": 10000,
                "total_return": 10.0,
                "position_count": 5,
            }
            mock_get.return_value = mock_response

            result = runner.invoke(portfolio)

            assert result.exit_code == 0

    def test_portfolio_detailed(self):
        """测试详细投资组合"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_summary = MagicMock()
            mock_summary.status_code = 200
            mock_summary.json.return_value = {
                "total_assets": 100000,
                "total_profit": 10000,
                "total_return": 10.0,
                "position_count": 2,
            }

            mock_items = MagicMock()
            mock_items.status_code = 200
            mock_items.json.return_value = {
                "items": [
                    {
                        "name": "平安银行",
                        "investment_type": "股票",
                        "current_amount": 50000,
                        "profit_amount": 5000,
                        "return_rate": 10.0,
                    },
                ]
            }

            mock_get.side_effect = [mock_summary, mock_items]

            result = runner.invoke(portfolio, ["--detailed"])

            assert result.exit_code == 0

    def test_portfolio_negative_profit(self):
        """测试负收益投资组合"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "total_assets": 90000,
                "total_profit": -10000,
                "total_return": -10.0,
                "position_count": 5,
            }
            mock_get.return_value = mock_response

            result = runner.invoke(portfolio)

            assert result.exit_code == 0


class TestRiskCommand:
    """测试风险命令"""

    def test_risk_no_alerts(self):
        """测试无风险预警"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"alerts": []}
            mock_get.return_value = mock_response

            result = runner.invoke(risk)

            assert result.exit_code == 0

    def test_risk_with_alerts(self):
        """测试有风险预警"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "alerts": [
                    {
                        "level": "danger",
                        "type": "仓位过高",
                        "message": "当前仓位超过 80%",
                        "suggestion": "建议减仓",
                    },
                    {
                        "level": "warning",
                        "type": "集中度风险",
                        "message": "单一股票占比过高",
                        "suggestion": "建议分散投资",
                    },
                    {
                        "level": "info",
                        "type": "提醒",
                        "message": "定期检查投资组合",
                        "suggestion": "每周复盘",
                    },
                ]
            }
            mock_get.return_value = mock_response

            result = runner.invoke(risk)

            assert result.exit_code == 0


class TestSignalCommand:
    """测试单只股票信号命令"""

    def test_signal_success(self):
        """测试获取股票信号成功"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "signal": {
                    "prediction": "up",
                    "confidence": 0.85,
                    "up_prob": 0.75,
                    "down_prob": 0.25,
                }
            }
            mock_get.return_value = mock_response

            result = runner.invoke(signal, ["000001"])

            assert result.exit_code == 0

    def test_signal_not_found(self):
        """测试股票信号不存在"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "signal": None,
                "message": "股票未在模型中",
            }
            mock_get.return_value = mock_response

            result = runner.invoke(signal, ["999999"])

            assert result.exit_code == 0


class TestMarketCommand:
    """测试市场行情命令"""

    def test_market_with_data(self):
        """测试有市场数据"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "indexes": [
                    {
                        "name": "上证指数",
                        "price": 3000.00,
                        "change": 20.00,
                        "change_percent": 0.67,
                    },
                    {
                        "name": "深证成指",
                        "price": 10000.00,
                        "change": -50.00,
                        "change_percent": -0.50,
                    },
                ]
            }
            mock_get.return_value = mock_response

            result = runner.invoke(market)

            assert result.exit_code == 0

    def test_market_empty(self):
        """测试无市场数据"""
        runner = CliRunner()

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"indexes": []}
            mock_get.return_value = mock_response

            result = runner.invoke(market)

            assert result.exit_code == 0
