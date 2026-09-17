$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = (Resolve-Path "LuminaBP_Vocational_Training_Report.docx").Path
$doc = $word.Documents.Open($docPath)
$pages = $doc.ComputeStatistics([Microsoft.Office.Interop.Word.WdStatistic]::wdStatisticPages)
Write-Host "Total Pages in Document: $pages"

# Force fields update
$doc.Fields.Update()

Write-Host "`n=== HEADINGS AND PAGE NUMBERS ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    if ($text -match "^(CHAPTER|APPENDIX|REFERENCES|DECLARATION|CERTIFICATE|ACKNOWLEDGMENTS|ABSTRACT|TABLE OF CONTENTS|LIST OF FIGURES|LIST OF TABLES|ABBREVIATIONS|Figure [0-9]|Table [0-9A-Z]|[0-9]+\.[0-9]+)" -and $text.Length -lt 110) {
        $pageNum = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndPageNumber)
        $sectionNum = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
        $pageInSec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
        Write-Host ("[Sec " + $sectionNum + "] [DocPg " + $pageNum + "] [SecPg " + $pageInSec + "] " + $text)
    }
}

$doc.Close($false)
$word.Quit()
