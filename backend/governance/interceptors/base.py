from abc import ABC, abstractmethod
from governance.context import GovernanceContext


class BaseInterceptor(ABC):

    @abstractmethod
    def process(self, ctx: GovernanceContext) -> GovernanceContext:
        raise NotImplementedError