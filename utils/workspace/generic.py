import ROOT  # type: ignore
from typing import Any


def safe_import(workspace: ROOT.RooWorkspace, obj: Any, debug: bool = False) -> None:
    """
    Import an object into a RooWorkspace while suppressing RooFit INFO messages.

    Args:
        workspace (ROOT.RooWorkspace): The target workspace.
        obj (Any): The object to import (e.g., RooDataHist, RooAbsPdf, etc.).
    """
    if not debug:
        msg_service = ROOT.RooMsgService.instance()
        previous_level = msg_service.globalKillBelow()
        msg_service.setGlobalKillBelow(ROOT.RooFit.WARNING)
    ignore_conflicts = isinstance(obj, ROOT.RooDataHist)
    if not ignore_conflicts:
        workspace._import(obj, ROOT.RooFit.RecycleConflictNodes())
    else:
        workspace._import(obj)
    if not debug:
        msg_service.setGlobalKillBelow(previous_level)
