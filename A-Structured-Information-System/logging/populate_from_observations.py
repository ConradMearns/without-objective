#!/usr/bin/env python3
"""Populate relationship matrices from observation log.

This script reads observation-log.csv and populates the three matrices
(problems-to-needs, product-planning, features-to-problems) based on
accumulated evidence rather than subjective scoring.

Approach:
- Count observations for each relationship
- Use majority vote for strength when observations conflict
- Mark cells with observation count for transparency
"""

import pandas as pd
import yaml
from pathlib import Path
from collections import defaultdict

# File paths
SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "product-planning.yaml"
OBSERVATION_LOG = SCRIPT_DIR / "observation-log.csv"
PROBLEMS_TO_NEEDS_CSV = SCRIPT_DIR / "problems-to-needs.csv"
NEEDS_TO_FEATURES_CSV = SCRIPT_DIR / "product-planning.csv"
FEATURES_TO_PROBLEMS_CSV = SCRIPT_DIR / "features-to-problems.csv"


def load_yaml():
    """Load the product planning YAML file."""
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)


def load_observations():
    """Load and parse the observation log."""
    df = pd.read_csv(OBSERVATION_LOG, comment='#')
    return df


def aggregate_observations(observations_df, yaml_data):
    """Aggregate observations by relationship and calculate consensus strength.

    Returns dict of dicts:
    {
        'problem-to-need': {
            ('problem_key', 'need_key'): {'strength': 1, 'count': 3, 'observers': [...]}
        },
        ...
    }
    """
    # Get valid keys from YAML
    problem_keys = set(yaml_data.get("problems", {}).keys())
    need_keys = set(yaml_data.get("needs", {}).keys())
    feature_keys = set(yaml_data.get("features", {}).keys())

    aggregated = {
        'problem-to-need': defaultdict(lambda: {'strengths': [], 'observers': [], 'evidence': []}),
        'need-to-feature': defaultdict(lambda: {'strengths': [], 'observers': [], 'evidence': []}),
        'feature-to-problem': defaultdict(lambda: {'strengths': [], 'observers': [], 'evidence': []})
    }

    for _, row in observations_df.iterrows():
        rel_type = row['relationship_type']
        from_item = row['from_item']
        to_item = row['to_item']
        strength = int(row['strength']) if pd.notna(row['strength']) else 0
        observer = row['observer']
        evidence = row['evidence']

        # Skip if relationship type not recognized or items don't exist in YAML
        if rel_type == 'problem-to-need':
            if from_item not in problem_keys or to_item not in need_keys:
                continue
            key = (from_item, to_item)
            aggregated[rel_type][key]['strengths'].append(strength)
            aggregated[rel_type][key]['observers'].append(observer)
            aggregated[rel_type][key]['evidence'].append(evidence)

        elif rel_type == 'need-to-feature':
            if from_item not in need_keys or to_item not in feature_keys:
                continue
            key = (from_item, to_item)
            aggregated[rel_type][key]['strengths'].append(strength)
            aggregated[rel_type][key]['observers'].append(observer)
            aggregated[rel_type][key]['evidence'].append(evidence)

        elif rel_type == 'feature-to-problem':
            if from_item not in feature_keys or to_item not in problem_keys:
                continue
            key = (from_item, to_item)
            aggregated[rel_type][key]['strengths'].append(strength)
            aggregated[rel_type][key]['observers'].append(observer)
            aggregated[rel_type][key]['evidence'].append(evidence)

        # Skip other types like 'problem-exists'

    # Calculate consensus strength (majority vote)
    for rel_type in aggregated:
        for key, data in aggregated[rel_type].items():
            strengths = data['strengths']
            if not strengths:
                continue

            # Count votes for each strength value
            strength_counts = defaultdict(int)
            for s in strengths:
                strength_counts[s] += 1

            # Use majority vote
            consensus_strength = max(strength_counts.items(), key=lambda x: x[1])[0]

            data['strength'] = consensus_strength
            data['count'] = len(strengths)
            data['conflict'] = len(set(strengths)) > 1  # True if observers disagree

    return aggregated


def format_cell_value(strength, count, show_count=True):
    """Format a cell value with optional observation count."""
    if strength == 0:
        return " ~ "
    if show_count and count > 1:
        return f" {strength}({count}) "
    return f" {strength} "


def generate_matrix_from_observations(csv_file, row_keys, col_keys, row_name, col_name, col_prefix,
                                       observations, relationship_type, yaml_data, show_counts=True):
    """Generate a matrix CSV from observations.

    Similar to generate_planning_matrix.py but populates from observation data.
    """
    # Create column codes
    col_codes = {key: f"{col_prefix}{i:02d}" for i, key in enumerate(col_keys)}
    col_code_names = list(col_codes.values())

    # Create DataFrame
    df = pd.DataFrame(index=row_keys, columns=col_code_names)

    # Populate from observations
    rel_obs = observations.get(relationship_type, {})

    for row_key in row_keys:
        for col_key in col_keys:
            col_code = col_codes[col_key]

            # Check if we have observations for this relationship
            if relationship_type == 'problem-to-need':
                obs_key = (row_key, col_key)
            elif relationship_type == 'need-to-feature':
                obs_key = (row_key, col_key)
            elif relationship_type == 'feature-to-problem':
                obs_key = (row_key, col_key)
            else:
                obs_key = None

            if obs_key and obs_key in rel_obs:
                data = rel_obs[obs_key]
                strength = data['strength']
                count = data['count']
                df.loc[row_key, col_code] = format_cell_value(strength, count, show_counts)
            else:
                df.loc[row_key, col_code] = " ~ "

    # Reset index to make row dimension a regular column
    df = df.reset_index()
    df = df.rename(columns={'index': row_name})

    # Reorder columns: col codes first, then row_name
    cols = col_code_names + [row_name]
    df = df[cols]

    # Write CSV with column mapping comments
    with open(csv_file, 'w') as f:
        # Write header comments
        f.write(f"# {col_name} Mapping:\n")
        col_data = yaml_data.get(col_name.lower() + 's', {})  # needs, features, problems
        for col_key, code in col_codes.items():
            if col_key in col_data:
                desc = col_data[col_key].get('description', col_key)
                f.write(f"# {code}: {col_key} - {desc}\n")
        f.write("#\n")
        f.write("# Values: +1 (contributes), -1 (inversely contributes), ~ (no observation)\n")
        f.write("# Format: strength or strength(count) where count is number of observations\n")
        f.write("#\n")

        # Write the DataFrame
        df.to_csv(f, index=False)

    print(f"✓ Wrote {csv_file.name} with {len(df)} rows and {len(df.columns) - 1} columns")

    # Report conflicts
    conflicts = [(k, v) for k, v in rel_obs.items() if v.get('conflict')]
    if conflicts:
        print(f"  ⚠ {len(conflicts)} relationships have conflicting observations:")
        for (from_item, to_item), data in conflicts[:5]:  # Show first 5
            strengths = data['strengths']
            print(f"    {from_item} → {to_item}: {strengths}")


def main():
    print("=" * 80)
    print("Populating Matrices from Observation Log")
    print("=" * 80)
    print()

    # Load data
    yaml_data = load_yaml()
    observations_df = load_observations()

    print(f"Loaded {len(observations_df)} observations")
    print()

    # Aggregate observations
    aggregated = aggregate_observations(observations_df, yaml_data)

    # Count observations per type
    for rel_type, data in aggregated.items():
        count = sum(1 for v in data.values() if v.get('count', 0) > 0)
        print(f"  {rel_type}: {count} unique relationships observed")
    print()

    # Get keys
    problem_keys = list(yaml_data.get("problems", {}).keys())
    need_keys = list(yaml_data.get("needs", {}).keys())
    feature_keys = list(yaml_data.get("features", {}).keys())

    # Generate matrices
    print("=" * 80)
    print("Generating Problems-to-Needs Matrix")
    print("=" * 80)
    generate_matrix_from_observations(
        csv_file=PROBLEMS_TO_NEEDS_CSV,
        row_keys=problem_keys,
        col_keys=need_keys,
        row_name="PROBLEM",
        col_name="Need",
        col_prefix="N",
        observations=aggregated,
        relationship_type='problem-to-need',
        yaml_data=yaml_data
    )
    print()

    print("=" * 80)
    print("Generating Needs-to-Features Matrix")
    print("=" * 80)
    generate_matrix_from_observations(
        csv_file=NEEDS_TO_FEATURES_CSV,
        row_keys=need_keys,
        col_keys=feature_keys,
        row_name="NEED",
        col_name="Feature",
        col_prefix="F",
        observations=aggregated,
        relationship_type='need-to-feature',
        yaml_data=yaml_data
    )
    print()

    print("=" * 80)
    print("Generating Features-to-Problems Matrix")
    print("=" * 80)
    generate_matrix_from_observations(
        csv_file=FEATURES_TO_PROBLEMS_CSV,
        row_keys=feature_keys,
        col_keys=problem_keys,
        row_name="FEATURE",
        col_name="Problem",
        col_prefix="P",
        observations=aggregated,
        relationship_type='feature-to-problem',
        yaml_data=yaml_data
    )
    print()

    print("=" * 80)
    print("✓ Matrix population complete")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review generated matrices for accuracy")
    print("  2. Add more observations to observation-log.csv")
    print("  3. Re-run this script to update matrices")
    print("  4. Run ./step.py 1 to calculate importance scores")


if __name__ == "__main__":
    main()
