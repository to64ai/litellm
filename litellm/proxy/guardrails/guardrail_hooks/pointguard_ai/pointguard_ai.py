from typing import TYPE_CHECKING, Any, List, Optional
import httpx

from litellm._logging import verbose_proxy_logger
from litellm.integrations.custom_guardrail import (
    CustomGuardrail,
    log_guardrail_information,
)
from litellm.proxy._types import UserAPIKeyAuth
from litellm.types.guardrails import GuardrailEventHooks
from litellm.types.utils import CallTypesLiteral

if TYPE_CHECKING:
    from litellm.types.proxy.guardrails.guardrail_hooks.base import GuardrailConfigModel


class PointGuardAIGuardrail(CustomGuardrail):
    """PointGuard/AppSOC guardrail using X-appsoc-api-key auth."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        org_code: Optional[str] = None,
        org_unit_code: Optional[str] = None,
        policy_config_name: Optional[str] = None,
        api_path: Optional[str] = None,
        fallback_on_error: bool = False,
        **kwargs,
    ):
        self._client: Optional[httpx.AsyncClient] = None
        self.api_key = api_key
        # Default per docs: https://api.eval1.appsoc.com
        self.api_base = (api_base or "https://api.eval1.appsoc.com").rstrip("/")
        self.org_code = org_code
        self.org_unit_code = org_unit_code
        self.policy_config_name = policy_config_name
        self.fallback_on_error = fallback_on_error
        # Default path: use core API when org_unit_code provided, else auth session/validate
        if api_path:
            self.api_path = api_path
        elif org_code and org_unit_code:
            self.api_path = f"core/api/v1/orgs/{org_code}/units/{org_unit_code}/scan"
        elif org_code:
            self.api_path = f"auth/api/v1/orgs/{org_code}/session/validate"
        else:
            self.api_path = ""
        if "supported_event_hooks" not in kwargs:
            kwargs["supported_event_hooks"] = [
                GuardrailEventHooks.pre_call,
                GuardrailEventHooks.during_call,
                GuardrailEventHooks.post_call,
            ]
        super().__init__(**kwargs)

        if not self.api_key:
            raise ValueError("PointGuardAI: api_key is required")
        if not self.org_code:
            raise ValueError("PointGuardAI: org_code is required")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _build_url(self) -> str:
        return f"{self.api_base}/{self.api_path.lstrip('/')}"

    def _get_headers(self) -> dict:
        return {
            "X-appsoc-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _prepare_messages(self, messages: List[dict]) -> List[dict]:
        supported_roles = ["system", "user", "assistant"]
        default_role = "user"
        return [
            {
                "role": m.get("role", default_role)
                if m.get("role") in supported_roles
                else default_role,
                "content": m.get("content", ""),
            }
            for m in messages
        ]

    async def _call_pointguard_api(
        self,
        messages: List[dict],
        response_string: Optional[str] = None,
    ) -> dict:
        payload: dict[str, Any] = {"messages": self._prepare_messages(messages)}
        if self.policy_config_name:
            payload["policyConfigName"] = self.policy_config_name
        if response_string is not None:
            payload["response"] = response_string

        url = self._build_url()
        verbose_proxy_logger.debug("PointGuardAI request to %s: %s", url, payload)

        try:
            client = await self._get_client()
            response = await client.post(
                url,
                json=payload,
                headers=self._get_headers(),
            )
        except Exception as e:
            if self.fallback_on_error:
                verbose_proxy_logger.warning(
                    "PointGuardAI API request failed - allowing request (fallback_on_error=True). URL: %s Error: %s",
                    url,
                    e,
                )
                return {"action": "passthrough"}
            raise

        verbose_proxy_logger.debug(
            "PointGuardAI response status=%s body=%s",
            response.status_code,
            response.text[:500] if response.text else "",
        )

        if response.status_code >= 400:
            if self.fallback_on_error:
                verbose_proxy_logger.warning(
                    "PointGuardAI API error %s - allowing request (fallback_on_error=True). URL: %s",
                    response.status_code,
                    url,
                )
                return {"action": "passthrough"}
            response.raise_for_status()

        try:
            return response.json()
        except Exception:
            return {"raw": response.text}

    def _check_blocked(self, result: dict) -> None:
        action = (result.get("action") or "").lower()
        if action == "block":
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Violated PointGuardAI guardrail policy",
                    "pointguardai_response": result,
                },
            )

    @log_guardrail_information
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: Any,
        data: dict,
        call_type: CallTypesLiteral,
    ) -> Any:
        event_type = GuardrailEventHooks.pre_call
        if self.should_run_guardrail(data=data, event_type=event_type) is not True:
            return data

        messages = data.get("messages", [])
        if not messages:
            verbose_proxy_logger.warning(
                "PointGuardAI: no messages in request, skipping validation"
            )
            return data

        result = await self._call_pointguard_api(messages=messages)
        self._check_blocked(result)

        from litellm.proxy.common_utils.callback_utils import (
            add_guardrail_to_applied_guardrails_header,
        )

        add_guardrail_to_applied_guardrails_header(
            request_data=data, guardrail_name=self.guardrail_name
        )
        return data

    @log_guardrail_information
    async def async_moderation_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        call_type: CallTypesLiteral,
    ):
        event_type = GuardrailEventHooks.during_call
        if self.should_run_guardrail(data=data, event_type=event_type) is not True:
            return

        messages = data.get("messages", [])
        if not messages:
            return

        result = await self._call_pointguard_api(messages=messages)
        self._check_blocked(result)

        from litellm.proxy.common_utils.callback_utils import (
            add_guardrail_to_applied_guardrails_header,
        )

        add_guardrail_to_applied_guardrails_header(
            request_data=data, guardrail_name=self.guardrail_name
        )

    @log_guardrail_information
    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response: Any,
    ):
        event_type = GuardrailEventHooks.post_call
        if self.should_run_guardrail(data=data, event_type=event_type) is not True:
            return

        from litellm.litellm_core_utils.logging_utils import (
            convert_litellm_response_object_to_str,
        )

        response_str = convert_litellm_response_object_to_str(response)
        messages = data.get("messages", [])
        result = await self._call_pointguard_api(
            messages=messages, response_string=response_str
        )
        self._check_blocked(result)

        from litellm.proxy.common_utils.callback_utils import (
            add_guardrail_to_applied_guardrails_header,
        )

        add_guardrail_to_applied_guardrails_header(
            request_data=data, guardrail_name=self.guardrail_name
        )
