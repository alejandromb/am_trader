# am_trader

# ro tun on raspberry on boot

cd /lib/systemd/system/
sudo nano trader.service

#copy this 

[Unit]
Description=Trader Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/running_script.py
Restart=on-abort

[Install]
WantedBy=multi-user.target




# change permission to be executable

sudo chmod 644 /lib/systemd/system/trader.service
chmod +x /home/pi/Documents/running_script.py
sudo systemctl daemon-reload
sudo systemctl enable trader.service
sudo systemctl start trader.service
