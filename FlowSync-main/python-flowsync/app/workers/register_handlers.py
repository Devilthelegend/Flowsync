"""Register all built-in handlers with the registry."""

from app.workers.handler_registry import registry
from app.workers.handlers.start_handler import StartHandler
from app.workers.handlers.end_handler import EndHandler
from app.workers.handlers.action_handler import ActionNodeHandler
from app.workers.handlers.delay_handler import DelayHandler
from app.workers.handlers.condition_handler import ConditionHandler
from app.workers.handlers.fork_handler import ForkHandler
from app.workers.handlers.join_handler import JoinHandler
from app.workers.handlers.transform_handler import TransformHandler
from app.workers.handlers.webhook_response_handler import WebhookResponseHandler


# Register all built-in handlers
registry.register(StartHandler())
registry.register(EndHandler())
registry.register(ActionNodeHandler())
registry.register(DelayHandler())
registry.register(ConditionHandler())
registry.register(ForkHandler())
registry.register(JoinHandler())
registry.register(TransformHandler())
registry.register(WebhookResponseHandler())

print(f"✅ Registered {len(registry.list_types())} worker handlers: {', '.join(registry.list_types())}")

