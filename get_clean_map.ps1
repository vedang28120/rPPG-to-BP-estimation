$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = (Resolve-Path "LuminaBP_Vocational_Training_Report.docx").Path
$doc = $word.Documents.Open($docPath)
$doc.Fields.Update()

$items = @(
    "DECLARATION", "CERTIFICATE", "ACKNOWLEDGMENTS", "ABSTRACT",
    "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES", "ABBREVIATIONS AND NOMENCLATURE",
    "CHAPTER-01", "1.1 Background and Clinical Context", "1.2 Problem Statement", "1.3 Motivation",
    "1.4 Objectives of the Project", "1.5 Scope of the Project", "1.6 Project Contributions", "1.7 Organization of the Report",
    "CHAPTER-02", "2.1 Scientific Computing Foundations in Python", "2.2 Data Preprocessing, Cleaning & Statistical Conditioning",
    "2.3 Machine Learning Taxonomy & Mathematical Core", "2.4 Deep Learning Architectures & Optimization",
    "2.5 Advanced AI Frontiers: NLP, Transformers, RAG & Agentic Systems",
    "CHAPTER-03", "3.1 Physiological Mechanisms of Blood Pressure Regulation", "3.2 Optical Foundations of Remote Photoplethysmography (rPPG)",
    "3.3 Classical and Deep Learning rPPG Extraction Algorithms", "3.4 Deep Learning for Optical Blood Pressure Estimation",
    "3.5 Comparative Analysis of Existing Studies", "3.6 Research Gaps & The Normotensive Regression Trap", "3.7 Proposed LuminaBP Solution",
    "CHAPTER-04", "4.1 System Overview & Architectural Pipeline", "4.2 Module 1: High-Stability Video Acquisition & Exposure Lock",
    "4.3 Module 2: Facial Mesh Landmarking & Dynamic Multi-ROI Tracking", "4.4 Module 3: Chrominance Projection (POS Algorithm)",
    "4.5 Module 4: Multi-Stage Signal Conditioning & Savitzky-Golay Denoising", "4.6 Module 5: Hemodynamic & Morphological Feature Engineering",
    "4.7 Module 6: Deep Sequential Architecture — MODEL-06-SepHead", "4.7 Module 6: Deep Sequential Architecture - MODEL-06-SepHead",
    "4.8 Module 7: Calibration Strategy & Signal Quality Rejection",
    "CHAPTER-05", "5.1 Computing Environment, Frameworks, and Libraries", "5.2 Hardware Specifications & Mobile Testbeds",
    "5.3 Clinical Benchmark Datasets & Cohort Curation", "5.4 Subject-Independent Split Protocol", "5.5 Model Training Protocol, Loss Formulations & Optimization",
    "5.6 Mobile Android Application Architecture (LuminaBP Mobile)",
    "CHAPTER-06", "6.1 Performance Evaluation Standards & Clinical Metrics", "6.2 Comparative Model Performance",
    "6.3 Detailed Analysis of Diastolic and Systolic Blood Pressure Estimation", "6.4 Clinical Agreement via Bland-Altman Analysis",
    "6.5 Correlation & Error Distribution Analysis", "6.6 Comprehensive Ablation Studies", "6.7 Hemodynamic Discussion & Physiological Interpretation",
    "CHAPTER-07", "7.1 Conclusion", "7.2 Limitations of the Current Study", "7.3 Future Research Directions", "7.4 Overall Summary",
    "REFERENCES", "APPENDIX-A",
    "Figure 3.1:", "Figure 4.1:", "Figure 4.2:", "Figure 4.3:", "Figure 4.4:",
    "Figure 5.1:", "Figure 6.1:", "Figure 6.2:", "Figure 6.3:", "Figure 6.4:",
    "Table 2.1:", "Table 2.2:", "Table 3.1:", "Table 4.1:", "Table 5.1:",
    "Table 5.2:", "Table 5.3:", "Table 5.4:", "Table 6.1:", "Table 6.2:",
    "Table 6.3:", "Table 6.4:", "Table A.1:"
)

# Start scanning after TOC
$seenToc = $false
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    if ($text -eq "TABLE OF CONTENTS") {
        $seenToc = $true
    }
    
    $sec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
    $secPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
    $docPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
    
    # Check preliminary pages before TOC
    if (-not $seenToc) {
        foreach ($item in @("DECLARATION", "CERTIFICATE", "ACKNOWLEDGMENTS", "ABSTRACT")) {
            if ($text.StartsWith($item)) {
                Write-Host "MAPPED|$item|$sec|$secPg|$docPg"
                break
            }
        }
    } else {
        # Check pages after TOC
        # Skip paragraphs that are within the TOC table
        if ($sec -eq 2 -and ($text -eq "LIST OF FIGURES" -or $text -eq "LIST OF TABLES" -or $text -eq "ABBREVIATIONS AND NOMENCLATURE")) {
            Write-Host "MAPPED|$text|$sec|$secPg|$docPg"
        }
        elseif ($sec -ge 3) {
            foreach ($item in $items) {
                if ($text.StartsWith($item)) {
                    Write-Host "MAPPED|$item|$sec|$secPg|$docPg"
                    break
                }
            }
        }
    }
}

$doc.Close($false)
$word.Quit()
