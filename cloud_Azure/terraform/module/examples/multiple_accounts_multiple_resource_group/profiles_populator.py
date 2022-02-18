import argparse
import configparser
from dataclasses import dataclass
import logging
import os
import shutil
import sys
from datetime import datetime
from itertools import islice
from pathlib import Path
from typing import Any, List, Optional

from azure_cli import az_cli

from profiles import AzureProfile, load_profiles


# redirect logs to file so they don't mess up user-program interaction
log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", filename="populator.log", level=logging.INFO
)

EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit code for failed command

BACKUP_PROFILES_DIRECTORY = "backup_profiles"
DEFAULT_PROFILES_FILE_NAME: str = "profiles_populator.ini"

AZURE_GRAPH_API = "00000003-0000-0000-c000-000000000000"
AZURE_READ_WRITE_ALL_PERMISSION = "1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9=Role"

SP_NAME: str = "KentikTerraformOnboarder"  # service principal to be created


@dataclass
class AzureAccountLoginInfo:
    subscription_id: str
    tenant_id: str


@dataclass
class ServicePrincipal:
    id: str
    secret: str


def add_new_profile(profiles_file_path: str) -> bool:
    """
    Create new profile and add it to specified file
    All interactions with user happen here and in cli_* functions
    """

    # Request name for the new profile
    profile_name = cli_ask_profile_name()

    # Load profiles from file and handle possible profile name collision
    profiles = try_load_profiles(profiles_file_path)
    if profiles is None:
        print_log(f"Failed to read profiles file '{profiles_file_path}'", file=sys.stderr, level=logging.ERROR)
        return False
    if profile_exists(profile_name, profiles) and cli_ask_overwrite_profile(profile_name) is False:
        print_log("Overwrite declined")
        return True  # it's ok to change mind

    # Login to Azure acccount
    cli_ask("Please login to target Azure account as a privileged user [ENTER]")
    account = azure_login_interactively()
    if account is None:
        print_log("Failed to login into Azure account", file=sys.stderr, level=logging.ERROR)
        return False

    # Get or create Service Principal
    principal = get_service_principal(SP_NAME, profiles) or setup_service_principal(account.subscription_id, SP_NAME)
    if principal is None:
        print_log("Failed to get as well as to create Service Principal", file=sys.stderr, level=logging.ERROR)
        return False

    # Request Azure location and list Resource Groups in that location
    location = cli_ask_azure_location()
    resource_group_names = list_resource_groups(location)

    # Update profile list with a new item
    profile = AzureProfile(
        name=profile_name,
        subscription_id=account.subscription_id,
        tenant_id=account.tenant_id,
        principal_id=principal.id,
        principal_secret=principal.secret,
        location=location,
        resource_group_names=resource_group_names,
        storage_account_names=[],
    )
    insert_or_overwrite_profile(profiles, profile)

    # Create backup and update profiles file
    if not backup_file(profiles_file_path):
        print_log("Failed to create profiles backup", file=sys.stderr, level=logging.WARNING)

    if not save_profiles(profiles_file_path, profiles):
        print_log(f"Failed to save profile to '{profiles_file_path}'", file=sys.stderr, level=logging.ERROR)
        return False

    print_log("Success")
    return True


def cli_ask_profile_name() -> str:
    while True:
        name = cli_ask("Enter name for a new profile: ")
        if name != "" and " " not in name and "\t" not in name:
            return name
        print_log(f"Invalid profile name '{name}'. Name should not contain white space characters")


def cli_ask_overwrite_profile(profile_name: str) -> bool:
    answer = cli_ask(f"Profile '{profile_name}' already exists. Overwrite? [y/n]: ")
    return answer.lower() in ["true", "y", "yes"]


def cli_ask_azure_location() -> str:
    NUM_COLUMNS = 5
    locations = list_locations()
    print_log("Select Azure Location. Available locations: ")
    print_log_in_columns(locations, NUM_COLUMNS)
    while True:
        location = cli_ask("Select location: ")
        if location in locations or locations == []:
            break
        cli_ask(f"Invalid location '{location}'. Please try again [ENTER]")

    return location


def cli_ask(prompt: str) -> str:
    """Ask user for information and return the answer"""

    print(prompt, end="", flush=True)
    answer = sys.stdin.readline().strip()
    log.info(prompt + answer)
    return answer


def try_load_profiles(file_path: str) -> Optional[List[AzureProfile]]:
    """
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    Return None on file reading error/parsing error
    """

    if not os.path.exists(file_path):
        log.info("File '%s' doesn't exist. Returning empty profile list", file_path)
        return []

    try:
        return load_profiles(file_path)
    except RuntimeError as err:
        log.exception(err)
        return None


def azure_login_interactively() -> Optional[AzureAccountLoginInfo]:
    """
    Return login information on login success
    Return None on login error
    """

    COMMAND = "login --query '[0]'"  # returns a dict
    output_dict = az_cli(COMMAND)
    if not isinstance(output_dict, dict):
        return None

    try:
        subscription_id, tenant_id = output_dict["id"], output_dict["tenantId"]
        log.info("Logged into Azure account with subscription_id '%s', tenant_id '%s'", subscription_id, tenant_id)
        return AzureAccountLoginInfo(subscription_id=subscription_id, tenant_id=tenant_id)
    except KeyError:
        log.exception("Failed to retrieve Azure account subscription_id and tenant_id")
        return None


def azure_logout() -> None:
    az_cli("logout")


def setup_service_principal(subscription_id: str, name: str) -> Optional[ServicePrincipal]:
    """
    Return ServicePrincipal on success
    Return None on error
    """

    principal = new_service_principal(subscription_id, name)
    if principal is None:
        log.error("Failed to create Service Principal '%s' in Subscription '%s'", name, subscription_id)
        return None

    if not add_read_write_all_permissions(principal.id):
        log.error("Failed to add permissions for Service Principal '%s' in Subscription '%s'", name, subscription_id)
        return None

    if not grant_permissions(principal.id):
        log.error("Failed to grant permissions for Service Principal '%s' in Subscription '%s'", name, subscription_id)
        return None

    if not consent_permissions(principal.id):
        log.error(
            "Failed to consent permissions for Service Principal '%s' in Subscription '%s'", name, subscription_id
        )
        return None

    log.info("Configured Service Principal '%s' with ID '%s' in Subscription '%s'", name, principal.id, subscription_id)
    return principal


def list_locations() -> List[str]:
    """
    Return currently available Azure locations on success
    Return empty list on error
    """

    COMMAND = "account list-locations --query '[].name'"  # returns a list
    output_list = az_cli(COMMAND)
    if not isinstance(output_list, list):
        log.error("Failed to list Azure Locations")
        return []

    log.info("Retrieved %d Azure Locations", len(output_list))
    return sorted(output_list)


def list_resource_groups(location: str) -> List[str]:
    """
    Return Resource Groups available in "location" on success
    Return empty list on error
    """

    COMMAND = f'''group list --query "[?location=='{location}'].name"'''  # returns a list
    output_list = az_cli(COMMAND)
    if not isinstance(output_list, list):
        log.error("Failed to list Resource Groups in location '%s'", location)
        return []

    log.info("Found %d Resource Group(s) in location '%s'", len(output_list), location)
    return output_list


def get_service_principal(name: str, profiles: List[AzureProfile]) -> Optional[ServicePrincipal]:
    principal_id = find_service_principal(name)
    if not principal_id:
        return None
    principal_secret = find_secret(principal_id, profiles)
    return ServicePrincipal(id=principal_id, secret=principal_secret or "")


def find_service_principal(name: str) -> Optional[str]:
    """
    Return principal_id on success
    Return empty string if principal not found
    Return None on lookup error
    """

    COMMAND = f"""ad app list --query "[?displayName == '{name}'].appId" """  # returns a list
    output_list = az_cli(COMMAND)
    if not isinstance(output_list, list):
        log.error("Failed to lookup Service Principal '%s'", name)
        return None
    if output_list == []:
        log.info("Service Principal '%s' not found", name)
        return ""

    principal_id = output_list[0]
    log.info("Service Principal '%s' found with ID '%s'", name, principal_id)
    return principal_id


def new_service_principal(subscription_id: str, name: str) -> Optional[ServicePrincipal]:
    """
    Return ServicePrincipal on success
    Return None on error
    """

    COMMAND = f"""ad sp create-for-rbac --role="Owner" --scopes="/subscriptions/{subscription_id}" --name {name}"""  # returns a dict
    output_dict = az_cli(COMMAND)
    if not isinstance(output_dict, dict):
        log.error("Failed to create Service Principal '%s' in Subscription '%s'", name, subscription_id)
        return None

    try:
        return ServicePrincipal(id=output_dict["appId"], secret=output_dict["password"])
    except KeyError:
        log.exception("Error parsing returned Service Principal")
        return None


def add_read_write_all_permissions(principal_id: str) -> bool:
    COMMAND = f"ad app permission add --id {principal_id} --api-permissions {AZURE_READ_WRITE_ALL_PERMISSION} --api {AZURE_GRAPH_API}"  # returns a dict
    ATTEMPT_COUNT = 5
    output_dict = az_cli(COMMAND, ATTEMPT_COUNT)
    if not isinstance(output_dict, dict):
        log.error("Failed to give read-write-all permissions to Service Principal")
        return False
    return True


def grant_permissions(principal_id: str) -> bool:
    COMMAND_GRANT = f"ad app permission grant --id {principal_id} --api {AZURE_GRAPH_API}"  # returns a dict
    ATTEMPT_COUNT = 5
    output_dict = az_cli(COMMAND_GRANT, ATTEMPT_COUNT)
    if not isinstance(output_dict, dict):
        log.error("Failed to grant permissions to Service Principal")
        return False
    return True


def consent_permissions(principal_id: str) -> bool:
    COMMAND = f"ad app permission admin-consent --id {principal_id}"  # returns a dict
    ATTEMPT_COUNT = 5
    output_dict = az_cli(COMMAND, ATTEMPT_COUNT)
    if not isinstance(output_dict, dict):
        log.error("Failed to consent permissions to Service Principal")
        return False
    return True


def save_profiles(file_path: str, profiles: List[AzureProfile]) -> bool:
    config = configparser.ConfigParser()
    for profile in profiles:
        section = profile.name
        config.add_section(section)
        config[section]["subscription_id"] = profile.subscription_id
        config[section]["tenant_id"] = profile.tenant_id
        config[section]["principal_id"] = profile.principal_id
        config[section]["principal_secret"] = profile.principal_secret
        config[section]["location"] = profile.location
        config[section]["resource_group_names"] = ",".join(profile.resource_group_names)
        config[section]["storage_account_names"] = ""

    try:
        with open(file_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)
        log.info("Saved profiles to '%s'", file_path)
        return True
    except OSError:
        log.exception("Failed to save profiles to '%s'", file_path)
        return False


def profile_exists(profile_name: str, profiles: List[AzureProfile]) -> bool:
    return find_profile(profile_name, profiles) is not None


def find_profile(profile_name: str, profiles: List[AzureProfile]) -> Optional[int]:
    for i, profile in enumerate(profiles):
        if profile.name == profile_name:
            return i
    return None


def find_secret(principal_id: str, profiles: List[AzureProfile]) -> Optional[str]:
    for profile in profiles:
        if profile.principal_id == principal_id and likely_valid_service_principal_secret(profile.principal_secret):
            log.info("Secret for Service Principal ID '%s' found in profile '%s'", principal_id, profile.name)
            return profile.principal_secret
    log.info("Secret for Service Principal ID '%s' not found", principal_id)
    return None


def likely_valid_service_principal_secret(secret: str) -> bool:
    SERVICE_PRINCIPAL_SECRET_LENGTH = 34
    return len(secret) == SERVICE_PRINCIPAL_SECRET_LENGTH


def insert_or_overwrite_profile(profiles: List[AzureProfile], profile: AzureProfile) -> None:
    index = find_profile(profile.name, profiles)
    if index is not None:
        profiles[index] = profile
    else:
        profiles.append(profile)


def backup_file(file_path: str) -> bool:
    """Create file backup with time stamp suffix in the name"""

    if not os.path.exists(file_path):
        log.info("Source file '%s' doesn't exist. Skipping backup", file_path)
        return True  # nothing to backup -> OK

    backup_time = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
    backup_name = f"{file_path}.{backup_time}"
    backup_dir = Path(BACKUP_PROFILES_DIRECTORY)
    backup_path = backup_dir.joinpath(backup_name)
    try:
        backup_dir.mkdir(exist_ok=True)
        shutil.copyfile(file_path, backup_path)
    except OSError:
        log.exception("Failed to create backup '%s' of '%s'", backup_path, file_path)
        return False

    log.info("Created backup '%s' of '%s", backup_path, file_path)
    return True


def print_log_in_columns(items: List[Any], num_columns: int) -> None:
    it = iter(items)
    groups = iter(lambda: tuple(islice(it, num_columns)), ())

    format_str = "{: <20} " * num_columns
    for row in groups:
        print_log(format_str.format(*row))


def parse_cmd_line() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=DEFAULT_PROFILES_FILE_NAME, help="Profiles file name")
    args = parser.parse_args()
    return args.filename


def print_log(msg: str = "", level: int = logging.INFO, file=sys.stdout) -> None:
    print(msg, file=file)
    log.log(level=level, msg=msg)


if __name__ == "__main__":
    profiles_file_name = parse_cmd_line()
    execution_successful = add_new_profile(profiles_file_name)
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
