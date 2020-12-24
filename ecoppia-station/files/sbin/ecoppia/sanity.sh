#!/usr/bin/env ash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

error() {
    printf "\n${RED}ERROR: ${1}${NC}\n"
    exit 1
}

info() {
    printf "${GREEN}${1}${NC}\n"
}

ok() {
    printf "\n${BLUE}OK: ${1}${NC}\n"
}

runtest() {
	# python installed?
	python --version > /dev/null 2>&1 && ok "python installed... :-)" || error "!!! python not found !!!"
	# libmraa installed?
	opkg list libmraa | grep -q mraa && ok "libmraa installed... :-)" || error "!!! libmraa not found !!!"
	# mraa installed?
	python -c "import mraa" && ok "python mraa package installed... :-)" || error "!!! mraa python package not found!!!"
	# has watchdog service?
	[ -f /etc/init.d/rfnwatchdogd ] && ok "watchdog service installed... :-)" || error "!!! RFN watchdog service not installed !!!"
	# has watchdog?
	which /usr/bin/rfnwatchdog > /dev/null && ok "watchdog installed... :-)" || error "!!! RFN watchdog not found !!!"
	# has crontab?
	[[ "$(crontab -l)" == "*/1 * * * * /usr/bin/rtr_clnt_wd" ]] && ok "crontab set correctly... :-)" || error "!!! crontab not set !!!" ||
	# has ecoppia watchdog?
	which /usr/bin/rtr_clnt_wd && ok "ecoppia watchdog installed... :-)" || error "!!! ecoppia watchdog not found !!!"
}

print_info() {
	info ""
	info "oprnWRT version `cat /etc/*release* | grep -i version_id`"
	info "libmraa version `opkg list libmraa`"
	info "libmraa-python version `opkg list libmraa-python`"
	mraa_ver=`python -c "import mraa; print(mraa.getVersion())"`
	info "mraa version ${mraa_ver}"
	info ""
}

test_reset() {
    cd /sbin/ecoppia
	python ecoppia1/ecoppia/lib/stand_alone_hard_reset.py
}

info "============================="
info "===   station sanity test ==="
info "===   ver 1.0             ==="
info "===   ./sanity.sh         ==="
info "============================="

runtest
print_info

info "============================="
info "===   OK   ALL   PASSED  ===="
info "============================="
info ""

if read -p "Station reset test - this will reboot the station. Continue? (y/n): " confirm && [ ${confirm} == "y" ] ; then
	test_reset && ok "station should reboot now" || error "!!! reset test failed !!!"
else info "exiting without reset test... bye"
fi
