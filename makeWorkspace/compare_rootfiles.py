import ROOT  # type: ignore


def compare_histograms(hist1, hist2):
    """Compare two histograms bin by bin."""
    if hist1.GetNbinsX() != hist2.GetNbinsX():
        return False

    for bin_idx in range(1, hist1.GetNbinsX() + 1):
        if hist1.GetBinContent(bin_idx) != hist2.GetBinContent(bin_idx):
            return False

    return True


def compare_tdirectory(file1_path, file2_path, dir_name):
    """Compare histograms inside a TDirectoryFile from two ROOT files."""
    file1 = ROOT.TFile.Open(file1_path)
    file2 = ROOT.TFile.Open(file2_path)

    no_issues = True

    if not file1 or not file2:
        print("Error: One of the ROOT files could not be opened.")
        no_issues = False

    dir1 = file1.Get(dir_name)
    dir2 = file2.Get(dir_name)

    if not dir1 or not dir2:
        print(f"Error: TDirectoryFile '{dir_name}' not found in one of the files.")
        no_issues = False

    keys1 = set([key.GetName() for key in dir1.GetListOfKeys()])
    keys2 = set([key.GetName() for key in dir2.GetListOfKeys()])

    if keys1 != keys2:
        print("Mismatch in histogram names:")
        print("Only in file1:", keys1 - keys2)
        print("Only in file2:", keys2 - keys1)
        no_issues = False

    for hist_name in keys1:
        hist1 = dir1.Get(hist_name)
        hist2 = dir2.Get(hist_name)

        if not hist1 or not hist2:
            print(f"Error: Could not retrieve histogram '{hist_name}' in one of the files.")
            no_issues = False

        if not compare_histograms(hist1, hist2):
            print(f"Mismatch found in histogram: {hist_name}")
            no_issues = False

    if no_issues:
        print("The two TDirectoryFiles contain identical histograms.")
    return no_issues


file1 = "../vbf/Run3_22_23/250331_oldcr/root/combined_model_vbf.root"
file2 = "../vbf/Run3_22_23/250331_newcr/root/combined_model_vbf.root"
directory_name = "Z_constraints_qcd_withphoton_category_vbf_2018"

compare_tdirectory(file1, file2, directory_name)
