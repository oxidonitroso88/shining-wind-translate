for /r "..\common" %%f in (*.txr) do (
    quickbms.exe extract_txr.bms "%%f" "output"
)
pause
