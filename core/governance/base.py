from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ValidationFinding(BaseModel):
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    resource: Optional[str] = None
    remediation_patch: Optional[str] = None

class ValidationResult(BaseModel):
    provider: str
    status: str # APPROVED, DENIED
    findings: List[ValidationFinding] = Field(default_factory=list)

class GovernanceProvider(ABC):
    def __init__(self, name: str, fail_on: str = "CRITICAL", params: Dict[str, Any] = None):
        self.name = name
        self.fail_on = fail_on
        self.params = params or {}

    @abstractmethod
    def validate(self, plan_json: Dict[str, Any], context: Dict[str, Any]) -> ValidationResult:
        pass

class GovernanceViolationError(Exception):
    def __init__(self, provider_name: str, findings: List[ValidationFinding]):
        self.provider_name = provider_name
        self.findings = findings
        messages = [f"[{f.severity}] {f.message}" for f in findings]
        super().__init__(f"Governance violation in {provider_name}: {'; '.join(messages)}")
