#!/usr/bin/expect -f

# shellcheck disable=SC2121
set force_conservative 0  ;# set to 1 to force conservative mode even if
                          ;# script was not run conservatively originally
if {$force_conservative} {
        set send_slow {1 .1}
        proc send {ignore arg} {
                sleep .1
                exp_send -s -- $arg
        }
}

set ARCHITECTURE [lindex $argv 0]
set INSTALL_DIR [lindex $argv 1]
set DEFAULT_DIR /home/ubuntu/mambaforge

set timeout -1
spawn sh Mambaforge-$ARCHITECTURE.sh
match_max 100000

expect -exact "In order to continue the installation process, please review the license\r
agreement.\r
Please, press ENTER to continue\r
>>> "
send -- "\r"
expect -exact "Do you accept the license terms? \[yes|no\]\r
\[no\] >>> "
send -- "yes\r"
expect -exact "yes\r
\r
Mambaforge will now be installed into this location:\r
$DEFAULT_DIR\r
\r
  - Press ENTER to confirm the location\r
  - Press CTRL-C to abort the installation\r
  - Or specify a different location below\r
\r
\[$DEFAULT_DIR\] >>> "
send -- "/home/ubuntu/Library/mambaforge\r"
expect -exact "Do you wish the installer to initialize Mambaforge\r
by running conda init? \[yes|no\]\r
\[no\] >>> "
send -- "yes\r"
expect eof