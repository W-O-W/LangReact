from typing import Any, Type, Callable, Union


class GlobalContextModifier:
    def invoke(global_context, **kwargs) -> bool:
        """modify global_context

        Args:
            context (GlobalContext): global context in EventFLow

        Returns:
            bool: is success
        """

        for k, v in kwargs.items():
            global_context.__setattr__(k, v)
        return True

    def __repr__(self) -> str:
        return self.__class__.__name__


class LocalContextModifier:
    def invoke(self, context, **kwargs) -> bool:
        """modify LocalContext

        Args:
            context (LocalContext): local context in one FlowAgent invoke

        Returns:
            bool: is success
        """
        for k, v in kwargs.items():
            # TODO check attr
            context.__setattr__(k, v)
        return True

    def __repr__(self) -> str:
        return self.__class__.__name__


def ContextModifierWrapper(name: str, T: Type = GlobalContextModifier, **kwargs):
    """wrapper of context modifier,set name of modifier

    Args:
        name (str): name of Modifier
        T (Type, optional): base class of ContextModifier. Defaults to GlobalContextModifier.

    Returns:
        GlobalContextModifier or  LocalContextModifier: a singleton of T
    """

    class ContextModifierTmp(T):
        def name(self):
            return name

        def __init__(self, func: Callable[[T, Any], bool]) -> None:
            T.__init__(self)
            self._invoke = func

        def invoke(self, context: Any) -> bool:
            return self._invoke(self, context, **kwargs)

        def __repr__(self) -> str:
            return T.__name__

    return ContextModifierTmp
