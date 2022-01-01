import subprocess
from pathlib import Path
from typing import Set, List


def generate_deps_set(requirements_txt_file: Path = None, package_name: str = None) -> Set[str]:
    """
    Generates a fully resolved, flat requirements list from a requirements.txt file or a package name
    :param package_name: name of a single python package you want to resolve dependencies for
    :param requirements_txt_file: a generated or a manually created requirements.txt file.
    :return: A set of recursively resolved dependencies.
    """
    if not requirements_txt_file and not package_name:
        raise ValueError("must supply either file Path or package name.")

    if requirements_txt_file:
        with open(requirements_txt_file.as_posix(), 'r') as req_file:
            file_lines = req_file.readlines()
    else:
        file_lines = [package_name]

    dependencies_set: Set[str] = set()

    for line in file_lines:
        package_name: str = line.split('==')[0]
        _add_dependencies_recursively(package_name, dependencies_set)

    return dependencies_set


def _add_dependencies_recursively(package_name: str, dependencies_set: Set[str]) -> None:
    """
    Updates passed dependencies set with all dependencies from the packages' dependency tree, recursively.

    :param package_name: packages you want to resolve dependencies for.
    :param dependencies_set: string set of dependencies. must be empty on first call.
    """
    print(f'current dependencies set: {str(dependencies_set)}')
    # remove if not used to Package Lambdas for AWS:
    if not package_name or any(native_package in package_name for native_package in ['aws-cdk', 'boto3', 'docker']):
        return
    rv = subprocess.run(['python', '-m', 'pip', 'show', package_name], capture_output=True)
    print(f'adding package {package_name}')
    dependencies_set.add(package_name)
    text_output: str = rv.stdout.decode()
    for item in text_output.split('\n'):
        if 'Requires' in item:  # if this package has sub-dependencies
            requirements_list: List[str] = item.split(":")[1].replace(" ", "").split(",")
            for requirement in requirements_list:
                if requirement in dependencies_set:  # we have already resolved dependencies for this package
                    print(f'package already added - {requirement}, skipping.')
                    continue
                _add_dependencies_recursively(requirement, dependencies_set)
            break


