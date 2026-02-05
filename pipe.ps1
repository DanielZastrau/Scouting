$filename = 'kiel' 

mkdir .\analysis
mkdir .\reports

py .\analysis.py --filename "${filename}.txt"

py .\generators\serves.py
py .\generators\receptions.py
py .\generators\sets.py
py .\generators\hitting.py
py .\generators\sets_reception1.py

py .\create_report.py --output "${filename}.pdf"

Remove-Item .\analysis -Recurse -Force -Confirm:$false
Remove-Item .\reports -Recurse -Force -Confirm:$false