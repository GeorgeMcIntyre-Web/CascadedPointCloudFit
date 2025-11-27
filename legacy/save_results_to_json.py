from create_report_name import create_report_name


import json


def save_results_to_json(source_file, target_file, initial_transform, refined_transform, initial_metrics, refined_metrics):
    report_name = create_report_name(source_file, target_file)
    results = {
        "source_file": source_file,
        "target_file": target_file,
        "initial_transform": initial_transform.tolist(),  # Convert ndarray to list
        "refined_transform": refined_transform.tolist(),  # Convert ndarray to list
        "initial_metrics": initial_metrics,
        "refined_metrics": refined_metrics
    }

    with open(report_name, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {report_name}")
    return report_name