import argparse
import logging
import math
import os
import shutil
import signal
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, List, Optional, Tuple

from texttable import Texttable

from azure_cli import az_cli
from profiles import (
    AzureProfile,
    likely_valid_service_principal_secret,
    list_missing_required_fields,
    load_incomplete_profiles,
    save_profiles,
)

log = logging.getLogger(__name__)


EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit code for failed command

BACKUP_PROFILES_DIRECTORY = "backup_profiles"
DEFAULT_PROFILES_FILE_NAME: str = "profiles_populator.ini"

AZURE_GRAPH_API = "00000003-0000-0000-c000-000000000000"
AZURE_READ_WRITE_ALL_PERMISSION = "1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9=Role"

SERVICE_PRINCIPAL_NAME: str = "KentikTerraformOnboarder"  # service principal to be created


@dataclass
class AzureAccountLoginInfo:
    subscription_id: str
    tenant_id: str


@dataclass
class ServicePrincipal:
    id: str
    secret: str


def add_new_profiles(file_path: str, names: Iterable[str]) -> bool:
    """
    Add new profiles for all provided names, in interactive manner
    User can break the process at any point by sending keyboard interrupt
    """

    signal.signal(signal.SIGINT, signal.default_int_handler)  # type: ignore # https://github.com/python/mypy/issues/2955

    profiles = try_load_profiles(file_path, load_incomplete_profiles)
    if profiles is None:
        return False

    cli_tell("[CTRL + C] to finish")
    all_successful = True
    try:
        for name in names:
            all_successful = all_successful and add_profile(name, profiles)
            cli_tell()
    except KeyboardInterrupt:
        log.info("Operation interrupted")
        cli_tell()

    if not backup_file(file_path):
        log.warning("Failed to create profiles backup")

    if not save_profiles(file_path, profiles):
        return False

    cli_tell("Finished adding profiles")
    return all_successful


def add_profile(profile_name: str, profiles: List[AzureProfile]) -> bool:
    """
    Create new profile and add it to the list
    All interactions with user happen here and in cli_* functions
    """

    cli_tell(f"Profile name: {profile_name}")

    # handle possible profile name collision
    if profile_exists(profile_name, profiles) and cli_ask_overwrite_profile(profile_name) is False:
        return True  # it's ok to change mind

    # login to Azure account
    account = cli_azure_login_interactively()
    if account is None:
        return False

    # find existing or create new Service Principal
    principal = cli_get_or_create_service_principal(profiles, account.subscription_id)
    if principal is None:
        return False

    # request Azure location and list Resource Groups in that location
    location = cli_ask_azure_location()
    resource_group_names = cli_list_resource_groups(location)

    # update profile list with a new item
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

    cli_tell(f"Profile '{profile_name}' ready")
    return True


def complete_existing_profiles(file_path: str) -> bool:
    """
    Complete missing information in profiles loaded from provided file_path
    User can break the process at any point by sending keyboard interrupt
    """

    signal.signal(signal.SIGINT, signal.default_int_handler)  # type: ignore # https://github.com/python/mypy/issues/2955

    profiles = try_load_profiles(file_path, load_incomplete_profiles)
    if profiles is None:
        return False

    if profiles == []:
        cli_tell(f"No profiles were loaded from '{file_path}'")
        return True

    cli_tell("[CTRL + C] to finish")
    all_successful = True
    try:
        for profile in profiles:
            all_successful = all_successful and complete_profile(profile, profiles)
    except KeyboardInterrupt:
        log.info("Operation interrupted")
        cli_tell()

    if not backup_file(file_path):
        log.warning("Failed to create profiles backup")

    if not save_profiles(file_path, profiles):
        return False

    cli_tell("Finished completing profiles")
    return all_successful


def complete_profile(profile: AzureProfile, profiles: List[AzureProfile]) -> bool:
    """
    Complete the profile if any information is missing
    All interactions with user happen here and in cli_* functions
    """

    cli_tell(f"Profile name: {profile.name}")

    # check if anything is missing at all
    missing_fields = list_missing_required_fields(profile)
    if not missing_fields:
        cli_tell("Profile is complete")
        return True

    missing_fields_str = ", ".join(missing_fields)
    cli_tell(f"The profile is missing following fields: {missing_fields_str}")
    # avoid logging into Azure if only principal_secret is missing - it can't be retrieved from the account anyway
    if missing_fields == ["principal_secret"]:
        profile.principal_secret = find_secret(profile.principal_id, profiles) or cli_ask_secret()
        cli_tell(f"Profile '{profile.name}' information completed: {missing_fields_str}")
        return True

    # filling any information other than just principal_secret requires logging into Azure Account
    account = cli_azure_login_interactively(profile.subscription_id, profile.tenant_id)
    if account is None:
        return False

    # fill account information
    profile.subscription_id = account.subscription_id
    profile.tenant_id = account.tenant_id

    # fill service principal information
    if profile.principal_id == "":
        principal = cli_get_or_create_service_principal(profiles, account.subscription_id)
        if principal is None:
            return False
        profile.principal_id = principal.id
        profile.principal_secret = principal.secret
    elif profile.principal_secret == "":
        profile.principal_secret = find_secret(profile.principal_id, profiles) or cli_ask_secret()

    # fill azure location information
    if profile.location == "":
        profile.location = cli_ask_azure_location()

    # fill resource groups information
    if not profile.resource_group_names:
        profile.resource_group_names = cli_list_resource_groups(profile.location)

    cli_tell(f"Profile '{profile.name}' information completed: {missing_fields_str}")
    return True


def cli_get_or_create_service_principal(
    profiles: List[AzureProfile], subscription_id: str
) -> Optional[ServicePrincipal]:
    principal = get_service_principal(SERVICE_PRINCIPAL_NAME, profiles)
    if principal is None:
        principal = setup_service_principal(subscription_id, SERVICE_PRINCIPAL_NAME)
    if principal is None:
        log.error("Failed to get as well as to create Service Principal in subscription '%s'", subscription_id)
        return None
    if principal.secret == "":
        principal.secret = cli_ask_secret()
    return principal


def cli_ask_profile_name() -> str:
    while True:
        name = cli_ask("Enter name for a new profile: ")
        if name != "" and " " not in name and "\t" not in name:
            return name

        cli_tell("Name must not contain white space characters")


def cli_ask_overwrite_profile(profile_name: str) -> bool:
    answer = cli_ask(f"Profile '{profile_name}' already exists. Overwrite? [y/n]: ")
    return answer.lower() == "y"


def cli_ask_azure_location() -> str:
    NUM_COLUMNS_FOR_LOCATIONS_PRINTOUT = 3
    locations = list_locations()
    num_locations = len(locations)
    if num_locations == 0:
        log.warning("No locations are available; skipping location selection")
        return ""

    cli_tell("Select Azure Location. Available locations: ")
    cli_tell(format_columns(locations, NUM_COLUMNS_FOR_LOCATIONS_PRINTOUT))
    selected_index = cli_ask_number_in_range(num_locations)
    return locations[selected_index]


def cli_ask_number_in_range(numbers_range: int) -> int:
    while True:
        s = cli_ask(f"Enter number in range [{0} - {numbers_range-1}]: ")
        if not s.isdigit():
            cli_tell("Invalid number")
            continue
        number = int(s)
        if number not in range(numbers_range):
            cli_tell("Number out of range")
            continue
        return number


def cli_ask_secret() -> str:
    while True:
        s = cli_ask("Enter Service Principal secret (34 letters) [empty to skip]: ")
        if likely_valid_service_principal_secret(s):
            return s
        if s == "":
            return ""
        cli_tell("Invalid format")


def cli_azure_login_interactively(subscription_id="", tenant_id: str = "") -> Optional[AzureAccountLoginInfo]:
    """
    Login to Azure Account
    Target account subscription and tenant must match subscription_id and tenant_id (if provided)
    """

    if subscription_id and tenant_id:
        prompt = f". Target Subscription ID: {subscription_id}, Tenant ID: {tenant_id} [ENTER]"
    elif subscription_id:
        prompt = f". Target Subscription ID: {subscription_id} [ENTER]"
    elif tenant_id:
        prompt = f". Target Tenant ID: {tenant_id} [ENTER]"
    else:
        prompt = " [ENTER]"

    while True:
        cli_ask(f"Please login to Azure Account{prompt}")
        account = azure_login_interactively()
        if account is None:
            log.error("Failed to login into Azure account")
            return None

        if subscription_id and subscription_id != account.subscription_id:
            cli_tell(
                f"Selected Azure Account has different Subscription ID than specified. Expected: {subscription_id}, got: {account.subscription_id}"
            )
            continue

        if tenant_id and tenant_id != account.tenant_id:
            cli_tell(
                f"Selected Azure Account has different Tenant ID than specified. Expected: {tenant_id}, got: {account.tenant_id}"
            )
            continue

        return account


def cli_list_resource_groups(location: str) -> List[str]:
    groups = list_resource_groups(location)
    if groups == []:
        log.warning("No Resource Groups found in Location '%s'", location)
    return groups


def cli_ask(prompt: str) -> str:
    """Ask user for information and return the answer"""

    answer = input(prompt).strip()  # strip to remove possible whitespace characters inputted by user by mistake
    return answer


def cli_tell(msg: str = "") -> None:
    print(msg)


def try_load_profiles(file_path: str, loader: Callable) -> Optional[List[AzureProfile]]:
    """
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    Return None on file reading error/parsing error
    """

    if not os.path.exists(file_path):
        log.info("File '%s' doesn't exist. Returning empty profile list", file_path)
        return []

    try:
        return loader(file_path)
    except RuntimeError:
        log.exception("Failed to load profiles file '%s'", file_path)
        return None
    except ValueError:
        log.exception("Missing fields in profiles. Please run again with '--complete' option")
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
        return None

    if not add_read_write_all_permissions(principal.id):
        return None

    if not grant_permissions(principal.id):
        return None

    if not consent_permissions(principal.id):
        return None

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

    if not location:
        log.warning("Location not specified, returning empty Resource Group list")
        return []

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


def profile_exists(profile_name: str, profiles: List[AzureProfile]) -> bool:
    return find_profile(profile_name, profiles) is not None


def find_profile(profile_name: str, profiles: List[AzureProfile]) -> Optional[int]:
    for i, profile in enumerate(profiles):
        if profile.name == profile_name:
            return i
    return None


def find_secret(principal_id: str, profiles: List[AzureProfile]) -> Optional[str]:
    for profile in profiles:
        if profile.principal_id == principal_id and profile.principal_secret != "":
            if likely_valid_service_principal_secret(profile.principal_secret):
                log.info("Secret for Service Principal ID '%s' found in profile '%s'", principal_id, profile.name)
                return profile.principal_secret
            log.warning(
                "Secret for Service Principal ID '%s' in profile '%s' is set, but has incorrect format",
                principal_id,
                profile.name,
            )
    log.warning("Secret for Service Principal ID '%s' not found", principal_id)
    return None


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

    backup_time = datetime.today().strftime("%Y-%m-%d_%H%M%S")
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


def format_columns(items: List[Any], num_columns: int) -> str:
    num_items = len(items)
    if num_items == 0:
        return "[no items]"

    # restrict num_columns to range [1..num_items]
    num_columns = min(num_items, max(1, num_columns))

    # prepare numbered items like: "11. norway"
    numbered_items = [format_item(i, num_items, item) for i, item in enumerate(items)]

    # prepare table rows
    num_rows = math.ceil(num_items / num_columns)
    rows: List[List[str]] = []
    for i in range(num_rows):
        row = numbered_items[i::num_rows]

        # append remaining columns
        while len(row) < num_columns:
            row.append("")
        rows.append(row)

    table = Texttable()
    table.set_deco(0)  # no table borders
    table.add_rows(rows, header=False)
    return table.draw()


def format_item(item_no: int, max_no: int, item: Any) -> str:
    """
    format numbered item nicely, eg.:
    8.  Pear
    9.  Apple
    10. Banana
    11. Pineapple
    """

    max_digits = int(math.log10(max_no)) + 1  # how many digits to represent the number in decimal system
    justified_item_no = f"{item_no}.".ljust(max_digits + 1)
    return f"{justified_item_no} {item}"


def parse_cmd_line() -> Tuple[str, bool, bool, List[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=DEFAULT_PROFILES_FILE_NAME, help="Profiles file name")
    parser.add_argument("--profiles", nargs="+", default=[], help="Names of profiles to create")
    parser.add_argument("--verbose", default=False, action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--complete", default=False, action="store_true", help="Only complete information in existing profiles"
    )
    args = parser.parse_args()
    return (args.filename, args.verbose, args.complete, args.profiles)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=level)


def profile_name_source() -> Iterator[str]:
    while True:
        yield cli_ask_profile_name()


if __name__ == "__main__":
    profiles_file_name, verbose_logging, complete_only, profile_names = parse_cmd_line()
    setup_logging(verbose_logging)
    if complete_only:
        execution_successful = complete_existing_profiles(profiles_file_name)
    else:
        execution_successful = add_new_profiles(profiles_file_name, profile_names or profile_name_source())
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
