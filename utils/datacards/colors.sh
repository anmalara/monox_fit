cecho() {
    local color="$1"
    shift

    case "$color" in
        red)     code='\033[0;31m' ;;
        green)   code='\033[0;32m' ;;
        yellow)  code='\033[1;33m' ;;
        blue)    code='\033[0;34m' ;;
        magenta) code='\033[0;35m' ;;
        cyan)    code='\033[0;36m' ;;
        *)       code='\033[0m' ;;  # default/no color
    esac

    echo -e "${code}$*${NC:-\033[0m}"
}