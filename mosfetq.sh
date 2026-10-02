while true; do
    read -p "MOSFETQ-DOS> " cmd
    upper_cmd=$(echo "$cmd" | tr '[:lower:]' '[:upper:]')
    case "$upper_cmd" in
        "DIR")
            ls -la
            ;;
        "EXIT")
            echo "Exiting MOSFETQ-DOS..."
            break
            ;;
        PYTHON|PYTHON3)
            python3
            ;;
        *)
            if [[ "$cmd" == *.py ]]; then
                python3 "$cmd"
            else
                eval "$cmd"
            fi
            ;;
    esac
done
