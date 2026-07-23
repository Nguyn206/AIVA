from core.exceptions import AIVAError, ProviderError, WorkflowError


def test_application_exceptions_share_common_base() -> None:
    assert issubclass(WorkflowError, AIVAError)
    assert issubclass(ProviderError, AIVAError)
