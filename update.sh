# !/bin/bash
source /etc/profile.d/clash.sh
proxy_on
cd /home/hxy/myblog
git stash
git pull origin main
hugo