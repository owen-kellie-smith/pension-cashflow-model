import pandas as pd
import argparse
import os
from model import calculate_pension_cashflows


# ------------------------------------------------
# Argument parsing
# ------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Run pension model for a model point file")

    parser.add_argument("-mp", "--model_point_file", required=True,
                        help="Path to model point file (CSV)")
    parser.add_argument("-a", "--assets_folder", required=True,
                        help="Path to assets folder containing mortality files")
    parser.add_argument("-n", "--projection_years", type=int, required=True,
                        help="Number of years to project")
    parser.add_argument("-r", "--interest_rate", type=float, required=True,
                        help="Annual interest rate (e.g., 0.03 for 3pc)")
    parser.add_argument("-agg", "--aggregation_type", required=True,
                        choices=["year_record", "sum_year", "sum_record", "sum"],
                        help="Aggregation type")
    parser.add_argument("-o", "--output_file", help="Optional CSV output file")

    return parser.parse_args()



# ------------------------------------------------
# Model point file
# ------------------------------------------------
def read_model_points(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model point file not found: {path}")
    df = pd.read_csv(path)
    return df


# ------------------------------------------------
# Run model for one model point
# ------------------------------------------------
def run_model_point(row, assets_folder, projection_years, interest_rate):

    mortality_file = os.path.join(assets_folder, row["mortality"])
    if not os.path.exists(mortality_file):
        raise FileNotFoundError(f"Mortality file not found: {mortality_file}")

    df = calculate_pension_cashflows(
        mortality_file=mortality_file,
        starting_age=row["age_at_vdate"],
        base_benefit=row["benefit_pa"],
        n_years=projection_years,
        discount_rate=interest_rate
    )

    return df


# ------------------------------------------------
# Run model for all records
# ------------------------------------------------
def run_all_model_points(mp_df, args):

    results = []

    for _, row in mp_df.iterrows():
        df = run_model_point(
            row,
            args.assets_folder,
            args.projection_years,
            args.interest_rate
        )
        results.append(df)

    return results


# ------------------------------------------------
# Aggregation
# ------------------------------------------------
def aggregate_results(results, aggregation_type):

    dfs = []

    for i, df in enumerate(results):

        mask = df["year"] != "Total"   # boolean mask
        df_filtered = df[mask]         # filter rows
        df = df_filtered.copy()        # safe copy for further modification
        df["record"] = i + 1
        dfs.append(df)

    combined = pd.concat(dfs)

    agg = aggregation_type.lower()
    numeric_columns = ["benefit_pp", "cashflow", "present_value"]

    if agg == "year_record":
        return combined.set_index(["year", "record"])

    if agg == "sum_year":
        return combined.groupby("year")[numeric_columns].sum()

    if agg == "sum_record":
        return combined.groupby("record")[numeric_columns].sum()

    if agg == "sum":
        return combined.groupby(lambda _:'All')[numeric_columns].sum()

    raise ValueError("aggregation_type must be: year_record, sum_year, sum_record or sum")


# ------------------------------------------------
# Output
# ------------------------------------------------
def write_output(df, output_file):

    if output_file is None:
        return

    if os.path.exists(output_file):
        print(f"WARNING: {output_file} already exists and will be overwritten")

    df.to_csv(output_file)
    print(f"\nResults written to {output_file}")


# ------------------------------------------------
# Main
# ------------------------------------------------
def main():

    args = parse_args()

    mp_df = read_model_points(args.model_point_file)

    results = run_all_model_points(mp_df, args)

    output = aggregate_results(results, args.aggregation_type)

    print("\nAggregated Results\n")
    print(output)
    print("\nAggregated Results Columns\n")
    print(output.columns)

    write_output(output, args.output_file)


# ------------------------------------------------
# Only run if CLI calls .py directly
# ------------------------------------------------
if __name__ == "__main__":
    main()
