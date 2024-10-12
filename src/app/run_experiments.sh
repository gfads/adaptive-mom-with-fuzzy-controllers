#!/bin/bash

controllers=(
    "fuzzy1 fuzzy1_trimf_cod_fixed_exp2 centroid"
    "fuzzy1 fuzzy2_trimf_mom_fixed_exp2 mom"
    "fuzzy2 fuzzy3_gaussmf_cod_fixed_exp2 centroid"
    "fuzzy2 fuzzy4_gaussmf_mom_fixed_exp2 mom"
    "fuzzy3 fuzzy5_gaussmfextra_cod_fixed_exp2 centroid"
    "fuzzy3 fuzzy6_gaussmfextra_mom_fixed_exp2 mom"
    "fuzzy4 fuzzy7_gbellmf_cod_fixed_exp2 centroid"
    "fuzzy4 fuzzy8_gbellmf_mom_fixed_exp2 mom"
    "fuzzy5 fuzzy9_pimf_cod_fixed_exp2 centroid"
    "fuzzy5 fuzzy10_pimf_mom_fixed_exp2 mom"
    "fuzzy6 fuzzy11_sigmoidmf_cod_fixed_exp2 centroid"
)

for args in "${controllers[@]}"; do
    python3 subscriber.py $args

    if [ $? -eq 0 ]; then
        echo "${args%% *} completed successfully."
    else
        echo "${args%% *} failed with exit code $?."
        exit 1
    fi

    echo "Sleeping for 10 seconds before the next iteration"
    sleep 10
done
        