# custom aliases/functions/one-liners/notes file

function standard_aliases {

  history_dir=$HOME/Documents/History

  # bash history management
  alias h='history'
  alias hm='history -s \#\# history_marker $HOSTNAME $( date --rfc-3339=seconds )'
  alias hgrep='history | cat $history_dir/bash_history_*.txt - | grep $@'
  alias hbackup='history -s \#\# history_marker $HOSTNAME $( date --rfc-3339=seconds ) history_backup && history -w && cp $HOME/.bash_history $history_dir/$(date +bash_history_%Y-%m-%dT%H-%M-%S.txt)'

  alias now='date +[%V]\ %A\,\ %Y-%m-%d\ %H:%M:%S'
  alias dfh='df -h -x"squashfs" -x"tmpfs" -x"udev"'
  alias t='gnome-terminal'
  alias op='xdg-open'
  alias ol='cat $HOME/.bash_aliases $HOME/.bash_company | grep -i -A1 $@ '

  # Notepad++ (wine)
  alias npp='echo; [ -f $HOME/.wine/drive_c/Local/Npp/notepad++.exe ] && pushd $HOME/share && ( wine "C:\Local\Npp\notepad++.exe" & ) && popd && echo Notepad++ started || echo Notepad++ not found '
  # LTspice (wine)
  alias lts='echo; [ -f $HOME/.wine/drive_c/Local/LTspice/XVIIx64.exe ] && pushd $HOME/share && ( wine "$HOME/.wine/drive_c/Local/LTspice/XVIIx64.exe" & ) && popd && echo LTspice started || echo LTspice not found '

  # Telegram desktop
  alias tg='telegram-desktop 2> /dev/null &'

  # Telegram web
  alias ptg='firefox --private-window https://web.telegram.org/#/login 2> /dev/null &'

  # WhatsApp web
  alias pwa='firefox --private-window https://web.whatsapp.com/ 2> /dev/null &' 

  # Gmail
  alias pgm='firefox --private-window https://www.gmail.com/ 2> /dev/null &' 

  # Telegram, WhatsApp, Gmail, and Alpha in one command, for use first thing in the morning
  alias ppp='( firefox --private-window https://web.telegram.org/#/login 2> /dev/null & ) & ( sleep 7 && firefox --private-window https://web.whatsapp.com/ 2> /dev/null & ) & ( sleep 14 && firefox --private-window https://www.gmail.com/ 2> /dev/null & ) & ( sleep 21 && firefox --private-window https://www.wolframalpha.com/ 2> /dev/null & ) &' 

  # YouTube
  alias pyt='firefox --private-window https://www.youtube.com/ 2> /dev/null &' 

  # GitHub
  alias pgh='firefox --private-window https://github.com/login 2> /dev/null &' 

  # get latest version of this aliases file
  alias get_latest_aliases='  wget --output-document=/tmp/latest_bash_aliases https://raw.githubusercontent.com/kevin137/dotfile/master/.bash_aliases && mv $HOME/.bash_aliases /tmp/bash_aliases.$( date +%Y-%m-%d-%H-%M-%S ) && mv /tmp/latest_bash_aliases $HOME/.bash_aliases '

  if [ -f ~/.bash_work ]; then
    . ~/.bash_work
  fi
}

function worldtime {
  echo -n 🌐; for tz in America/Los_Angeles America/Chicago Europe/Madrid Asia/Shanghai; do echo -n \  \|\ \ $( echo $tz | cut -d/ -f2) $( TZ=$tz date +%H:%M ); done; echo
}

function ipv4 {
  for ip in $( ip -4 addr | grep -v 127.0.0.1 | grep inet | tr -s ' ' '@' | cut -d@ -f3 ); do echo -n $ip \ \|\  ; done; echo -n \  ; hostname
}

function install_npp {
  # Download and install Notepad++
  variant=portable.x64.7z && install=$HOME/.wine/drive_c/Local/Npp && site=https://github.com && latest=$site/notepad-plus-plus/notepad-plus-plus/releases/latest && portable=$site$( wget -q -O - $latest | grep href=.*$variant\" | tr \  \\n | grep href | cut -d= -f2 | tr -d \" ) && echo PORTABLE $portable && downloaded=$( wget $portable 2>&1 | grep saved | strings | grep $variant ) && echo DOWNLOADED $downloaded && checksum=$( wget -q -O - $latest | grep $variant | grep -E '^[0-9a-f]+ +.*'$variant | cut -d\  -f1 ) && echo -e CHECKSUM\\n$checksum && sha256sum $downloaded | grep $checksum && 7z -o$install x $downloaded && rm $downloaded && wine $install/notepad++.exe $install/change.log && sed -i '/Default Style/ s/Courier New/Noto Mono/' $install/stylers.xml && grep Default\ Style $install/stylers.xml && echo Notepad++ installed, type npp to run
}

function install_ltspice {
  # Download and install LTspice
  variant=LTspiceXVII.exe && install=$HOME/.wine/drive_c/Local/LTspice && site=https://ltspice.analog.com && latest=$site/software/$variant && downloaded=$( wget $latest 2>&1 | grep saved | strings | grep $variant ) && echo DOWNLOADED $downloaded && echo install in $install && wine $downloaded && LTspice installed, type lts to run
}

if [ $# -eq 0 ]; then
  standard_aliases
else
  case $1 in
    worldtime)
      worldtime
      ;;
    ipv4)
      ipv4
      ;;
    *)
      echo $@ 
      ;;
    esac 
fi

# Notes:
#   Ubuntu hotkeys:
#     Move windows between displays : Super+Shift+Arrow 
