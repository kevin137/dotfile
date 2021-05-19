# get latest version of this alias file
alias get_latest_alias='  wget --output-document=/tmp/latest_bash_aliases https://raw.githubusercontent.com/kevin137/dotfile/master/.bash_aliases && mv $HOME/.bash_aliases /tmp/bash_aliases.$( date +%Y-%m-%d-%H-%M-%S ) && mv /tmp/latest_bash_aliases $HOME/.bash_aliases '

# quick history, history_marker with hostname, date, and time, to history
alias h='history'
alias hm='history -s \#\# history_marker hostname `date --rfc-3339=seconds`'
alias hgrep='history | grep $@'

alias now="LC_ALL=C date '+[%V] %A, %Y-%m-%d %H:%M:%S'"
alias dfh='df -h -x"squashfs" -x"tmpfs" -x"udev"'
alias t='gnome-terminal'
alias op='xdg-open'
alias ol='cat $HOME/.bash_aliases $HOME/.bash_company | grep -i -A1 $@ '

# Notepad++ (wine)
alias npp='echo; [ -f $HOME/.wine/drive_c/Local/Npp/notepad++.exe ] && pushd $HOME/share && ( wine "C:\Local\Npp\notepad++.exe" & ) && popd && echo Notepad++ started || echo Notepad++ not found '
# LTspice (wine)
alias lts='echo; [ -f $HOME/.wine/drive_c/Local/LTspice/XVIIx64.exe ] && pushd $HOME/share && ( wine "$HOME/.wine/drive_c/Local/LTspice/XVIIx64.exe" & ) && popd && echo LTspice started || echo LTspice not found '

# Telegram web
alias ptg='firefox --private-window https://web.telegram.org/#/login 2> /dev/null &'

# WhatsApp web
alias pwa='firefox --private-window https://web.whatsapp.com/ 2> /dev/null &' 

# YouTube web
alias pyt='firefox --private-window https://www.youtube.com/ 2> /dev/null &' 

if [ -f ~/.bash_company ]; then
    . ~/.bash_company
fi

return

# Download and install Notepad++
variant=portable.x64.7z && install=$HOME/.wine/drive_c/Local/Npp && site=https://github.com && latest=$site/notepad-plus-plus/notepad-plus-plus/releases/latest && portable=$site$( wget -q -O - $latest | grep href=.*$variant\" | tr \  \\n | grep href | cut -d= -f2 | tr -d \" ) && echo PORTABLE $portable && downloaded=$( wget $portable 2>&1 | grep saved | strings | grep $variant ) && echo DOWNLOADED $downloaded && checksum=$( wget -q -O - $latest | grep $variant | grep -E '^[0-9a-f]+ +.*'$variant | cut -d\  -f1 ) && echo -e CHECKSUM\\n$checksum && sha256sum $downloaded | grep $checksum && 7z -o$install x $downloaded && rm $downloaded && wine $install/notepad++.exe $install/change.log && sed -i '/Default Style/ s/Courier New/Noto Mono/' $install/stylers.xml && grep Default\ Style $install/stylers.xml && echo Notepad++ installed, type npp to run

# Download and install LTspice
variant=LTspiceXVII.exe && install=$HOME/.wine/drive_c/Local/LTspice && site=https://ltspice.analog.com && latest=$site/software/$variant && downloaded=$( wget $latest 2>&1 | grep saved | strings | grep $variant ) && echo DOWNLOADED $downloaded && echo install in $install && wine $downloaded && LTspice installed, type lts to run
