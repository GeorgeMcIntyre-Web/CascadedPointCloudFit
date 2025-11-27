import os


def create_report_name(source_file, target_file):
    # Extract the directory and the base name without extension
    directory = os.path.dirname(source_file)
    source_name = os.path.splitext(os.path.basename(source_file))[0]
    target_name = os.path.splitext(os.path.basename(target_file))[0]
    # Construct a new filename for the report
    return os.path.join(directory, f"{source_name}_{target_name}_combined_report.json")