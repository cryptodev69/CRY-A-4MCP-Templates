#!/usr/bin/env python3
"""
CRY-A-4MCP Interactive Setup Wizard

This wizard helps you configure your CRY-A-4MCP system based on your specific use case.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SetupWizard:
    def __init__(self):
        self.config = {}
        self.base_path = Path.cwd()
        
    def print_header(self):
        print(f"""
{Colors.BLUE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                CRY-A-4MCP Setup Wizard                      ║
║          Configure your crypto analysis platform            ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
        """)
    
    def ask_question(self, question: str, options: List[str] = None, default: str = None) -> str:
        """Ask a question with optional multiple choice"""
        print(f"\n{Colors.BOLD}{question}{Colors.END}")
        
        if options:
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = input(f"\nEnter choice (1-{len(options)}): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(options):
                        return options[int(choice) - 1]
                    else:
                        print(f"{Colors.RED}Invalid choice. Please enter 1-{len(options)}.{Colors.END}")
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Setup cancelled.{Colors.END}")
                    sys.exit(0)
        else:
            prompt = "Enter value"
            if default:
                prompt += f" (default: {default})"
            prompt += ": "
            
            response = input(prompt).strip()
            return response if response else default
    
    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{question} ({default_str}): ").strip().lower()
        
        if not response:
            return default
        return response in ['y', 'yes', 'true', '1']
    
    def select_use_case(self):
        """Select primary use case"""
        print(f"\n{Colors.GREEN}Step 1: Select Your Primary Use Case{Colors.END}")
        
        use_cases = [
            "Market Sentiment Analysis - News, social media, sentiment tracking",
            "Trading Signals - Technical analysis, signal generation, backtesting", 
            "Compliance Monitoring - Regulatory tracking, risk assessment, AML",
            "Custom Setup - Manual configuration for specific needs"
        ]
        
        choice = self.ask_question("What is your primary use case?", use_cases)
        
        if "Market Sentiment" in choice:
            self.config['variant'] = 'market-sentiment'
            self.config['use_case'] = 'sentiment'
        elif "Trading Signals" in choice:
            self.config['variant'] = 'trading-signals'
            self.config['use_case'] = 'trading'
        elif "Compliance" in choice:
            self.config['variant'] = 'compliance-monitoring'
            self.config['use_case'] = 'compliance'
        else:
            self.config['variant'] = 'base'
            self.config['use_case'] = 'custom'
    
    def configure_data_sources(self):
        """Configure data sources based on use case"""
        print(f"\n{Colors.GREEN}Step 2: Configure Data Sources{Colors.END}")
        
        if self.config['use_case'] == 'sentiment':
            # News sources
            news_sources = [
                "All major sources (CoinDesk, CoinTelegraph, Decrypt, TheBlock)",
                "Premium sources only (CoinDesk, TheBlock)",
                "Free sources only (CoinTelegraph, Decrypt)",
                "Custom selection"
            ]
            news_choice = self.ask_question("Select news sources:", news_sources)
            self.config['news_sources'] = news_choice
            
            # Social media
            if self.ask_yes_no("Enable social media monitoring?"):
                social_platforms = []
                if self.ask_yes_no("Include Twitter/X?"):
                    social_platforms.append("twitter")
                if self.ask_yes_no("Include Reddit?"):
                    social_platforms.append("reddit")
                if self.ask_yes_no("Include Discord?"):
                    social_platforms.append("discord")
                self.config['social_platforms'] = social_platforms
        
        elif self.config['use_case'] == 'trading':
            # Trading pairs
            pair_options = [
                "Major pairs (BTC/USD, ETH/USD, BNB/USD)",
                "Top 10 pairs (includes SOL, ADA, DOT, etc.)",
                "Top 50 pairs (comprehensive coverage)",
                "Custom selection"
            ]
            pairs_choice = self.ask_question("Select trading pairs:", pair_options)
            self.config['trading_pairs'] = pairs_choice
            
            # Timeframes
            if self.ask_yes_no("Include high-frequency data (1m, 5m)?"):
                self.config['hf_data'] = True
            
            # Exchanges
            exchanges = []
            if self.ask_yes_no("Include Binance data?", True):
                exchanges.append("binance")
            if self.ask_yes_no("Include Coinbase data?", True):
                exchanges.append("coinbase")
            if self.ask_yes_no("Include Kraken data?"):
                exchanges.append("kraken")
            self.config['exchanges'] = exchanges
        
        elif self.config['use_case'] == 'compliance':
            # Jurisdictions
            jurisdictions = []
            if self.ask_yes_no("Monitor US regulations (SEC, CFTC)?", True):
                jurisdictions.append("US")
            if self.ask_yes_no("Monitor EU regulations (ESMA, MiCA)?"):
                jurisdictions.append("EU")
            if self.ask_yes_no("Monitor UK regulations (FCA)?"):
                jurisdictions.append("UK")
            if self.ask_yes_no("Monitor Asian regulations (Japan, Singapore)?"):
                jurisdictions.append("ASIA")
            self.config['jurisdictions'] = jurisdictions
    
    def configure_performance(self):
        """Configure performance settings"""
        print(f"\n{Colors.GREEN}Step 3: Configure Performance Settings{Colors.END}")
        
        # Resource allocation
        resource_options = [
            "Low (4GB RAM, 2 CPU cores) - Basic usage",
            "Medium (8GB RAM, 4 CPU cores) - Standard usage", 
            "High (16GB RAM, 8 CPU cores) - Heavy usage",
            "Custom - Manual configuration"
        ]
        
        resource_choice = self.ask_question("Select resource allocation:", resource_options)
        
        if "Low" in resource_choice:
            self.config['resources'] = {'ram': '4g', 'cpu': '2', 'level': 'low'}
        elif "Medium" in resource_choice:
            self.config['resources'] = {'ram': '8g', 'cpu': '4', 'level': 'medium'}
        elif "High" in resource_choice:
            self.config['resources'] = {'ram': '16g', 'cpu': '8', 'level': 'high'}
        else:
            ram = self.ask_question("RAM allocation (e.g., 8g):", default="8g")
            cpu = self.ask_question("CPU cores:", default="4")
            self.config['resources'] = {'ram': ram, 'cpu': cpu, 'level': 'custom'}
        
        # Update frequency
        if self.config['use_case'] in ['sentiment', 'trading']:
            update_options = [
                "Real-time (< 1 minute) - High resource usage",
                "Fast (5 minutes) - Balanced performance",
                "Standard (15 minutes) - Lower resource usage",
                "Slow (1 hour) - Minimal resource usage"
            ]
            
            update_choice = self.ask_question("Select update frequency:", update_options)
            
            if "Real-time" in update_choice:
                self.config['update_frequency'] = 60
            elif "Fast" in update_choice:
                self.config['update_frequency'] = 300
            elif "Standard" in update_choice:
                self.config['update_frequency'] = 900
            else:
                self.config['update_frequency'] = 3600
    
    def configure_features(self):
        """Configure optional features"""
        print(f"\n{Colors.GREEN}Step 4: Configure Optional Features{Colors.END}")
        
        # Monitoring
        if self.ask_yes_no("Enable advanced monitoring (Grafana dashboards)?", True):
            self.config['monitoring'] = True
        
        # Alerts
        if self.ask_yes_no("Enable alert system?", True):
            self.config['alerts'] = True
            
            alert_methods = []
            if self.ask_yes_no("Email alerts?"):
                email = self.ask_question("Email address for alerts:")
                alert_methods.append({"type": "email", "address": email})
            
            if self.ask_yes_no("Webhook alerts?"):
                webhook = self.ask_question("Webhook URL:")
                alert_methods.append({"type": "webhook", "url": webhook})
            
            self.config['alert_methods'] = alert_methods
        
        # API access
        if self.ask_yes_no("Enable external API access?"):
            self.config['external_api'] = True
            
            # API keys (optional)
            if self.ask_yes_no("Configure API keys now? (can be done later)"):
                api_keys = {}
                
                if self.config['use_case'] == 'sentiment':
                    if self.ask_yes_no("Add Twitter API key?"):
                        api_keys['twitter'] = self.ask_question("Twitter Bearer Token:")
                    if self.ask_yes_no("Add Reddit API key?"):
                        api_keys['reddit'] = self.ask_question("Reddit API Key:")
                
                elif self.config['use_case'] == 'trading':
                    if self.ask_yes_no("Add CoinMarketCap API key?"):
                        api_keys['coinmarketcap'] = self.ask_question("CoinMarketCap API Key:")
                    if self.ask_yes_no("Add CoinGecko API key?"):
                        api_keys['coingecko'] = self.ask_question("CoinGecko API Key:")
                
                self.config['api_keys'] = api_keys
    
    def generate_config_files(self):
        """Generate configuration files based on selections"""
        print(f"\n{Colors.GREEN}Step 5: Generating Configuration Files{Colors.END}")
        
        # Create variant directory if needed
        variant_path = self.base_path / "variants" / self.config['variant']
        if not variant_path.exists() and self.config['variant'] != 'base':
            print(f"Creating variant directory: {variant_path}")
            variant_path.mkdir(parents=True, exist_ok=True)
        
        # Generate .env file
        env_content = self.generate_env_file()
        env_path = variant_path / ".env" if self.config['variant'] != 'base' else self.base_path / ".env"
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Generated environment configuration: {env_path}")
        
        # Generate docker-compose override
        if self.config.get('resources'):
            compose_override = self.generate_compose_override()
            compose_path = variant_path / "docker-compose.override.yml" if self.config['variant'] != 'base' else self.base_path / "docker-compose.override.yml"
            
            with open(compose_path, 'w') as f:
                f.write(compose_override)
            
            print(f"✅ Generated Docker Compose override: {compose_path}")
        
        # Generate setup script
        setup_script = self.generate_setup_script()
        script_path = variant_path / "setup_generated.sh" if self.config['variant'] != 'base' else self.base_path / "setup_generated.sh"
        
        with open(script_path, 'w') as f:
            f.write(setup_script)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Generated setup script: {script_path}")
        
        # Save configuration for reference
        config_path = variant_path / "wizard_config.json" if self.config['variant'] != 'base' else self.base_path / "wizard_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✅ Saved configuration: {config_path}")
    
    def generate_env_file(self) -> str:
        """Generate .env file content"""
        env_lines = [
            "# CRY-A-4MCP Configuration",
            "# Generated by Setup Wizard",
            "",
            "# Application Settings",
            f"CRYA4MCP_ENVIRONMENT=development",
            f"CRYA4MCP_LOG_LEVEL=INFO",
            f"CRYA4MCP_VARIANT={self.config['variant']}",
            "",
            "# Database Settings",
            "CRYA4MCP_QDRANT_URL=http://qdrant:6333",
            "CRYA4MCP_NEO4J_URI=bolt://neo4j:7687",
            "CRYA4MCP_NEO4J_PASSWORD=cry-a-4mcp-password",
            "",
        ]
        
        # Use case specific settings
        if self.config['use_case'] == 'sentiment':
            env_lines.extend([
                "# Sentiment Analysis Settings",
                f"CRYA4MCP_SENTIMENT_MODEL=finbert-crypto",
                f"CRYA4MCP_NEWS_SOURCES={','.join(self.config.get('news_sources', []))}",
                f"CRYA4MCP_SOCIAL_PLATFORMS={','.join(self.config.get('social_platforms', []))}",
                f"CRYA4MCP_SENTIMENT_UPDATE_INTERVAL={self.config.get('update_frequency', 300)}",
                "",
            ])
        
        elif self.config['use_case'] == 'trading':
            env_lines.extend([
                "# Trading Settings",
                f"CRYA4MCP_TRADING_PAIRS=BTC/USD,ETH/USD,SOL/USD",
                f"CRYA4MCP_TIMEFRAMES=1m,5m,15m,1h,4h,1d",
                f"CRYA4MCP_EXCHANGES={','.join(self.config.get('exchanges', ['binance']))}",
                f"CRYA4MCP_UPDATE_FREQUENCY={self.config.get('update_frequency', 300)}",
                "",
            ])
        
        elif self.config['use_case'] == 'compliance':
            env_lines.extend([
                "# Compliance Settings",
                f"CRYA4MCP_JURISDICTIONS={','.join(self.config.get('jurisdictions', ['US']))}",
                f"CRYA4MCP_REGULATORY_SOURCES=sec,cftc,fca,jfsa,mas",
                f"CRYA4MCP_COMPLIANCE_LEVEL=strict",
                "",
            ])
        
        # API Keys
        if self.config.get('api_keys'):
            env_lines.append("# API Keys")
            for service, key in self.config['api_keys'].items():
                env_lines.append(f"CRYA4MCP_{service.upper()}_API_KEY={key}")
            env_lines.append("")
        
        # Monitoring
        if self.config.get('monitoring'):
            env_lines.extend([
                "# Monitoring Settings",
                "CRYA4MCP_MONITORING_ENABLED=true",
                "CRYA4MCP_GRAFANA_ADMIN_PASSWORD=cry-a-4mcp-admin",
                "",
            ])
        
        return "\n".join(env_lines)
    
    def generate_compose_override(self) -> str:
        """Generate docker-compose override file"""
        resources = self.config.get('resources', {})
        
        override_content = f"""version: '3.8'

services:
  mcp-server:
    deploy:
      resources:
        limits:
          memory: {resources.get('ram', '8g')}
          cpus: '{resources.get('cpu', '4')}'
        reservations:
          memory: {int(resources.get('ram', '8g')[:-1]) // 2}g
          cpus: '{int(resources.get('cpu', '4')) // 2}'

  qdrant:
    deploy:
      resources:
        limits:
          memory: {int(resources.get('ram', '8g')[:-1]) // 4}g
          cpus: '{int(resources.get('cpu', '4')) // 2}'

  neo4j:
    deploy:
      resources:
        limits:
          memory: {int(resources.get('ram', '8g')[:-1]) // 4}g
          cpus: '{int(resources.get('cpu', '4')) // 2}'
"""
        
        return override_content
    
    def generate_setup_script(self) -> str:
        """Generate setup script"""
        script_lines = [
            "#!/bin/bash",
            "",
            "# CRY-A-4MCP Generated Setup Script",
            "# Generated by Setup Wizard",
            "",
            "set -e",
            "",
            "echo 'Starting CRY-A-4MCP setup...'",
            "",
        ]
        
        # Variant-specific setup
        if self.config['variant'] != 'base':
            script_lines.extend([
                f"# Setup {self.config['variant']} variant",
                f"echo 'Configuring {self.config['variant']} variant...'",
                "",
            ])
        
        # Docker setup
        script_lines.extend([
            "# Start Docker services",
            "echo 'Starting Docker services...'",
            "docker-compose up -d",
            "",
            "# Wait for services to be ready",
            "echo 'Waiting for services to start...'",
            "sleep 30",
            "",
            "# Run health check",
            "echo 'Running health check...'",
            "./scripts/health_check.sh",
            "",
            "echo 'Setup complete!'",
            "echo 'Access your services at:'",
            "echo '  - Qdrant: http://localhost:6333'",
            "echo '  - Neo4j: http://localhost:7474'",
            "echo '  - n8n: http://localhost:5678'",
            "echo '  - Grafana: http://localhost:3000'",
            "echo '  - MCP Server: http://localhost:8000'",
        ])
        
        return "\n".join(script_lines)
    
    def show_summary(self):
        """Show configuration summary"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}Configuration Summary{Colors.END}")
        print("=" * 50)
        
        print(f"Use Case: {self.config['use_case']}")
        print(f"Variant: {self.config['variant']}")
        
        if self.config.get('resources'):
            resources = self.config['resources']
            print(f"Resources: {resources['ram']} RAM, {resources['cpu']} CPU cores")
        
        if self.config.get('update_frequency'):
            print(f"Update Frequency: {self.config['update_frequency']} seconds")
        
        if self.config.get('monitoring'):
            print("Monitoring: Enabled")
        
        if self.config.get('alerts'):
            print("Alerts: Enabled")
        
        print("\nNext Steps:")
        print("1. Review generated configuration files")
        print("2. Run the generated setup script")
        print("3. Access the services using the provided URLs")
        print("4. Check the documentation for usage examples")
    
    def run(self):
        """Run the setup wizard"""
        try:
            self.print_header()
            self.select_use_case()
            self.configure_data_sources()
            self.configure_performance()
            self.configure_features()
            self.generate_config_files()
            self.show_summary()
            
            print(f"\n{Colors.GREEN}Setup wizard completed successfully!{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.END}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Colors.RED}Error during setup: {e}{Colors.END}")
            sys.exit(1)

if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
