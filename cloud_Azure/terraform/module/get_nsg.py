import sys
from typing import Dict, List

from az.cli import az
from terraform_external_data import terraform_external_data


@terraform_external_data
def get_nsg_from_rg(query: Dict[str, str]) -> Dict[str, str]:
    """
    Gather all Network Security Groups for each requested Resource Group
    """

    if query["resource_group_names"] == "":
        return {}

    resource_group_names: List[str] = query["resource_group_names"].split(",")
    result: Dict[str, str] = {}

    for rg in resource_group_names:
        exit_code, result_dict, logs = az(
            f"network nsg list --resource-group {rg} --query '[].id' -o json"
        )
        if exit_code == 0:
            network_security_group_ids = (
                str(result_dict).strip("[]").replace("'", "").replace(" ", "")
            )
            result[rg] = network_security_group_ids
        else:
            # Terraform-Python communication protocol: on error, print message to stderr and exit with non-zero code
            print(logs, file=sys.stderr)
            exit(1)

    return result  # result is consumed by function decorator


if __name__ == "__main__":
    get_nsg_from_rg()  # pylint: disable=no-value-for-parameter
