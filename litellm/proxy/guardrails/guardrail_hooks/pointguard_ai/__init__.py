from typing import TYPE_CHECKING

from litellm.secret_managers.main import get_secret

from .pointguard_ai import PointGuardAIGuardrail

if TYPE_CHECKING:
    from litellm.types.guardrails import Guardrail, LitellmParams


def _resolve_param(val):
    """Resolve os.environ/... to actual value."""
    if val and isinstance(val, str) and val.startswith("os.environ/"):
        return str(get_secret(val) or "")
    return val


def initialize_guardrail(litellm_params: "LitellmParams", guardrail: "Guardrail"):
    import litellm

    org_code = _resolve_param(getattr(litellm_params, "org_code", None))
    org_unit_code = _resolve_param(getattr(litellm_params, "org_unit_code", None))
    policy_config_name = _resolve_param(getattr(litellm_params, "policy_config_name", None))
    api_path = getattr(litellm_params, "api_path", None)
    fallback_on_error = getattr(litellm_params, "fallback_on_error", False)

    _callback = PointGuardAIGuardrail(
        api_key=litellm_params.api_key,
        api_base=litellm_params.api_base,
        org_code=org_code,
        org_unit_code=org_unit_code,
        policy_config_name=policy_config_name,
        api_path=api_path,
        fallback_on_error=fallback_on_error,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=litellm_params.mode,
        default_on=litellm_params.default_on,
    )
    litellm.logging_callback_manager.add_litellm_callback(_callback)
    return _callback


guardrail_initializer_registry = {
    "pointguard_ai": initialize_guardrail,
}
