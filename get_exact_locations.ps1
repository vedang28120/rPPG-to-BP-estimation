$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = (Resolve-Path "LuminaBP_Vocational_Training_Report.docx").Path
$doc = $word.Documents.Open($docPath)
$doc.Fields.Update()

Write-Host "=== PRELIMINARY PAGES ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    $sec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
    $secPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
    
    if ($sec -eq 2) {
        if ($text -in @("DECLARATION", "CERTIFICATE", "ACKNOWLEDGMENTS", "ABSTRACT", "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES", "ABBREVIATIONS AND NOMENCLATURE")) {
            Write-Host "PRELIM|$text|$secPg"
        }
    }
}

Write-Host "`n=== FIGURES ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    $sec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
    $secPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
    
    if ($sec -ge 3 -and $text -match "^Figure [0-9]+\.[0-9]+:") {
        $fig = $text.Substring(0, 10)
        Write-Host "FIG|$text|$secPg"
    }
}

Write-Host "`n=== TABLES ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    $sec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
    $secPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
    
    if ($sec -ge 3 -and $text -match "^Table [0-9A-Za-z]+\.[0-9]+:") {
        Write-Host "TBL|$text|$secPg"
    }
}

Write-Host "`n=== HEADINGS ==="
for ($i = 1; $i -le $doc.Paragraphs.Count; $i++) {
    $p = $doc.Paragraphs.Item($i)
    $text = $p.Range.Text.Trim()
    $sec = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndSectionNumber)
    $secPg = $p.Range.Information([Microsoft.Office.Interop.Word.WdInformation]::wdActiveEndAdjustedPageNumber)
    
    if ($sec -ge 3) {
        if ($text -match "^(CHAPTER-[0-9]+|APPENDIX-[A-Z]|REFERENCES|[0-9]+\.[0-9]+ [A-Z])" -and $text.Length -lt 85) {
            Write-Host "HEAD|$text|$secPg"
        }
    }
}

$doc.Close($false)
$word.Quit()
