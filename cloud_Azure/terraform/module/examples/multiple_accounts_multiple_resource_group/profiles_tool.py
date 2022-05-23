import argparse
import logging
import math
import os
import shutil
import sys
from datetime import datetime
from enum import Enum
from getpass import getpass
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, List, Optional, Tuple

from texttable import Texttable

from azure_client import AzureClient, AzureClientError, LoginCredentials, ServicePrincipal
from profiles import (
    AzureProfile,
    ProfileConfigurationError,
    has_complete_authentication_data,
    list_missing_required_fields,
    load_incomplete_profiles,
    save_profiles,
    validate_profile_configuration,
)

log = logging.getLogger(__name__)

EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit code for failed command

BACKUP_PROFILES_DIRECTORY = "backup_profiles"
DEFAULT_PROFILES_FILE_NAME: str = "profiles.ini"

APP_REGISTRATION_NAME: str = "KentikTerraformOnboarder"  # AppRegistration to be created


class Action(str, Enum):
    """Action for the tool to perform"""

    ADD = "add"
    COMPLETE = "complete"
    VALIDATE = "validate"


def add_new_profiles(file_path: str, names: Iterable[str]) -> bool:
    """
    Add new profiles for all provided names, in interactive manner
    User can break the process at any point by sending keyboard interrupt
    """

    profiles = try_load_profiles(file_path, load_incomplete_profiles)
    if profiles is None:
        return False

    cli_tell("[CTRL + D or CTRL + C] to finish")
    all_successful = True
    try:
        for name in names:
            successful = add_profile(name, profiles)
            all_successful = all_successful and successful
            cli_tell()
    except (EOFError, KeyboardInterrupt):
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

    try:
        # login to Azure account
        client = AzureClient.login_user(cli_ask_tenant_id(), cli_ask_subscription_id())

        # find existing or create new Service Principal
        principal = cli_get_or_create_service_principal(client, profiles)
        if principal is None:
            return False

        # request Azure location and list Resource Groups in that location
        location = cli_ask_azure_location(client)
        resource_group_names = cli_ask_resource_groups(client, location)

        # update profile list with a new item
        profile = AzureProfile(
            name=profile_name,
            subscription_id=client.subscription_id,
            tenant_id=client.tenant_id,
            principal_id=principal.app_id,
            principal_secret=principal.secret,
            location=location,
            resource_group_names=resource_group_names,
            storage_account_names=[],
        )
        insert_or_overwrite_profile(profiles, profile)

        cli_tell(f"Profile '{profile_name}' ready")
        return True
    except AzureClientError:
        log.exception("Failed to add profile '%s'", profile_name)
        return False


def complete_existing_profiles(file_path: str) -> bool:
    """
    Complete missing information in profiles loaded from provided file_path
    User can break the process at any point by sending keyboard interrupt
    """

    profiles = try_load_profiles(file_path, load_incomplete_profiles)
    if profiles is None:
        return False

    if not profiles:
        cli_tell(f"No profiles were loaded from '{file_path}'")
        return True

    cli_tell("[CTRL + D or CTRL + C] to finish")
    all_successful = True
    try:
        for profile in profiles:
            successful = complete_profile(profile, profiles)
            all_successful = all_successful and successful
            cli_tell()
    except (EOFError, KeyboardInterrupt):
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

    try:
        # filling any information other than just principal_secret requires logging into Azure Account
        # login to Azure account
        if has_complete_authentication_data(profile):
            cred = profile_to_credentials(profile)
            client = AzureClient.login_application(cred)
        else:
            tenant_id = profile.tenant_id or cli_ask_tenant_id()
            subscription_id = profile.subscription_id or cli_ask_subscription_id()
            client = AzureClient.login_user(tenant_id, subscription_id)

        profile.tenant_id = client.tenant_id
        profile.subscription_id = client.subscription_id

        # fill service principal information
        if profile.principal_id == "":
            principal = cli_get_or_create_service_principal(client, profiles)
            if principal is None:
                return False
            profile.principal_id = principal.app_id
            profile.principal_secret = principal.secret
        elif profile.principal_secret == "":
            profile.principal_secret = find_secret(profile.principal_id, profiles) or cli_ask_secret()

        # fill azure location information
        if profile.location == "":
            profile.location = cli_ask_azure_location(client)
            if list_invalid_resource_groups(client, profile):
                profile.resource_group_names = []

        # fill resource groups information
        if not profile.resource_group_names:
            profile.resource_group_names = cli_ask_resource_groups(client, profile.location)

        cli_tell(f"Profile '{profile.name}' information completed: {missing_fields_str}")
        return True
    except AzureClientError:
        log.exception("Failed to complete profile '%s'", profile.name)
        return False


def validate_profiles(file_path: str) -> bool:
    """
    Validate profiles by checking information against Azure API
    """

    cli_tell(f"Validating '{file_path}'")
    profiles = try_load_profiles(file_path, load_incomplete_profiles)
    all_valid = True
    for profile in profiles:
        valid = validate_profile(profile)
        all_valid = all_valid and valid
        cli_tell()

    status = "All profiles are valid" if all_valid else "Invalid profiles found"
    cli_tell(f"Finished validating profiles. {status}")

    return all_valid


def validate_profile(profile: AzureProfile) -> bool:
    """
    Check the information in profile against Azure
    """

    is_valid = True
    cli_tell(f"Profile name: {profile.name}")

    try:
        # check invariants
        validate_profile_configuration(profile)

        # check if provided credentials allow to login to Azure
        cred = profile_to_credentials(profile)
        client = AzureClient.login_application(cred)

        # check if location is valid
        available_locations = client.list_locations()
        if profile.location not in available_locations:
            cli_tell(f"The location is invalid in Azure: '{profile.location}'")
            is_valid = False
        else:
            # check if resource groups exist in location
            invalid_groups = list_invalid_resource_groups(client, profile)
            if invalid_groups:
                invalid_groups_str = ", ".join(invalid_groups)
                cli_tell(f"Resource Groups do not exist in Location '{profile.location}': '{invalid_groups_str}'")
                is_valid = False

    except (ProfileConfigurationError, AzureClientError) as err:
        cli_tell("Validation failed: " + str(err))
        is_valid = False

    cli_tell("Profile is valid" if is_valid else "Profile is invalid")
    return is_valid


def profile_to_credentials(profile: AzureProfile) -> LoginCredentials:
    return LoginCredentials(
        tenant_id=profile.tenant_id,
        subscription_id=profile.subscription_id,
        principal=ServicePrincipal(app_id=profile.principal_id, secret=profile.principal_secret),
    )


def list_invalid_resource_groups(client: AzureClient, p: AzureProfile) -> List[str]:
    if not p.resource_group_names:
        return []
    available_resource_groups = client.list_resource_groups(p.location)
    return list(set(p.resource_group_names) - set(available_resource_groups))


def cli_get_or_create_service_principal(
    client: AzureClient, profiles: List[AzureProfile]
) -> Optional[ServicePrincipal]:

    # try get existing AppRegistration
    app_ids = client.find_app_registrations(APP_REGISTRATION_NAME)
    app_count = len(app_ids)
    if app_count > 1:
        log.error("There are %d AppRegistrations named '%s'. 1 is allowed", app_count, APP_REGISTRATION_NAME)
        return None
    if app_count == 1:
        app_id = app_ids[0]
        log.debug("Found AppRegistration ID '%s' for '%s'", app_id, APP_REGISTRATION_NAME)
        principal_secret = find_secret(app_id, profiles) or cli_ask_secret()
        return ServicePrincipal(app_id=app_id, secret=principal_secret)

    # try create new AppRegistration
    return client.create_app_registration(APP_REGISTRATION_NAME).principal


def cli_ask_profile_name() -> str:
    while True:
        name = cli_ask("Enter new profile name: ")
        if name != "" and " " not in name and "\t" not in name:
            return name

        cli_tell("Name must not contain white space characters")


def cli_ask_tenant_id() -> str:
    while True:
        tenant_id = cli_ask("Enter Azure Tenant ID: ")
        if tenant_id != "" and " " not in tenant_id and "\t" not in tenant_id:
            return tenant_id
        cli_tell("ID must not contain white space characters")


def cli_ask_subscription_id() -> str:
    while True:
        subscription_id = cli_ask("Enter Azure Subscription ID [leave empty for auto-select]: ")
        if " " not in subscription_id and "\t" not in subscription_id:
            return subscription_id
        cli_tell("ID must not contain white space characters")


def cli_ask_overwrite_profile(profile_name: str) -> bool:
    answer = cli_ask(f"Profile '{profile_name}' already exists. Overwrite? [y/n]: ")
    return answer.lower() == "y"


def cli_ask_azure_location(client: AzureClient) -> str:
    NUM_COLUMNS_FOR_LOCATIONS_PRINTOUT = 3
    locations = client.list_locations()
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
        if valid_number(s, numbers_range):
            return int(s)


def cli_ask_numbers_in_range(numbers_range: int) -> List[int]:
    def valid(s: str) -> bool:
        return valid_number(s, numbers_range)

    while True:
        s = cli_ask(f"Enter comma-separated numbers in range [{0} - {numbers_range-1}]: ")
        numbers = [n.strip() for n in s.split(",")] if s else []
        if all(map(valid, numbers)):
            return list(map(int, numbers))


def valid_number(s: str, numbers_range: int) -> bool:
    if not s.isdigit():
        cli_tell(f"Invalid number '{s}'")
        return False
    number = int(s)
    if number not in range(numbers_range):
        cli_tell(f"Number '{number}' out of range")
        return False
    return True


def cli_ask_secret() -> str:
    return getpass("Enter Service Principal secret [empty to skip]: ")


def cli_ask_resource_groups(client: AzureClient, location: str) -> List[str]:
    NUM_COLUMNS = 3
    groups = client.list_resource_groups(location)
    num_groups = len(groups)
    if num_groups == 0:
        log.warning("No Resource Groups found in Location '%s', skipping resource groups selection", location)
        return []

    cli_tell("Select Resource Groups. Available: ")
    cli_tell(format_columns(groups, NUM_COLUMNS))
    selected_indexes = cli_ask_numbers_in_range(num_groups)
    return [groups[i] for i in selected_indexes]


def cli_ask(prompt: str) -> str:
    """Ask user for information and return the answer"""

    answer = input(prompt).strip()  # strip to remove possible whitespace characters inputted by user by mistake
    return answer


def cli_tell(msg: str = "") -> None:
    print(msg)


def try_load_profiles(file_path: str, loader: Callable) -> List[AzureProfile]:
    """
    Return profile list on success
    Return empty list if file_path doesn't exist or file contains no profiles
    """

    if not os.path.exists(file_path):
        log.debug("File '%s' doesn't exist. Returning empty profile list", file_path)
        return []

    return loader(file_path)


def profile_exists(profile_name: str, profiles: List[AzureProfile]) -> bool:
    return find_profile(profile_name, profiles) is not None


def find_profile(profile_name: str, profiles: List[AzureProfile]) -> Optional[int]:
    for i, profile in enumerate(profiles):
        if profile.name == profile_name:
            return i
    return None


def find_secret(app_id: str, profiles: List[AzureProfile]) -> Optional[str]:
    for profile in profiles:
        if profile.principal_id == app_id and profile.principal_secret != "":
            log.info("Secret for AppRegistration ID '%s' found in profile '%s'", app_id, profile.name)
            return profile.principal_secret
    log.warning("Secret for AppRegistration ID '%s' not found", app_id)
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


def parse_cmd_line() -> Tuple[str, bool, Action, List[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default=DEFAULT_PROFILES_FILE_NAME, help="Profiles file name")
    parser.add_argument("--profiles", nargs="+", default=[], help="Names of profiles to create")
    parser.add_argument("--verbose", default=False, action="store_true", help="Enable verbose logging")
    parser.add_argument("action", choices=[Action.ADD.value, Action.COMPLETE.value, Action.VALIDATE.value])
    args = parser.parse_args()
    return (args.filename, args.verbose, Action(args.action), args.profiles)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=level)


def profile_name_source() -> Iterator[str]:
    while True:
        yield cli_ask_profile_name()


if __name__ == "__main__":
    profiles_file_name, verbose_logging, action, profile_names = parse_cmd_line()
    setup_logging(verbose_logging)
    if action == Action.ADD:
        execution_successful = add_new_profiles(profiles_file_name, profile_names or profile_name_source())
    elif action == Action.COMPLETE:
        execution_successful = complete_existing_profiles(profiles_file_name)
    elif action == Action.VALIDATE:
        execution_successful = validate_profiles(profiles_file_name)
    else:
        log.fatal("Unknown action: %s", action)
        execution_successful = False

    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
