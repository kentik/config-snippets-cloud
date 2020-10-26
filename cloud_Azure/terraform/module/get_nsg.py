from az.cli import az
from terraform_external_data import terraform_external_data

import sys


@terraform_external_data
def get_nsg_from_rg(query):
    """
    Functions that gest all Network Security Groups from Resource Group
    """

    exit_code, result_dict, logs = az(
        "network nsg list --resource-group " + str(sys.argv[1]) + " --query '[].id' -o json")
    if exit_code == 0:
        return {query['network_security_groups']: str(result_dict).strip("[]").replace("'", "").replace(" ", "")}
    else:
        print(logs)


if __name__ == '__main__':
    get_nsg_from_rg()
