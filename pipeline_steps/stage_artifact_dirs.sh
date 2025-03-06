#!/bin/bash

files=($(git diff-tree --no-commit-id --name-only -r HEAD~ HEAD))
general_resources=()
management_resources=()
target="${1}"
dirname="${2}"

mkdir $dirname $dirname/general $dirname/management

for i in "${files[@]}"
do
	pbip_file=$(echo "${i%/*}" | sed "s|$target|pbip|")
	if [[ "${i%/*}" == *"$target" ]] && [[ "${i%/*}" == *"management"* ]]; then
		management_resources+=("${i%/*}" "$pbip_file")
	elif [[ "${i%/*}" == *"$target" ]] && [[ "${i%/*}" == *"general"* ]]; then
		general_resources+=("${i%/*}" "$pbip_file")
	fi
done

unique_management_resources=($(for resource in "${management_resources[@]}"; do echo "${resource}"; done | sort -u))
unique_general_resources=($(for resource in "${general_resources[@]}"; do echo "${resource}"; done | sort -u))

for resource in "${unique_management_resources[@]}"
do
	cp -r "${resource}" $dirname/management
done

for resource in "${unique_general_resources[@]}"
do
	cp -r "${resource}" $dirname/general
done
