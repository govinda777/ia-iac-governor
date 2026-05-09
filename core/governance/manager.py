import yaml
from typing import List, Dict, Any, Type
from core.governance.base import GovernanceProvider, ValidationResult, GovernanceViolationError
from core.governance.providers.cost_provider import CostProvider
from core.governance.providers.opa_provider import OPAProvider
from core.governance.providers.firefly_provider import FireflyProvider

class GovernanceManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.providers: List[GovernanceProvider] = []
        self._load_config()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        provider_map: Dict[str, Type[GovernanceProvider]] = {
            "cost": CostProvider,
            "opa": OPAProvider,
            "firefly": FireflyProvider
        }

        for provider_cfg in config.get("providers", []):
            if provider_cfg.get("enabled", True):
                name = provider_cfg.get("name")
                fail_on = provider_cfg.get("fail_on", "CRITICAL")
                params = provider_cfg.get("params", {})

                provider_cls = provider_map.get(name)
                if provider_cls:
                    self.providers.append(provider_cls(name=name, fail_on=fail_on, params=params))
                else:
                    print(f"Warning: Provider '{name}' not found.")

    def validate_plan(self, plan_json: Dict[str, Any]) -> List[ValidationResult]:
        context = {}
        all_results = []

        severity_rank = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }

        for provider in self.providers:
            print(f"[GovernanceManager] Running provider: {provider.name}")
            result = provider.validate(plan_json, context)
            all_results.append(result)

            # Check for violations that should stop the pipeline
            fail_threshold = severity_rank.get(provider.fail_on, 4)

            critical_findings = [
                f for f in result.findings
                if severity_rank.get(f.severity, 0) >= fail_threshold
            ]

            if critical_findings:
                raise GovernanceViolationError(provider.name, critical_findings)

        return all_results
