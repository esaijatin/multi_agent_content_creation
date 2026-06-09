class OrchestratorError(Exception):
    """Base orchestrator error."""

    def __init__(self, message: str, *, code: str = "orchestrator_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ModelServiceError(OrchestratorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="model_service_error")


class CheckpointError(OrchestratorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="checkpoint_error")


class ValidationError(OrchestratorError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class WorkflowNotFoundError(OrchestratorError):
    def __init__(self, thread_id: str) -> None:
        super().__init__(f"Workflow thread not found: {thread_id}", code="not_found")
