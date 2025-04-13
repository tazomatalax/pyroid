### To Run in Linux

I had a few problems moving from VScode to WSL to run. I ended up having to install a few extra libraries and use X-server for a the GUI.
```
sudo apt-get install libgl1-mesa-glx libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0
```
Install an X Server on Windows:
You need an X-Windows compatible server. A popular open-source option is VcXsrv. You can install it using Chocolatey:
```
choco install vcxsrv
```
After installation, run it using the XLaunch command available in the Windows Start menu.

Configure WSL to Use the X Server:
Set the DISPLAY environment variable in your WSL terminal:
```
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
```
#### Troubleshooting
If you encounter any issues, ensure that the X server is running and the DISPLAY environment variable is set correctly. You can also try setting the QT_QPA_PLATFORM environment variable:
```
export QT_QPA_PLATFORM=xcb
```
For further assistance, feel free to open an issue on the GitHub repository.
