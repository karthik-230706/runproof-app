@echo off
echo.
echo Your RunProof network addresses:
echo --------------------------------
echo Local laptop: http://127.0.0.1:8000
echo.
ipconfig | findstr /i "IPv4"
echo.
echo Give your friend: http://YOUR_IPV4_ADDRESS:8000
echo Both laptops should normally be on the same Wi-Fi.
echo If it does not open, allow Python through Windows Firewall on Private networks.
echo.
pause
