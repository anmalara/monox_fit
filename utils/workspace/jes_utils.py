# ==============================
# Helper functions regarding JES/JER uncertainties
# ==============================

import ROOT  # type: ignore


def get_jes_variations_names(year: str) -> list[str]:
    """Get the list of JES variations."""
    jes_names = [
        f"jer_{year}",
        "jesAbsolute",
        f"jesAbsolute_{year}",
        "jesBBEC1",
        f"jesBBEC1_{year}",
        "jesEC2",
        f"jesEC2_{year}",
        "jesFlavorQCD",
        "jesHF",
        f"jesHF_{year}",
        "jesRelativeBal",
        f"jesRelativeSample_{year}",
    ]

    return jes_names


def get_jes_file(category: str, source: str) -> ROOT.TFile:
    """Get the JES shape uncertainty ROOT file."""
    jes_file = ROOT.TFile(f"inputs/sys/{category}/systematics_{source}.root", "READ")
    if jes_file:
        return jes_file
    raise RuntimeError(f"No JES file found for category: {category}")
